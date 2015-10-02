# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.


class PlatformioException(Exception):

    MESSAGE = None

    def __str__(self):  # pragma: no cover
        if self.MESSAGE:
            return self.MESSAGE % self.args
        else:
            return Exception.__str__(self)


class ReturnErrorCode(PlatformioException):
    pass


class MinitermException(PlatformioException):
    pass


class AbortedByUser(PlatformioException):

    MESSAGE = "Aborted by user"


class UnknownPlatform(PlatformioException):

    MESSAGE = "Unknown platform '%s'"


class PlatformNotInstalledYet(PlatformioException):

    MESSAGE = ("The platform '%s' has not been installed yet. "
               "Use `platformio platforms install` command")


class UnknownCLICommand(PlatformioException):

    MESSAGE = ("Unknown command '%s'. Please use `platformio --help`"
               " to see all available commands")


class UnknownBoard(PlatformioException):

    MESSAGE = "Unknown board type '%s'"


class UnknownFramework(PlatformioException):

    MESSAGE = "Unknown framework '%s'"


class UnknownPackage(PlatformioException):

    MESSAGE = "Detected unknown package '%s'"


class InvalidPackageVersion(PlatformioException):

    MESSAGE = "The package '%s' with version '%d' does not exist"


class NonSystemPackage(PlatformioException):

    MESSAGE = "The package '%s' is not available for your system '%s'"


class FDUnrecognizedStatusCode(PlatformioException):

    MESSAGE = "Got an unrecognized status code '%s' when downloaded %s"


class FDSizeMismatch(PlatformioException):

    MESSAGE = ("The size (%d bytes) of downloaded file '%s' "
               "is not equal to remote size (%d bytes)")


class FDSHASumMismatch(PlatformioException):

    MESSAGE = ("The 'sha1' sum '%s' of downloaded file '%s' "
               "is not equal to remote '%s'")


class NotPlatformProject(PlatformioException):

    MESSAGE = "Not a PlatformIO project. `platformio.ini` file has not been "\
        "found in current working directory (%s). To initialize new project "\
        "please use `platformio init` command"


class UndefinedEnvPlatform(PlatformioException):

    MESSAGE = "Please specify platform for '%s' environment"


class UnsupportedArchiveType(PlatformioException):

    MESSAGE = "Can not unpack file '%s'"


class ProjectEnvsNotAvailable(PlatformioException):

    MESSAGE = "Please setup environments in `platformio.ini` file."


class InvalidEnvName(PlatformioException):

    MESSAGE = "Invalid environment '%s'. The name must start " "with 'env:'."


class UnknownEnvNames(PlatformioException):

    MESSAGE = "Unknown environment names '%s'."


class GetSerialPortsError(PlatformioException):

    MESSAGE = "No implementation for your platform ('%s') available"


class GetLatestVersionError(PlatformioException):

    MESSAGE = "Can't retrieve the latest PlatformIO version"


class APIRequestError(PlatformioException):

    MESSAGE = "[API] %s"


class LibAlreadyInstalledError(PlatformioException):
    pass


class LibNotInstalledError(PlatformioException):

    MESSAGE = "Library #%d has not been installed yet"


class LibInstallDependencyError(PlatformioException):

    MESSAGE = "Error has been occurred for library dependency '%s'"


class InvalidLibConfURL(PlatformioException):

    MESSAGE = "Invalid library config URL '%s'"


class BuildScriptNotFound(PlatformioException):

    MESSAGE = "Invalid path '%s' to build script"


class InvalidSettingName(PlatformioException):

    MESSAGE = "Invalid setting with the name '%s'"


class InvalidSettingValue(PlatformioException):

    MESSAGE = "Invalid value '%s' for the setting '%s'"


class UpgraderFailed(PlatformioException):

    MESSAGE = "An error occurred while upgrading PlatformIO"


class CIBuildEnvsEmpty(PlatformioException):

    MESSAGE = (
        "Can't find PlatformIO build environments.\nPlease specify `--board` "
        "or path to `platformio.ini` with predefined environments using "
        "`--project-conf` option"
    )


class SConsNotInstalled(PlatformioException):

    MESSAGE = (
        "The PlatformIO and `scons` aren't installed properly. "
        "More details in FAQ/Troubleshooting section: "
        "http://docs.platformio.org/en/latest/faq.html"
    )


class PlatformioUpgradeError(PlatformioException):

    MESSAGE = (
        "%s \n\n"
        "1. Please report this issue here: "
        "https://github.com/platformio/platformio/issues \n"
        "2. Try different installation/upgrading steps: "
        "http://docs.platformio.org/en/latest/installation.html"
    )


class CygwinEnvDetected(PlatformioException):

    MESSAGE = (
        "PlatformIO does not work within Cygwin environment. "
        "Use native Terminal instead."
    )
