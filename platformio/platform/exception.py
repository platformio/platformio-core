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

from platformio.exception import PlatformioException


class PlatformException(PlatformioException):
    pass


class UnknownPlatform(PlatformException):

    MESSAGE = "Unknown development platform '{0}'"


class IncompatiblePlatform(PlatformException):

    MESSAGE = (
        "Development platform '{0}' is not compatible with PlatformIO Core v{1} and "
        "depends on PlatformIO Core {2}.\n"
    )


class UnknownBoard(PlatformException):

    MESSAGE = "Unknown board ID '{0}'"


class InvalidBoardManifest(PlatformException):

    MESSAGE = "Invalid board JSON manifest '{0}'"


class UnknownFramework(PlatformException):

    MESSAGE = "Unknown framework '{0}'"


class BuildScriptNotFound(PlatformException):

    MESSAGE = "Invalid path '{0}' to build script"
