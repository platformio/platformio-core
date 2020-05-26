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


class PackageSpec(object):
    def __init__(self, raw=None, organization=None, name=None, version=None):
        if raw is not None:
            organization, name, version = self.parse(raw)

        self.organization = organization
        self.name = name
        self.version = version

    @staticmethod
    def parse(raw):
        organization = None
        name = None
        version = None
        raw = raw.strip()
        if raw.startswith("@") and "/" in raw:
            tokens = raw[1:].split("/", 1)
            organization = tokens[0].strip()
            raw = tokens[1]
        if "@" in raw:
            name, version = raw.split("@", 1)
            name = name.strip()
            version = version.strip()
        else:
            name = raw.strip()

        return organization, name, version
