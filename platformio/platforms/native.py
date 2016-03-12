# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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

from platformio.platforms.base import BasePlatform


class NativePlatform(BasePlatform):

    """
    Native development platform is intended to be used for desktop OS.
    This platform uses built-in toolchains (preferable based on GCC),
    frameworks, libs from particular OS where it will be run.

    http://platformio.org/platforms/native
    """

    PACKAGES = {
    }
