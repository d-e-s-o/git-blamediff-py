# diff.py

#/***************************************************************************
# *   Copyright (C) 2015-2016 Daniel Mueller (deso@posteo.net)              *
# *                                                                         *
# *   This program is free software: you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation, either version 3 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU General Public License for more details.                          *
# *                                                                         *
# *   You should have received a copy of the GNU General Public License     *
# *   along with this program.  If not, see <http://www.gnu.org/licenses/>. *
# ***************************************************************************/

"""A module for parsing diffs."""

from re import (
  compile as regex,
)
from collections import (
  namedtuple,
)


_NUM_STRING = r"[0-9]"
_NUMS_STRING = r"{nr}+".format(nr=_NUM_STRING)
_WS_STRING = r"[ \t]*"
_FILE_STRING = r"([^ \t]+)"
_ADDSUB_STRING = r"([+\-])"
_NUMLINE_STRING = r"({nr})".format(nr=_NUMS_STRING)
# Aside from '+' and '-' we have a "continuation" character ('\') in
# here which essentially just indicates a line that is being ignored.
# This character is used (in conjunction with the string "No newline at
# end of file") to indicate that a newline symbol at the end of a file
# is added or removed, for instance.
_DIFF_DIFF_REGEX = regex(r"^[+\-\\ ]")
_DIFF_NODIFF_REGEX = regex(r"^[^+\- ]")
_DIFF_SRC_REGEX = regex(r"^---{ws}{f}".format(ws=_WS_STRING, f=_FILE_STRING))
_DIFF_DST_REGEX = regex(r"^\+\+\+{ws}{f}".format(ws=_WS_STRING, f=_FILE_STRING))
# Note that in case a new file containing a single line is added the
# diff header might not contain the second count.
_DIFF_HEAD_LINE = r"^@@ {a}{nl}(?:,{nl})? {a}{nl}(?:,{nl})? @@"
_DIFF_HEAD_REGEX = regex(_DIFF_HEAD_LINE.format(a=_ADDSUB_STRING,
                                                nl=_NUMLINE_STRING))


DiffFile = namedtuple("DiffFile", ["file", "add_sub", "line", "count"])


class State:
  """A class representing the states our parser can be in."""
  def __init__(self, parser, parse_functions, **kwargs):
    """Create a new parser state.

      A state is always associated with a parser. It interacts with the
      latter in order to extract information out of a diff. A state
      contains a list of parsing functions that are invoked in the order
      in which they are given so as to try to parse a line of a diff.
      Additional arguments can be passed in that will be accessible as
      properties of the state.
    """
    self._parser = parser
    self._parse_functions = parse_functions
    self._args = kwargs


  def __getattr__(self, attribute):
    """Forward attribute requests to the arguments passed during construction."""
    return self._args[attribute]


  def parse(self, line):
    """Parse a line of input."""
    # Invoke all functions in the order they were supplied. The first
    # one matches "wins". If none matches raise an error.
    for function in self._parse_functions:
      if function(self, line):
        return

    raise RuntimeError("Unexpected line: \"%s\"" % line)


  @property
  def parser(self):
    """Retrieve the state's associated parser."""
    return self._parser


def parseSrc(state, line):
  """Try parsing a line containing the source file."""
  m = _DIFF_SRC_REGEX.match(line)
  if m is not None:
    src, = m.groups()
    state.parser.advance(srcState(state.parser, src))
    return True
  else:
    return False


def parseDst(state, line):
  """Try parsing a line containing the destination file."""
  m = _DIFF_DST_REGEX.match(line)
  if m is not None:
    dst, = m.groups()
    state.parser.advance(dstState(state.parser, state.src, dst))
    return True
  else:
    return False


def parseHead(state, line):
  """Try parsing a line containg information about the changed lines."""
  m = _DIFF_HEAD_REGEX.match(line)
  if m is not None:
    # Because a diff header might not contain counts if only a single
    # line is affected, we supply the default "1" to the groups method.
    add_src, start_src, count_src,\
    add_dst, start_dst, count_dst = m.groups(default="1")

    src = DiffFile(state.src, add_src, int(start_src), int(count_src))
    dst = DiffFile(state.dst, add_dst, int(start_dst), int(count_dst))
    header = headerState(state.parser, state.src, state.dst)
    state.parser.advance(header)
    diff = (src, dst)
    state.parser.addDiff(diff)
    return True
  else:
    return False


def matchNoDiff(state, line):
  """Try matching a line that contains no actual diff."""
  return _DIFF_NODIFF_REGEX.match(line) is not None


def matchDiff(state, line):
  """Try matching an actual diff line."""
  return _DIFF_DIFF_REGEX.match(line) is not None


def restart(state, line):
  """Try matching a line not from an actual diff that indicates the start of a new file."""
  if _DIFF_NODIFF_REGEX.match(line):
    state.parser.advance(startState(state.parser))
    return True
  else:
    return False


def startState(parser):
  """Retrieve the state to enter when we expect a new file to start."""
  return State(parser, [parseSrc, matchNoDiff])


def srcState(parser, src):
  """Retrieve the state to enter after we parsed the source file header part."""
  return State(parser, [parseDst], src=src)


def dstState(parser, src, dst):
  """Retrieve the state to enter after we parsed the destination file header part."""
  return State(parser, [parseHead], src=src, dst=dst)


def headerState(parser, src, dst):
  """Retrieve the state to enter after we parsed the entire header."""
  return State(parser, [matchDiff, parseHead, restart], src=src, dst=dst)


class Parser:
  """The parser class interpretes a diff and extracts relevant information."""
  def __init__(self):
    """Create a new Parser object ready for diff parsing."""
    self._state = startState(self)
    self._diffs = []


  def parse(self, lines):
    """Parse the given diff and extract the relevant information."""
    for line in lines:
      # We simply ignore any empty lines and do not even hand them into
      # the state for further consideration because they cannot change
      # anything.
      if len(line) > 0:
        # Remove trailing new line symbols, we already expect lines.
        self._state.parse(line[:-1] if line[-1] == "\n" else line)


  def advance(self, state):
    """Advance the parsers state."""
    self._state = state


  def addDiff(self, diff):
    """Add a found diff to the list of all diffs."""
    self._diffs.append(diff)


  @property
  def diffs(self):
    """Retrieve all found diffs."""
    return self._diffs
