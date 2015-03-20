# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

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

    # check content type and that file exists
    r = requests.head(package_data['url'], allow_redirects=True)
    validate_response(r)
    assert r.headers['Content-Type'] in ("application/x-gzip",
                                         "application/octet-stream")

    # check sha1 sum
    if sfpkglist is None:
        return pytest.skip("SF is offline")
    pkgname = basename(package_data['url'])
    assert pkgname in sfpkglist
    assert package_data['sha1'] == sfpkglist.get(pkgname, {}).get("sha1")
