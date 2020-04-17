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
            # pylint: disable=not-an-iterable
            return self.MESSAGE.format(*self.args)

        return super(PlatformioException, self).__str__()


class ReturnErrorCode(PlatformioException):

    MESSAGE = "{0}"


class LockFileTimeoutError(PlatformioException):
    pass


class MinitermException(PlatformioException):
    pass


class UserSideException(PlatformioException):
    pass


class AbortedByUser(UserSideException):

    MESSAGE = "Aborted by user"


#
# Development Platform
#


class UnknownPlatform(PlatformioException):

    MESSAGE = "Unknown development platform '{0}'"


class IncompatiblePlatform(PlatformioException):

    MESSAGE = "Development platform '{0}' is not compatible with PIO Core v{1}"


class PlatformNotInstalledYet(PlatformioException):

    MESSAGE = (
        "The platform '{0}' has not been installed yet. "
        "Use `platformio platform install {0}` command"
    )


class UnknownBoard(PlatformioException):

    MESSAGE = "Unknown board ID '{0}'"


class InvalidBoardManifest(PlatformioException):

    MESSAGE = "Invalid board JSON manifest '{0}'"


class UnknownFramework(PlatformioException):

    MESSAGE = "Unknown framework '{0}'"


# Package Manager


class PlatformIOPackageException(PlatformioException):
    pass


class UnknownPackage(PlatformIOPackageException):

    MESSAGE = "Detected unknown package '{0}'"


class MissingPackageManifest(PlatformIOPackageException):

    MESSAGE = "Could not find one of '{0}' manifest files in the package"


class UndefinedPackageVersion(PlatformIOPackageException):

    MESSAGE = (
        "Could not find a version that satisfies the requirement '{0}'"
        " for your system '{1}'"
    )


class PackageInstallError(PlatformIOPackageException):

    MESSAGE = (
        "Could not install '{0}' with version requirements '{1}' "
        "for your system '{2}'.\n\n"
        "Please try this solution -> http://bit.ly/faq-package-manager"
    )


class ExtractArchiveItemError(PlatformIOPackageException):

    MESSAGE = (
        "Could not extract `{0}` to `{1}`. Try to disable antivirus "
        "tool or check this solution -> http://bit.ly/faq-package-manager"
    )


class UnsupportedArchiveType(PlatformIOPackageException):

    MESSAGE = "Can not unpack file '{0}'"


class FDUnrecognizedStatusCode(PlatformIOPackageException):

    MESSAGE = "Got an unrecognized status code '{0}' when downloaded {1}"


class FDSizeMismatch(PlatformIOPackageException):

    MESSAGE = (
        "The size ({0:d} bytes) of downloaded file '{1}' "
        "is not equal to remote size ({2:d} bytes)"
    )


class FDSHASumMismatch(PlatformIOPackageException):

    MESSAGE = (
        "The 'sha1' sum '{0}' of downloaded file '{1}' is not equal to remote '{2}'"
    )


#
# Library
#


class LibNotFound(PlatformioException):

    MESSAGE = (
        "Library `{0}` has not been found in PlatformIO Registry.\n"
        "You can ignore this message, if `{0}` is a built-in library "
        "(included in framework, SDK). E.g., SPI, Wire, etc."
    )


class NotGlobalLibDir(UserSideException):

    MESSAGE = (
        "The `{0}` is not a PlatformIO project.\n\n"
        "To manage libraries in global storage `{1}`,\n"
        "please use `platformio lib --global {2}` or specify custom storage "
        "`platformio lib --storage-dir /path/to/storage/ {2}`.\n"
        "Check `platformio lib --help` for details."
    )


class InvalidLibConfURL(PlatformioException):

    MESSAGE = "Invalid library config URL '{0}'"


#
# UDEV Rules
#


class InvalidUdevRules(PlatformioException):
    pass


class MissedUdevRules(InvalidUdevRules):

    MESSAGE = (
        "Warning! Please install `99-platformio-udev.rules`. \nMode details: "
        "https://docs.platformio.org/en/latest/faq.html#platformio-udev-rules"
    )


class OutdatedUdevRules(InvalidUdevRules):

    MESSAGE = (
        "Warning! Your `{0}` are outdated. Please update or reinstall them."
        "\n Mode details: https://docs.platformio.org"
        "/en/latest/faq.html#platformio-udev-rules"
    )


#
# Misc
#


class GetSerialPortsError(PlatformioException):

    MESSAGE = "No implementation for your platform ('{0}') available"


class GetLatestVersionError(PlatformioException):

    MESSAGE = "Can not retrieve the latest PlatformIO version"


class APIRequestError(PlatformioException):

    MESSAGE = "[API] {0}"


class InternetIsOffline(UserSideException):

    MESSAGE = (
        "You are not connected to the Internet.\n"
        "If you build a project first time, we need Internet connection "
        "to install all dependencies and toolchains."
    )


class BuildScriptNotFound(PlatformioException):

    MESSAGE = "Invalid path '{0}' to build script"


class InvalidSettingName(PlatformioException):

    MESSAGE = "Invalid setting with the name '{0}'"


class InvalidSettingValue(PlatformioException):

    MESSAGE = "Invalid value '{0}' for the setting '{1}'"


class InvalidJSONFile(PlatformioException):

    MESSAGE = "Could not load broken JSON: {0}"


class CIBuildEnvsEmpty(PlatformioException):

    MESSAGE = (
        "Can't find PlatformIO build environments.\n"
        "Please specify `--board` or path to `platformio.ini` with "
        "predefined environments using `--project-conf` option"
    )


class UpgradeError(PlatformioException):

    MESSAGE = """{0}

* Upgrade using `pip install -U platformio`
* Try different installation/upgrading steps:
  https://docs.platformio.org/page/installation.html
"""


class HomeDirPermissionsError(UserSideException):

    MESSAGE = (
        "The directory `{0}` or its parent directory is not owned by the "
        "current user and PlatformIO can not store configuration data.\n"
        "Please check the permissions and owner of that directory.\n"
        "Otherwise, please remove manually `{0}` directory and PlatformIO "
        "will create new from the current user."
    )


class CygwinEnvDetected(PlatformioException):

    MESSAGE = (
        "PlatformIO does not work within Cygwin environment. "
        "Use native Terminal instead."
    )


class TestDirNotExists(PlatformioException):

    MESSAGE = (
        "A test folder '{0}' does not exist.\nPlease create 'test' "
        "directory in project's root and put a test set.\n"
        "More details about Unit "
        "Testing: https://docs.platformio.org/page/plus/"
        "unit-testing.html"
    )
