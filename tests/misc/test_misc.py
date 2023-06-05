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

# pylint: disable=unused-argument

import pytest
import requests

from platformio import __check_internet_hosts__, http, proc
from platformio.registry.client import RegistryClient


def test_platformio_cli():
    result = proc.exec_command(["pio", "--help"])
    assert result["returncode"] == 0
    # pylint: disable=unsupported-membership-test
    assert "Usage: pio [OPTIONS] COMMAND [ARGS]..." in result["out"]


def test_ping_internet_ips():
    for host in __check_internet_hosts__:
        requests.get("http://%s" % host, allow_redirects=False, timeout=2)


def test_api_internet_offline(without_internet, isolated_pio_core):
    regclient = RegistryClient()
    with pytest.raises(http.InternetConnectionError):
        regclient.fetch_json_data("get", "/v3/search")


def test_api_cache(monkeypatch, isolated_pio_core):
    regclient = RegistryClient()
    api_kwargs = {"method": "get", "path": "/v3/search", "x_cache_valid": "10s"}
    result = regclient.fetch_json_data(**api_kwargs)
    assert result and "total" in result
    monkeypatch.setattr(http, "_internet_on", lambda: False)
    assert regclient.fetch_json_data(**api_kwargs) == result
