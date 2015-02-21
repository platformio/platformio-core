# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import requests
from platformio.util import get_api_result


def pytest_generate_tests(metafunc):
    if "package_data" not in metafunc.fixturenames:
        return
    pkgs_manifest = get_api_result("/packages")
    assert isinstance(pkgs_manifest, dict)
    packages = []
    for _, variants in pkgs_manifest.iteritems():
        for item in variants:
            packages.append(item)
    metafunc.parametrize("package_data", packages)


def validate_response(req):
    assert req.status_code == 200
    assert int(req.headers['Content-Length']) > 0


def validate_package(url):
    r = requests.head(url, allow_redirects=True)
    validate_response(r)
    assert r.headers['Content-Type'] == "application/x-gzip"


def test_package(package_data):
    assert package_data['url'].endswith("%d.tar.gz" % package_data['version'])
    validate_package(package_data['url'])
