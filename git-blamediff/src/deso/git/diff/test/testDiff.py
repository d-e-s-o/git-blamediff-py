# testDiff.py

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


  def testParseDiffAddingNewlineAtEndOfFile(self):
    """Test that we can parse a diff emitted by git if a file's trailing newline is added."""
    diff = dedent("""\
      --- main.c
      +++ main.c
      @@ -8,4 +8,4 @@ int main(int argc, char const* argv[])
         }
         printf("Hello world!");
         return 0;
      -}
      \\ No newline at end of file
      +}\
    """)
    self._parser.parse(diff.splitlines())

    (src, dst), = self._parser.diffs
    self.assertEqual(src, DiffFile("main.c", add_sub="-", line=8, count=4))
    self.assertEqual(dst, DiffFile("main.c", add_sub="+", line=8, count=4))


  def testParseDiffRemovingNewlineAtEndOfFile(self):
    """Test that we can parse a diff emitted by git if a file's trailing newline is removed."""
    diff = dedent("""\
      --- main.c
      +++ main.c
      @@ -8,4 +8,4 @@ int main(int argc, char const* argv[])
         }
         printf("Hello world!");
         return 0;
      -}
      +}
      \\ No newline at end of file\
    """)
    self._parser.parse(diff.splitlines())

    (src, dst), = self._parser.diffs
    self.assertEqual(src, DiffFile("main.c", add_sub="-", line=8, count=4))
    self.assertEqual(dst, DiffFile("main.c", add_sub="+", line=8, count=4))


  def testParseDiffWithAddedFileWithSingleLine(self):
    """Test that we can parse a diff adding a file with a single line."""
    diff = dedent("""\
      --- /dev/null
      +++ main.c
      @@ -0,0 +1 @@
      +main.c\
    """)
    self._parser.parse(diff.splitlines())

    (src, dst), = self._parser.diffs
    self.assertEqual(src, DiffFile("/dev/null", add_sub="-", line=0, count=0))
    self.assertEqual(dst, DiffFile("main.c", add_sub="+", line=1, count=1))


  def testParseDiffWithRemovedFileWithSingleLine(self):
    """Test that we can parse a diff removing a file with a single line."""
    diff = dedent("""\
      --- main.c
      +++ /dev/null
      @@ -1 +0,0 @@
      -main.c\
    """)
    self._parser.parse(diff.splitlines())

    (src, dst), = self._parser.diffs
    self.assertEqual(src, DiffFile("main.c", add_sub="-", line=1, count=1))
    self.assertEqual(dst, DiffFile("/dev/null", add_sub="+", line=0, count=0))


  def testParseDiffWithEmptyLine(self):
    """Verify that we can parse a diff containing an empty line."""
    diff = dedent("""\
      --- main.c
      +++ main.c
      @@ -1,6 +1,6 @@
       #include <stdio.h>
       
      -int main(int argc, char const* argv[])
      +int main(int argc, char* argv[])
       {
         if (argc > 1) {
           fprintf(stderr, "Too many arguments.\\n");\
      """)
    self._parser.parse(diff.splitlines())

    (src, dst), = self._parser.diffs
    self.assertEqual(src, DiffFile("main.c", add_sub="-", line=1, count=6))
    self.assertEqual(dst, DiffFile("main.c", add_sub="+", line=1, count=6))


if __name__ == "__main__":
  main()
