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


def validate_username(value, field="username"):
    value = str(value).strip()
    if not re.match(r"^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,37}$", value, flags=re.I):
        raise click.BadParameter(
            "Invalid %s format. "
            "%s must contain only alphanumeric characters "
            "or single hyphens, cannot begin or end with a hyphen, "
            "and must not be longer than 38 characters."
            % (field.lower(), field.capitalize())
        )
    return value


def validate_email(value):
    value = str(value).strip()
    if not re.match(r"^[a-z\d_.+-]+@[a-z\d\-]+\.[a-z\d\-.]+$", value, flags=re.I):
        raise click.BadParameter("Invalid email address")
    return value


def validate_password(value):
    value = str(value).strip()
    if not re.match(r"^(?=.*[a-z])(?=.*\d).{8,}$", value):
        raise click.BadParameter(
            "Invalid password format. "
            "Password must contain at least 8 characters"
            " including a number and a lowercase letter"
        )
    return value
