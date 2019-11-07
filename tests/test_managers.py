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

import json
from os.path import join

from platformio.managers.package import PackageManager
from platformio.project.helpers import get_project_core_dir


def test_pkg_input_parser():
    items = [
        ["PkgName", ("PkgName", None, None)],
        [("PkgName", "!=1.2.3,<2.0"), ("PkgName", "!=1.2.3,<2.0", None)],
        ["PkgName@1.2.3", ("PkgName", "1.2.3", None)],
        [("PkgName@1.2.3", "1.2.5"), ("PkgName@1.2.3", "1.2.5", None)],
        ["id=13", ("id=13", None, None)],
        ["id=13@~1.2.3", ("id=13", "~1.2.3", None)],
        [
            get_project_core_dir(),
            (".platformio", None, "file://" + get_project_core_dir()),
        ],
        [
            "LocalName=" + get_project_core_dir(),
            ("LocalName", None, "file://" + get_project_core_dir()),
        ],
        [
            "LocalName=%s@>2.3.0" % get_project_core_dir(),
            ("LocalName", ">2.3.0", "file://" + get_project_core_dir()),
        ],
        [
            "https://github.com/user/package.git",
            ("package", None, "git+https://github.com/user/package.git"),
        ],
        [
            "MyPackage=https://gitlab.com/user/package.git",
            ("MyPackage", None, "git+https://gitlab.com/user/package.git"),
        ],
        [
            "MyPackage=https://gitlab.com/user/package.git@3.2.1,!=2",
            ("MyPackage", "3.2.1,!=2", "git+https://gitlab.com/user/package.git"),
        ],
        [
            "https://somedomain.com/path/LibraryName-1.2.3.zip",
            (
                "LibraryName-1.2.3",
                None,
                "https://somedomain.com/path/LibraryName-1.2.3.zip",
            ),
        ],
        [
            "https://github.com/user/package/archive/branch.zip",
            ("branch", None, "https://github.com/user/package/archive/branch.zip"),
        ],
        [
            "https://github.com/user/package/archive/branch.zip@~1.2.3",
            ("branch", "~1.2.3", "https://github.com/user/package/archive/branch.zip"),
        ],
        [
            "https://github.com/user/package/archive/branch.tar.gz",
            (
                "branch.tar",
                None,
                "https://github.com/user/package/archive/branch.tar.gz",
            ),
        ],
        [
            "https://github.com/user/package/archive/branch.tar.gz@!=5",
            (
                "branch.tar",
                "!=5",
                "https://github.com/user/package/archive/branch.tar.gz",
            ),
        ],
        [
            "https://developer.mbed.org/users/user/code/package/",
            ("package", None, "hg+https://developer.mbed.org/users/user/code/package/"),
        ],
        [
            "https://os.mbed.com/users/user/code/package/",
            ("package", None, "hg+https://os.mbed.com/users/user/code/package/"),
        ],
        [
            "https://github.com/user/package#v1.2.3",
            ("package", None, "git+https://github.com/user/package#v1.2.3"),
        ],
        [
            "https://github.com/user/package.git#branch",
            ("package", None, "git+https://github.com/user/package.git#branch"),
        ],
        [
            "PkgName=https://github.com/user/package.git#a13d344fg56",
            ("PkgName", None, "git+https://github.com/user/package.git#a13d344fg56"),
        ],
        ["user/package", ("package", None, "git+https://github.com/user/package")],
        [
            "PkgName=user/package",
            ("PkgName", None, "git+https://github.com/user/package"),
        ],
        [
            "PkgName=user/package#master",
            ("PkgName", None, "git+https://github.com/user/package#master"),
        ],
        [
            "git+https://github.com/user/package",
            ("package", None, "git+https://github.com/user/package"),
        ],
        [
            "hg+https://example.com/user/package",
            ("package", None, "hg+https://example.com/user/package"),
        ],
        [
            "git@github.com:user/package.git",
            ("package", None, "git+git@github.com:user/package.git"),
        ],
        [
            "git@github.com:user/package.git#v1.2.0",
            ("package", None, "git+git@github.com:user/package.git#v1.2.0"),
        ],
        [
            "LocalName=git@github.com:user/package.git#v1.2.0@~1.2.0",
            ("LocalName", "~1.2.0", "git+git@github.com:user/package.git#v1.2.0"),
        ],
        [
            "git+ssh://git@gitlab.private-server.com/user/package#1.2.0",
            (
                "package",
                None,
                "git+ssh://git@gitlab.private-server.com/user/package#1.2.0",
            ),
        ],
        [
            "git+ssh://user@gitlab.private-server.com:1234/package#1.2.0",
            (
                "package",
                None,
                "git+ssh://user@gitlab.private-server.com:1234/package#1.2.0",
            ),
        ],
        [
            "LocalName=git+ssh://user@gitlab.private-server.com:1234"
            "/package#1.2.0@!=13",
            (
                "LocalName",
                "!=13",
                "git+ssh://user@gitlab.private-server.com:1234/package#1.2.0",
            ),
        ],
    ]
    for params, result in items:
        if isinstance(params, tuple):
            assert PackageManager.parse_pkg_uri(*params) == result
        else:
            assert PackageManager.parse_pkg_uri(params) == result


