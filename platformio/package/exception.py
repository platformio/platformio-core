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

from platformio import util
from platformio.exception import PlatformioException, UserSideException


class PackageException(PlatformioException):
    pass


class ManifestException(PackageException):
    pass


class UnknownManifestError(ManifestException):
    pass


class ManifestParserError(ManifestException):
    pass


class ManifestValidationError(ManifestException):
    def __init__(self, messages, data, valid_data):
        super().__init__()
        self.messages = messages
        self.data = data
        self.valid_data = valid_data

    def __str__(self):
        return (
            "Invalid manifest fields: %s. \nPlease check specification -> "
            "https://docs.platformio.org/page/librarymanager/config.html"
            % self.messages
        )


class MissingPackageManifestError(ManifestException):

    MESSAGE = "Could not find one of '{0}' manifest files in the package"


class UnknownPackageError(UserSideException):

    MESSAGE = (
        "Could not find the package with '{0}' requirements for your system '%s'"
        % util.get_systype()
    )


class NotGlobalLibDir(UserSideException):

    MESSAGE = (
        "The `{0}` is not a PlatformIO project.\n\n"
        "To manage libraries in global storage `{1}`,\n"
        "please use `platformio lib --global {2}` or specify custom storage "
        "`platformio lib --storage-dir /path/to/storage/ {2}`.\n"
        "Check `platformio lib --help` for details."
    )
