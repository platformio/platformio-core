# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import chdir, getcwd, readlink, remove, symlink, walk
from os.path import exists, islink, join, relpath
from sys import exit as sys_exit


def fix_symlink(root, fname, brokenlink):
    print(root, fname, brokenlink)
    prevcwd = getcwd()

    chdir(root)
    remove(fname)
    symlink(relpath(brokenlink, root), fname)
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
