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

import pytest
import requests
from os.path import basename

from platformio.util import get_api_result


@pytest.fixture(scope="session")
def sfpkglist():
    result = None
    r = None

    try:
        r = requests.get("http://sourceforge.net/projects"
                         "/platformio-storage/files/packages/list")
        result = r.json()
        r.raise_for_status()
    except:
        pass
    finally:
        if r:
            r.close()
    return result


def pytest_generate_tests(metafunc):
    if "package_data" not in metafunc.fixturenames:
        return
    pkgs_manifest = get_api_result("/packages/manifest")
    assert isinstance(pkgs_manifest, dict)
    packages = []
    for _, variants in pkgs_manifest.iteritems():
        for item in variants:
            packages.append(item)
    metafunc.parametrize("package_data", packages)


def validate_response(req):
    assert req.status_code == 200
    assert int(req.headers['Content-Length']) > 0


def validate_package(url, sfpkglist):
    r = requests.head(url, allow_redirects=True)
    validate_response(r)
    assert r.headers['Content-Type'] in ("application/x-gzip",
                                         "application/octet-stream")


def test_package(package_data, sfpkglist):
    assert package_data['url'].endswith("%d.tar.gz" % package_data['version'])
    sf_package = "sourceforge.net" in package_data['url']

    # check content type and that file exists
    try:
        r = requests.head(package_data['url'], allow_redirects=True)
        if 500 <= r.status_code <= 599:
            raise requests.exceptions.ConnectionError()
    except requests.exceptions.ConnectionError as e:
        if sf_package:
            return pytest.skip("SF is off-line")
        raise Exception(e)

    validate_response(r)
    assert r.headers['Content-Type'] in ("application/x-gzip",
                                         "application/octet-stream")

    if not sf_package:
        return

    # check sha1 sum
    if sfpkglist is None:
        return pytest.skip("SF is off-line")
    pkgname = basename(package_data['url'])
    assert pkgname in sfpkglist
    assert package_data['sha1'] == sfpkglist.get(pkgname, {}).get("sha1")
