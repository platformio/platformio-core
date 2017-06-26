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


class PlatformioException(Exception):

    MESSAGE = None

    def __str__(self):  # pragma: no cover
        if self.MESSAGE:
            return self.MESSAGE.format(*self.args)
        return Exception.__str__(self)


class ReturnErrorCode(PlatformioException):

    MESSAGE = "{0}"


class MinitermException(PlatformioException):
    pass


class AbortedByUser(PlatformioException):

    MESSAGE = "Aborted by user"


class UnknownPlatform(PlatformioException):

    MESSAGE = "Unknown development platform '{0}'"


class IncompatiblePlatform(PlatformioException):

    MESSAGE = "Development platform '{0}' is not compatible with PIO Core v{1}"


class PlatformNotInstalledYet(PlatformioException):

    MESSAGE = "The platform '{0}' has not been installed yet. "\
        "Use `platformio platform install {0}` command"


class BoardNotDefined(PlatformioException):

    MESSAGE = "You need to specify board ID using `-b` or `--board` "\
        "option. Supported boards list is available via "\
        "`platformio boards` command"


class UnknownBoard(PlatformioException):

    MESSAGE = "Unknown board ID '{0}'"


class InvalidBoardManifest(PlatformioException):

    MESSAGE = "Invalid board JSON manifest '{0}'"


class UnknownFramework(PlatformioException):

    MESSAGE = "Unknown framework '{0}'"


class UnknownPackage(PlatformioException):

    MESSAGE = "Detected unknown package '{0}'"


class MissingPackageManifest(PlatformioException):

    MESSAGE = "Could not find one of '{0}' manifest files in the package"


class UndefinedPackageVersion(PlatformioException):

    MESSAGE = "Could not find a version that satisfies the requirement '{0}'"\
              " for your system '{1}'"


class PackageInstallError(PlatformioException):

    MESSAGE = "Could not install '{0}' with version requirements '{1}' "\
              "for your system '{2}'.\n"\
              "If you use Antivirus, it can block PlatformIO Package "\
              "Manager. Try to disable it for a while."


class FDUnrecognizedStatusCode(PlatformioException):

    MESSAGE = "Got an unrecognized status code '{0}' when downloaded {1}"


class FDSizeMismatch(PlatformioException):

    MESSAGE = "The size ({0:d} bytes) of downloaded file '{1}' "\
        "is not equal to remote size ({2:d} bytes)"


class FDSHASumMismatch(PlatformioException):

    MESSAGE = "The 'sha1' sum '{0}' of downloaded file '{1}' "\
        "is not equal to remote '{2}'"


class NotPlatformIOProject(PlatformioException):

    MESSAGE = "Not a PlatformIO project. `platformio.ini` file has not been "\
        "found in current working directory ({0}). To initialize new project "\
        "please use `platformio init` command"


class UndefinedEnvPlatform(PlatformioException):

    MESSAGE = "Please specify platform for '{0}' environment"


class UnsupportedArchiveType(PlatformioException):

    MESSAGE = "Can not unpack file '{0}'"


class ProjectEnvsNotAvailable(PlatformioException):

    MESSAGE = "Please setup environments in `platformio.ini` file"


class UnknownEnvNames(PlatformioException):

    MESSAGE = "Unknown environment names '{0}'. Valid names are '{1}'"


class GetSerialPortsError(PlatformioException):

    MESSAGE = "No implementation for your platform ('{0}') available"


class GetLatestVersionError(PlatformioException):

    MESSAGE = "Can not retrieve the latest PlatformIO version"


class APIRequestError(PlatformioException):

    MESSAGE = "[API] {0}"


class InternetIsOffline(PlatformioException):

    MESSAGE = "You are not connected to the Internet"


class LibNotFound(PlatformioException):

    MESSAGE = "Library `{0}` has not been found in PlatformIO Registry.\n"\
              "You can ignore this message, if `{0}` is a built-in library "\
              "(included in framework, SDK). E.g., SPI, Wire, etc."


class NotGlobalLibDir(PlatformioException):

    MESSAGE = "The `{0}` is not a PlatformIO project.\n\n"\
              "To manage libraries "\
              "in global storage `{1}`,\n"\
              "please use `platformio lib --global {2}` or specify custom "\
              "storage `platformio lib --storage-dir /path/to/storage/ {2}`."\
              "\nCheck `platformio lib --help` for details."


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
  http://docs.platformio.org/page/installation.html
"""


class CygwinEnvDetected(PlatformioException):

    MESSAGE = "PlatformIO does not work within Cygwin environment. "\
        "Use native Terminal instead."
