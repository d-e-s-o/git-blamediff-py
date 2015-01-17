git-blamediff
=============


Purpose
-------

**git-blamediff** is a script aiding in annotating changes made in a ``git``
repository with the SHA1 hashes the respective lines in the base state were
modified in. This process allows for quick lookup of previous commits of
interest or creation of fix-up commits. Depending on your workflow the latter
might be massively helpful for sorting in changes to the proper previous
commits in a set of changes.


Usage
-----

Consider the following example where a developer noticed that he/she forgot a
trailing newline on a string to print. The code has not gotten pushed and so
fixing up the commit of interest is the best option. The patch looks as
follows:

```patch
 --- main.c
 +++ main.c
@@ -6,6 +6,6 @@ int main(int argc, char const* argv[])
     fprintf(stderr, "Too many arguments.\n");
     return -1;
   }
-  printf("Hello world!");
+  printf("Hello world!\n");
   return 0;
 }
```

There can potentially be a couple of changes being made in the repository. How
to find the commit that introduced the initial (faulty) line? Usually, one
would use ``git blame`` or ``git annotate`` and scan through the annotated diff
to find the line and with it the SHA1 hash of interest. Doing so one either has
to manually inspect the entire annotated file for the lines of interest or to
tediously figure out the lines in a file that were modified and craft and pass
in an -L argument to the blame/annotate invocation.

**git-blamediff** can be used to automated this process. It reads a patch such
as the one above and automatically invokes ``git`` on the respective lines to
print it in annotated form. For example:

```
$ git diff --relative --no-prefix | git blamediff
--- main.c
+++ main.c
8d4442c  6)     fprintf(stderr, "Too many arguments.\n");
8d4442c  7)     return -1;
8d4442c  8)   }
bd7ee05  9)   printf("Hello world!");
bd7ee05 10)   return 0;
bd7ee05 11) }
```

This example also illustrates two important properties a patch must have in
order to be annotated correctly: it should contain paths relative to the
current working directory (by using the ``--relative`` argument) and contain no
prefixes (i.e., instead of ``a/some-path/some-file`` just use
``some-path/some-file``; produced by providing the ``--no-prefix`` option to
``git``).

These requirements exist to keep the script concise and not have to deal with
too many special cases. Since under normal circumstances one would create an
alias shortening the ``git diff`` invocation shown before, this property is not
considered a restriction (see section ``Installation`` for an example of such
aliases).

Continuing the workflow, one could create a fixup commit and then, at some
point, perform an interactive rebase in order to automatically have the
original changes amended, e.g.:

```shell
$ git add --all
$ git commit --fixup bd7ee05
...
$ git rebase --interactive --autosquash bd7ee05^
```


Installation
------------

**git-blamediff** does not have any external dependencies. In order to
use it the containing package needs to be made known to Python, e.g., by
adding the path to the ``src/`` directory to the ``PYTHONPATH``
environment variable. Furthermore, the ``git-blamediff.py`` script
should be installed or linked as ``git-blamediff`` into a location
accessible via ``PATH``.

Due to the script's name, ``git`` will recognize the command as well, so it can
be invoked as ``git blamediff`` but also via ``git-blamediff``.

If you are using [Gentoo Linux](https://www.gentoo.org/), there is an
[ebuild](https://github.com/d-e-s-o/git-blamediff-ebuild) available that
can be used directly.

To simplify usage, a ``git`` alias should be introduced. Two aliases for
annotating the currently unstaged (``git bd`` -- *"git blame diff"*) and staged
(``git bds`` -- *"git blame diff staged"*) changes, respectively, could look
like this:

```git
[alias]
  bd = "!bd() { git diff --relative --no-prefix | git blamediff; }; bd"
  bds = "!bds() { git diff --relative --no-prefix --staged | git blamediff; }; bds"
```


Support
-------

The module is tested with Python 3. There is no work going on to
ensure compatibility with Python 2.
