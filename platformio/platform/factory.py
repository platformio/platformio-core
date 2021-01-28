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

from platformio import fs
from platformio.compat import load_python_module
from platformio.package.meta import PackageItem
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
        # pylint: disable=import-outside-toplevel

        platform_dir = None
        platform_name = None
        if isinstance(pkg_or_spec, PackageItem):
            platform_dir = pkg_or_spec.path
            platform_name = pkg_or_spec.metadata.name
        elif os.path.isdir(pkg_or_spec):
            platform_dir = pkg_or_spec
        else:
            from platformio.package.manager.platform import PlatformPackageManager

            pkg = PlatformPackageManager().get_package(pkg_or_spec)
            if not pkg:
                raise UnknownPlatform(pkg_or_spec)
            platform_dir = pkg.path
            platform_name = pkg.metadata.name

        if not platform_dir or not os.path.isfile(
            os.path.join(platform_dir, "platform.json")
        ):
            raise UnknownPlatform(pkg_or_spec)

        if not platform_name:
            platform_name = fs.load_json(os.path.join(platform_dir, "platform.json"))[
                "name"
            ]

        platform_cls = None
        if os.path.isfile(os.path.join(platform_dir, "platform.py")):
            platform_cls = getattr(
                cls.load_module(
                    platform_name, os.path.join(platform_dir, "platform.py")
                ),
                cls.get_clsname(platform_name),
            )
        else:
            platform_cls = type(
                str(cls.get_clsname(platform_name)), (PlatformBase,), {}
            )

        _instance = platform_cls(os.path.join(platform_dir, "platform.json"))
        assert isinstance(_instance, PlatformBase)
        return _instance
