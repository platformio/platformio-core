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

VERSION = (6, 1, "17b2")
__version__ = ".".join([str(s) for s in VERSION])

__title__ = "platformio"
__description__ = (
    "Your Gateway to Embedded Software Development Excellence. "
    "Unlock the true potential of embedded software development "
    "with PlatformIO's collaborative ecosystem, embracing "
    "declarative principles, test-driven methodologies, and "
    "modern toolchains for unrivaled success."
)
__url__ = "https://platformio.org"

__author__ = "PlatformIO Labs"
__email__ = "contact@piolabs.com"

__license__ = "Apache Software License"
__copyright__ = "Copyright 2014-present PlatformIO Labs"

__accounts_api__ = "https://api.accounts.platformio.org"
__registry_mirror_hosts__ = [
    "registry.platformio.org",
    "registry.nm1.platformio.org",
]
__pioremote_endpoint__ = "ssl:host=remote.platformio.org:port=4413"

__check_internet_hosts__ = [
    "185.199.110.153",  # Github.com
    "88.198.170.159",  # platformio.org
    "github.com",
] + __registry_mirror_hosts__
