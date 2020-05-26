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

from platformio.package.spec import PackageSpec


def test_parser():
    inputs = [
        ("foo", (None, "foo", None)),
        ("@org/foo", ("org", "foo", None)),
        ("@org/foo @ 1.2.3", ("org", "foo", "1.2.3")),
        ("bar @ 1.2.3", (None, "bar", "1.2.3")),
        ("cat@^1.2", (None, "cat", "^1.2")),
    ]
    for raw, result in inputs:
        assert PackageSpec.parse(raw) == result
