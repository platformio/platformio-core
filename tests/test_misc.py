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

from platformio import exception, util


def test_ping_internet_ips():
    for ip in util.PING_INTERNET_IPS:
        requests.get("http://%s" % ip, allow_redirects=False, timeout=2)


def test_api_internet_offline(without_internet, isolated_pio_home):
    with pytest.raises(exception.InternetIsOffline):
        util.get_api_result("/stats")


def test_api_cache(monkeypatch, isolated_pio_home):
    api_kwargs = {"url": "/stats", "cache_valid": "10s"}
    result = util.get_api_result(**api_kwargs)
    assert result and "boards" in result
    monkeypatch.setattr(util, '_internet_on', lambda: False)
    assert util.get_api_result(**api_kwargs) == result
