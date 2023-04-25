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

from os import makedirs
from os.path import isdir, isfile, join

from platformio import fs
from platformio.project.helpers import compute_project_checksum, get_project_dir

KNOWN_CLEAN_TARGETS = ("clean",)
KNOWN_FULLCLEAN_TARGETS = ("cleanall", "fullclean")
KNOWN_ALLCLEAN_TARGETS = KNOWN_CLEAN_TARGETS + KNOWN_FULLCLEAN_TARGETS


def clean_build_dir(build_dir, config):
    # remove legacy ".pioenvs" folder
    legacy_build_dir = join(get_project_dir(), ".pioenvs")
    if isdir(legacy_build_dir) and legacy_build_dir != build_dir:
        fs.rmtree(legacy_build_dir)

    checksum_file = join(build_dir, "project.checksum")
    checksum = compute_project_checksum(config)

    if isdir(build_dir):
        # check project structure
        if isfile(checksum_file):
            with open(checksum_file, encoding="utf8") as fp:
                if fp.read() == checksum:
                    return
        fs.rmtree(build_dir)

    makedirs(build_dir)
    with open(checksum_file, mode="w", encoding="utf8") as fp:
        fp.write(checksum)
