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

import re

import click

from platformio.account.validate import validate_orgname_teamname, validate_username


def validate_urn(value):
    value = str(value).strip()
    if not re.match(r"^prn:reg:pkg:(\d+):(\w+)$", value, flags=re.I):
        raise click.BadParameter("Invalid URN format.")
    return value


def validate_client(value):
    if ":" in value:
        validate_orgname_teamname(value)
    else:
        validate_username(value)
    return value
