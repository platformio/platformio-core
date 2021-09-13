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

import os

from platformio import exception


def get_test_names(config):
    test_dir = config.get_optional_dir("test")
    if not os.path.isdir(test_dir):
        raise exception.TestDirNotExists(test_dir)
    names = []
    for item in sorted(os.listdir(test_dir)):
        if os.path.isdir(os.path.join(test_dir, item)):
            names.append(item)
    if not names:
        names = ["*"]
    return names
