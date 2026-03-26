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


import inspect
import os


class BaseRPCHandler:
    PATH_ARGUMENT_MARKERS = (
        "path",
        "paths",
        "dir",
        "dirs",
        "directory",
        "directories",
        "file",
        "files",
        "folder",
        "folders",
    )

    factory = None

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if name.startswith("_") or not callable(attr):
            return attr

        def wrapped(*args, **kwargs):
            args, kwargs = self._normalize_path_arguments(attr, args, kwargs)
            return attr(*args, **kwargs)

        return wrapped

    def _normalize_path_arguments(self, method, args, kwargs):
        bound_args = inspect.signature(method).bind_partial(*args, **kwargs)
        for param_name, value in bound_args.arguments.items():
            if not self._is_path_argument(param_name):
                continue
            bound_args.arguments[param_name] = self._normalize_path_value(value)
        return bound_args.args, bound_args.kwargs

    def _is_path_argument(self, param_name):
        parts = param_name.lower().split("_")
        return any(marker in parts for marker in self.PATH_ARGUMENT_MARKERS)

    def _normalize_path_value(self, value):
        if not value:
            return value
        if isinstance(value, str):
            return os.path.normpath(value)
        if isinstance(value, list):
            return [self._normalize_path_value(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self._normalize_path_value(item) for item in value)
        if isinstance(value, set):
            return {self._normalize_path_value(item) for item in value}
        return value
