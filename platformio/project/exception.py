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

from platformio.exception import PlatformioException, UserSideException


class ProjectError(PlatformioException):
    pass


class NotPlatformIOProjectError(ProjectError, UserSideException):
    MESSAGE = (
        "Not a PlatformIO project. `platformio.ini` file has not been "
        "found in current working directory ({0}). To initialize new project "
        "please use `platformio project init` command"
    )


class InvalidProjectConfError(ProjectError, UserSideException):
    MESSAGE = "Invalid '{0}' (project configuration file): '{1}'"


class UndefinedEnvPlatformError(ProjectError, UserSideException):
    MESSAGE = "Please specify platform for '{0}' environment"


class ProjectEnvsNotAvailableError(ProjectError, UserSideException):
    MESSAGE = "Please setup environments in `platformio.ini` file"


class UnknownEnvNamesError(ProjectError, UserSideException):
    MESSAGE = "Unknown environment names '{0}'. Valid names are '{1}'"


class InvalidEnvNameError(ProjectError, UserSideException):
    MESSAGE = (
        "Invalid environment name '{0}'. The name can contain "
        "alphanumeric, underscore, and hyphen characters (a-z, 0-9, -, _)"
    )


class ProjectOptionValueError(ProjectError, UserSideException):
    pass
