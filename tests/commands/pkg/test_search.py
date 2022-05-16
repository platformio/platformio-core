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

from platformio.package.commands.search import package_search_cmd


def test_empty_query(clirunner, validate_cliresult):
    result = clirunner.invoke(
        package_search_cmd,
        [""],
    )
    validate_cliresult(result)
    assert all(t in result.output for t in ("Found", "Official", "page 1 of"))


def test_pagination(clirunner, validate_cliresult):
    result = clirunner.invoke(
        package_search_cmd,
        ["type:tool"],
    )
    validate_cliresult(result)
    assert all(t in result.output for t in ("Verified Tool", "page 1 of"))

    result = clirunner.invoke(
        package_search_cmd,
        ["type:tool", "-p", "10"],
    )
    validate_cliresult(result)
    assert all(t in result.output for t in ("Tool", "page 10 of"))


def test_sorting(clirunner, validate_cliresult):
    result = clirunner.invoke(
        package_search_cmd,
        ["OneWire", "-s", "popularity"],
    )
    validate_cliresult(result)
    assert "paulstoffregen/OneWire" in result.output


def test_not_found(clirunner, validate_cliresult):
    result = clirunner.invoke(
        package_search_cmd,
        ["name:unknown-package"],
    )
    validate_cliresult(result)
    assert "Nothing has been found" in result.output
