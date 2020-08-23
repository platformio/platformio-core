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

import re

import semantic_version


def cast_version_to_semver(value, force=True, raise_exception=False):
    assert value
    try:
        return semantic_version.Version(value)
    except ValueError:
        pass
    if force:
        try:
            return semantic_version.Version.coerce(value)
        except ValueError:
            pass
    if raise_exception:
        raise ValueError("Invalid SemVer version %s" % value)
    # parse commit hash
    if re.match(r"^[\da-f]+$", value, flags=re.I):
        return semantic_version.Version("0.0.0+sha." + value)
    return semantic_version.Version("0.0.0+" + value)


def pepver_to_semver(pepver):
    return cast_version_to_semver(
        re.sub(r"(\.\d+)\.?(dev|a|b|rc|post)", r"\1-\2.", pepver, 1)
    )


def get_original_version(version):
    if version.count(".") != 2:
        return None
    _, raw = version.split(".")[:2]
    if int(raw) <= 99:
        return None
    if int(raw) <= 9999:
        return "%s.%s" % (raw[:-2], int(raw[-2:]))
    return "%s.%s.%s" % (raw[:-4], int(raw[-4:-2]), int(raw[-2:]))
