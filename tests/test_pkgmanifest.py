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

import pytest
import requests


def validate_response(r):
    assert r.status_code == 200, r.url
    assert int(r.headers['Content-Length']) > 0, r.url
    assert r.headers['Content-Type'] in ("application/gzip",
                                         "application/octet-stream")


def test_packages():
    pkgs_manifest = requests.get(
        "https://dl.bintray.com/platformio/dl-packages/manifest.json").json()
    assert isinstance(pkgs_manifest, dict)
    items = []
    for _, variants in pkgs_manifest.items():
        for item in variants:
            items.append(item)

    for item in items:
        assert item['url'].endswith(".tar.gz"), item

        r = requests.head(item['url'], allow_redirects=True)
        validate_response(r)

        if "X-Checksum-Sha1" not in r.headers:
            return pytest.skip("X-Checksum-Sha1 is not provided")

        assert item['sha1'] == r.headers.get("X-Checksum-Sha1")[0:40], item
