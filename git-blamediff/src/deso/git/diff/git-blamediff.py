#!/usr/bin/env python

#/***************************************************************************
# *   Copyright (C) 2015 Daniel Mueller (deso@posteo.net)                   *
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

"""A script to annotate the lines of a git diff directly."""

from deso.git.diff import (
  Parser,
)
from subprocess import (
  call,
)
from sys import (
  stdin,
  stdout,
)


def blame(diffs):
  """Invoke git to annotate all the diff hunks."""
  for diff in diffs:
    # Start off by printing some information on the file we are
    # currently annotating.
    # TODO: We should print the file header only once.
    src, dst = diff
    print("--- %s" % src.file)
    print("+++ %s" % dst.file)
    # Make sure stdout is flushed properly before invoking a git command
    # to be sure our 'print' output arrives before that of git.
    stdout.flush()

    # Invoke git with the appropriate options to annotate the lines of
    # the diff.
    # TODO: Make the arguments here more configurable. In fact, we
    #       should not hard-code any of them here.
    cmd = "/usr/bin/git --no-pager blame -s -L{l},+{c} {f} HEAD"
    cmd = cmd.format(l=src.line, c=src.count, f=src.file)

    call(cmd.split())


def main():
  """Parse the diff from stdin and invoke git blame on each hunk."""
  parser = Parser()
  parser.parse(stdin.readlines())

  blame(parser.diffs)
  return 0


if __name__ == "__main__":
  exit(main())
