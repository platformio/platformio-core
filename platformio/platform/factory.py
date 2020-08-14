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

import os
import re

from platformio.compat import load_python_module
from platformio.package.manager.platform import PlatformPackageManager
from platformio.platform.base import PlatformBase
from platformio.platform.exception import UnknownPlatform


class PlatformFactory(object):
    @staticmethod
    def get_clsname(name):
        name = re.sub(r"[^\da-z\_]+", "", name, flags=re.I)
        return "%s%sPlatform" % (name.upper()[0], name.lower()[1:])

    @staticmethod
    def load_module(name, path):
        try:
            return load_python_module("platformio.platform.%s" % name, path)
        except ImportError:
            raise UnknownPlatform(name)

    @classmethod
    def new(cls, pkg_or_spec):
        pkg = PlatformPackageManager().get_package(
            "file://%s" % pkg_or_spec if os.path.isdir(pkg_or_spec) else pkg_or_spec
        )
        if not pkg:
            raise UnknownPlatform(pkg_or_spec)

        platform_cls = None
        if os.path.isfile(os.path.join(pkg.path, "platform.py")):
            platform_cls = getattr(
                cls.load_module(
                    pkg.metadata.name, os.path.join(pkg.path, "platform.py")
                ),
                cls.get_clsname(pkg.metadata.name),
            )
        else:
            platform_cls = type(
                str(cls.get_clsname(pkg.metadata.name)), (PlatformBase,), {}
            )

        _instance = platform_cls(os.path.join(pkg.path, "platform.json"))
        assert isinstance(_instance, PlatformBase)
        return _instance
