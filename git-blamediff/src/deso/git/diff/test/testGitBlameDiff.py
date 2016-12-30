# testGitBlameDiff.py

#/***************************************************************************
# *   Copyright (C) 2016 Daniel Mueller (deso@posteo.net)                   *
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

"""End-to-end tests for git-blamediff."""

from deso.execute import (
  findCommand,
  pipeline,
)
from deso.git.repo import (
  PythonMixin,
  Repository,
  write,
)
from os.path import (
  dirname,
  join,
)
from sys import (
  executable,
)
from textwrap import (
  dedent,
)
from unittest import (
  TestCase,
  main,
)


GIT = findCommand("git")
GIT_SHA1_DIGITS = 8


class GitRepository(Repository):
  """A git repository with the copyright hook installed."""
  def __init__(self):
    """Initialize the parent portion of the object."""
    super().__init__(GIT)


  def _init(self):
    """Initialize the repository."""
    super()._init()
    # For some reason the actual number of digits reported is always one
    # higher than our setting here.
    self.config("core", "abbrev", GIT_SHA1_DIGITS - 1)


  @Repository.autoChangeDir
  def blamediff(self):
    """Invoke git-blamediff on the repository."""
    script = join(dirname(__file__), "..", "git-blamediff.py")

    env = {}
    PythonMixin.inheritEnv(env)
    out, _ = pipeline([
        [GIT, "diff", "--relative", "--no-prefix"],
        [executable, script],
      ],
      env=env, stdout=b"",
    )
    return out


class TestGitBlameDiff(TestCase):
  """Test cases for git-blamediff."""
  def testBlameSingleFileSingleLine(self):
    """Check that git-blamediff works on a single file with a single line."""
    with GitRepository() as repo:
      repo.commit("--allow-empty")

      write(repo, "main.py", data="# main.py")
      repo.add("main.py")
      repo.commit()

      write(repo, "main.py", data="# main.py\n# Hello, World!")
      sha1, _ = repo.revParse("--short=%d" % GIT_SHA1_DIGITS, "HEAD", stdout=b"")
      out = repo.blamediff()

      expected = dedent("""\
        --- main.py
        +++ main.py
        %s 1) # main.py
      """ % sha1[:-1].decode())

      self.assertEqual(out.decode(), expected)


if __name__ == "__main__":
  main()
