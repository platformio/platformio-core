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


class PlatformioException(Exception):

    MESSAGE = None

    def __str__(self):  # pragma: no cover
        if self.MESSAGE:
            return self.MESSAGE.format(*self.args)
        else:
            return Exception.__str__(self)


class ReturnErrorCode(PlatformioException):
    pass


class MinitermException(PlatformioException):
    pass


class AbortedByUser(PlatformioException):

    MESSAGE = "Aborted by user"


class UnknownPlatform(PlatformioException):

    MESSAGE = "Unknown platform '{0}'"


class PlatformNotInstalledYet(PlatformioException):

    MESSAGE = "The platform '{0}' has not been installed yet. "\
        "Use `platformio platforms install {0}` command"


class BoardNotDefined(PlatformioException):

    MESSAGE = "You need to specify board type using `-b` or `--board` "\
        "option. Supported boards list is available via "\
        " `platformio boards` command"


class UnknownBoard(PlatformioException):

    MESSAGE = "Unknown board type '{0}'"


class UnknownFramework(PlatformioException):

    MESSAGE = "Unknown framework '{0}'"


class UnknownPackage(PlatformioException):

    MESSAGE = "Detected unknown package '{0}'"


class InvalidPackageVersion(PlatformioException):

    MESSAGE = "The package '{0}' with version '{1:d}' does not exist"


class NonSystemPackage(PlatformioException):

    MESSAGE = "The package '{0}' is not available for your system '{1}'"


class FDUnrecognizedStatusCode(PlatformioException):

    MESSAGE = "Got an unrecognized status code '{0}' when downloaded {1}"


class FDSizeMismatch(PlatformioException):

    MESSAGE = "The size ({0:d} bytes) of downloaded file '{1}' "\
        "is not equal to remote size ({2:d} bytes)"


class FDSHASumMismatch(PlatformioException):

    MESSAGE = "The 'sha1' sum '{0}' of downloaded file '{1}' "\
        "is not equal to remote '{2}'"


class NotPlatformProject(PlatformioException):

    MESSAGE = "Not a PlatformIO project. `platformio.ini` file has not been "\
        "found in current working directory ({0}). To initialize new project "\
        "please use `platformio init` command"


class UndefinedEnvPlatform(PlatformioException):

    MESSAGE = "Please specify platform for '{0}' environment"


class UnsupportedArchiveType(PlatformioException):

    MESSAGE = "Can not unpack file '{0}'"


class ProjectEnvsNotAvailable(PlatformioException):

    MESSAGE = "Please setup environments in `platformio.ini` file"


class InvalidEnvName(PlatformioException):

    MESSAGE = "Invalid environment '{0}'. The name must start with 'env:'"


class UnknownEnvNames(PlatformioException):

    MESSAGE = "Unknown environment names '{0}'. Valid names are '{1}'"


class GetSerialPortsError(PlatformioException):

    MESSAGE = "No implementation for your platform ('{0}') available"


class GetLatestVersionError(PlatformioException):

    MESSAGE = "Can not retrieve the latest PlatformIO version"


class APIRequestError(PlatformioException):

    MESSAGE = "[API] {0}"


class LibAlreadyInstalled(PlatformioException):
    pass


class LibNotInstalled(PlatformioException):

    MESSAGE = "Library #{0:d} has not been installed yet"


class LibInstallDependencyError(PlatformioException):

    MESSAGE = "Error has been occurred for library dependency '{0}'"


class InvalidLibConfURL(PlatformioException):

    MESSAGE = "Invalid library config URL '{0}'"


class BuildScriptNotFound(PlatformioException):

    MESSAGE = "Invalid path '{0}' to build script"


class InvalidSettingName(PlatformioException):

    MESSAGE = "Invalid setting with the name '{0}'"


class InvalidSettingValue(PlatformioException):

    MESSAGE = "Invalid value '{0}' for the setting '{1}'"


class CIBuildEnvsEmpty(PlatformioException):

    MESSAGE = "Can't find PlatformIO build environments.\n"\
        "Please specify `--board` or path to `platformio.ini` with "\
        "predefined environments using `--project-conf` option"


class UpgradeError(PlatformioException):

    MESSAGE = """{0}

* Upgrade using `pip install -U platformio`
* Try different installation/upgrading steps:
  http://docs.platformio.org/en/latest/installation.html
"""


class CygwinEnvDetected(PlatformioException):

    MESSAGE = "PlatformIO does not work within Cygwin environment. "\
        "Use native Terminal instead."