def test_install_packages(isolated_pio_home, tmpdir):
    packages = [
        dict(id=1, name="name_1", version="shasum"),
        dict(id=1, name="name_1", version="2.0.0"),
        dict(id=1, name="name_1", version="2.1.0"),
        dict(id=1, name="name_1", version="1.2"),
        dict(id=1, name="name_1", version="1.0.0"),
        dict(name="name_2", version="1.0.0"),
        dict(name="name_2", version="2.0.0", __src_url="git+https://github.com"),
        dict(name="name_2", version="3.0.0", __src_url="git+https://github2.com"),
        dict(name="name_2", version="4.0.0", __src_url="git+https://github2.com"),
    ]

    pm = PackageManager(join(get_project_core_dir(), "packages"))
    for package in packages:
        tmp_dir = tmpdir.mkdir("tmp-package")
        tmp_dir.join("package.json").write(json.dumps(package))
        pm._install_from_url(package["name"], "file://%s" % str(tmp_dir))
        tmp_dir.remove(rec=1)

    assert len(pm.get_installed()) == len(packages) - 1

    pkg_dirnames = [
        "name_1_ID1",
        "name_1_ID1@1.0.0",
        "name_1_ID1@1.2",
        "name_1_ID1@2.0.0",
        "name_1_ID1@shasum",
        "name_2",
        "name_2@src-177cbce1f0705580d17790fda1cc2ef5",
        "name_2@src-f863b537ab00f4c7b5011fc44b120e1f",
    ]
    assert set(
        [p.basename for p in isolated_pio_home.join("packages").listdir()]
    ) == set(pkg_dirnames)


def test_get_package():
    tests = [
        [("unknown",), None],
        [("1",), None],
        [("id=1", "shasum"), dict(id=1, name="name_1", version="shasum")],
        [("id=1", "*"), dict(id=1, name="name_1", version="2.1.0")],
        [("id=1", "^1"), dict(id=1, name="name_1", version="1.2")],
        [("id=1", "^1"), dict(id=1, name="name_1", version="1.2")],
        [("name_1", "<2"), dict(id=1, name="name_1", version="1.2")],
        [("name_1", ">2"), None],
        [("name_1", "2-0-0"), None],
        [("name_2",), dict(name="name_2", version="4.0.0")],
        [
            ("url_has_higher_priority", None, "git+https://github.com"),
            dict(name="name_2", version="2.0.0", __src_url="git+https://github.com"),
        ],
        [
            ("name_2", None, "git+https://github.com"),
            dict(name="name_2", version="2.0.0", __src_url="git+https://github.com"),
        ],
    ]

    pm = PackageManager(join(get_project_core_dir(), "packages"))
    for test in tests:
        manifest = pm.get_package(*test[0])
        if test[1] is None:
            assert manifest is None, test
            continue
        for key, value in test[1].items():
            assert manifest[key] == value, test
