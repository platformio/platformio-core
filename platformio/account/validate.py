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
    value = str(value).strip() if value else None
    if not value or not re.match(
        r"^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,37}$", value, flags=re.I
    ):
        raise click.BadParameter(
            "Invalid %s format. "
            "%s must contain only alphanumeric characters "
            "or single hyphens, cannot begin or end with a hyphen, "
            "and must not be longer than 38 characters."
            % (field.lower(), field.capitalize())
        )
    return value


def validate_orgname(value):
    return validate_username(value, "Organization name")


def validate_email(value):
    value = str(value).strip() if value else None
    if not value or not re.match(
        r"^[a-z\d_\.\+\-]+@[a-z\d\-]+\.[a-z\d\-\.]+$", value, flags=re.I
    ):
        raise click.BadParameter("Invalid email address")
    return value


def validate_password(value):
    value = str(value).strip() if value else None
    if not value or not re.match(r"^(?=.*[a-z])(?=.*\d).{8,}$", value):
        raise click.BadParameter(
            "Invalid password format. "
            "Password must contain at least 8 characters"
            " including a number and a lowercase letter"
        )
    return value


def validate_teamname(value):
    value = str(value).strip() if value else None
    if not value or not re.match(
        r"^[a-z\d](?:[a-z\d]|[\-_ ](?=[a-z\d])){0,19}$", value, flags=re.I
    ):
        raise click.BadParameter(
            "Invalid team name format. "
            "Team name must only contain alphanumeric characters, "
            "single hyphens, underscores, spaces. It can not "
            "begin or end with a hyphen or a underscore and must"
            " not be longer than 20 characters."
        )
    return value


def validate_orgname_teamname(value):
    value = str(value).strip() if value else None
    if not value or ":" not in value:
        raise click.BadParameter(
            "Please specify organization and team name using the following"
            " format - orgname:teamname. For example, mycompany:DreamTeam"
        )
    orgname, teamname = value.split(":", 1)
    validate_orgname(orgname)
    validate_teamname(teamname)
    return value
