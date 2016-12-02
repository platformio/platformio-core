# Copyright 2014-present PlatformIO <contact@platformio.org>
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
from platformio.managers.package import BasePkgManager


def test_pkg_name_parser():
    items = [
        ["PkgName", ("PkgName", None, None)],
        [("PkgName", "!=1.2.3,<2.0"), ("PkgName", "!=1.2.3,<2.0", None)],
        ["PkgName@1.2.3", ("PkgName", "1.2.3", None)],
        [("PkgName@1.2.3", "1.2.5"), ("PkgName@1.2.3", "1.2.5", None)],
        ["id:13", ("id:13", None, None)],
        ["id:13@~1.2.3", ("id:13", "~1.2.3", None)], [
            util.get_home_dir(),
            (".platformio", None, "file://" + util.get_home_dir())
        ], [
            "LocalName=" + util.get_home_dir(),
            ("LocalName", None, "file://" + util.get_home_dir())
        ], [
            "https://github.com/user/package.git",
            ("package", None, "git+https://github.com/user/package.git")
        ], [
            "https://gitlab.com/user/package.git",
            ("package", None, "git+https://gitlab.com/user/package.git")
        ], [
            "https://github.com/user/package/archive/branch.zip",
            ("branch", None,
             "https://github.com/user/package/archive/branch.zip")
        ], [
            "https://github.com/user/package/archive/branch.tar.gz",
            ("branch", None,
             "https://github.com/user/package/archive/branch.tar.gz")
        ], [
            "https://developer.mbed.org/users/user/code/package/",
            ("package", None,
             "hg+https://developer.mbed.org/users/user/code/package/")
        ], [
            "https://github.com/user/package#v1.2.3",
            ("package", None, "git+https://github.com/user/package#v1.2.3")
        ], [
            "https://github.com/user/package.git#branch",
            ("package", None, "git+https://github.com/user/package.git#branch")
        ], [
            "PkgName=https://github.com/user/package.git#a13d344fg56",
            ("PkgName", None,
             "git+https://github.com/user/package.git#a13d344fg56")
        ], [
            "PkgName=user/package",
            ("PkgName", None, "git+https://github.com/user/package")
        ], [
            "PkgName=user/package#master",
            ("PkgName", None, "git+https://github.com/user/package#master")
        ], [
            "git+https://github.com/user/package",
            ("package", None, "git+https://github.com/user/package")
        ], [
            "hg+https://example.com/user/package",
            ("package", None, "hg+https://example.com/user/package")
        ], [
            "git@github.com:user/package.git",
            ("package", None, "git@github.com:user/package.git")
        ], [
            "git@github.com:user/package.git#v1.2.0",
            ("package", None, "git@github.com:user/package.git#v1.2.0")
        ], [
            "git+ssh://git@gitlab.private-server.com/user/package#1.2.0",
            ("package", None,
             "git+ssh://git@gitlab.private-server.com/user/package#1.2.0")
        ]
    ]
    for params, result in items:
        if isinstance(params, tuple):
            assert BasePkgManager.parse_pkg_name(*params) == result
        else:
            assert BasePkgManager.parse_pkg_name(params) == result
