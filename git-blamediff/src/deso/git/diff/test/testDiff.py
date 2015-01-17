# testDiff.py

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

"""Test diff parsing functionality."""

from deso.git.diff.diff import (
  DiffFile,
  Parser,
)
from textwrap import (
  dedent,
)
from unittest import (
  TestCase,
  main,
)


class TestParser(TestCase):
  """Tests for the diff parsing functionality."""
  def setUp(self):
    """Create a new Parser object ready to use."""
    self._parser = Parser()


  def testParseEmptyDiff(self):
    """Verify that we can handle an empty diff."""
    diff = ""
    self._parser.parse(diff.splitlines())


  def testParseSimpleDiff(self):
    """Test parsing of a very simple one-line-change diff."""
    diff = dedent("""\
      --- main.c
      +++ main.c
      @@ -6,6 +6,6 @@ int main(int argc, char const* argv[])
           fprintf(stderr, "Too many arguments.\\n");
           return -1;
         }
      -  printf("Hello world!");
      +  printf("Hello world!\\n");
         return 0;
       }\
    """)
    self._parser.parse(diff.splitlines())

    (src, dst), = self._parser.diffs
    self.assertEqual(src, DiffFile("main.c", add_sub="-", line=6, count=6))
    self.assertEqual(dst, DiffFile("main.c", add_sub="+", line=6, count=6))


if __name__ == "__main__":
  main()
