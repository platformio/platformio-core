# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import chdir, getcwd, readlink, remove, symlink, walk
from os.path import exists, islink, join, split
from sys import exit as sys_exit


def get_symrelpath(root, sympath, ending=None):
    head, tail = split(sympath)

    if ending:
        ending = join(tail, ending)
        relpath = join("..", ending)
    else:
        relpath = tail
        ending = tail

    if exists(join(root, relpath)):
        return relpath
    elif head:
        return get_symrelpath(root, head, ending)
    else:
        raise Exception()


def fix_symlink(root, fname, brokenlink):
    prevcwd = getcwd()
    symrelpath = get_symrelpath(root, brokenlink)

    chdir(root)
    remove(fname)
    symlink(symrelpath, fname)
    chdir(prevcwd)


def main():
    for root, dirnames, filenames in walk("."):
        for f in filenames:
            path = join(root, f)
            if not islink(path) or exists(path):
                continue
            fix_symlink(root, f, readlink(path))


if __name__ == "__main__":
    sys_exit(main())
