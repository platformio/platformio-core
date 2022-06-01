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

import click

from platformio.account.client import AccountClient
from platformio.account.validate import (
    validate_email,
    validate_password,
    validate_username,
)


@click.command("register", short_help="Create new PlatformIO Account")
@click.option(
    "-u",
    "--username",
    prompt=True,
    callback=lambda _, __, value: validate_username(value),
)
@click.option(
    "-e", "--email", prompt=True, callback=lambda _, __, value: validate_email(value)
)
@click.option(
    "-p",
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    callback=lambda _, __, value: validate_password(value),
)
@click.option("--firstname", prompt=True)
@click.option("--lastname", prompt=True)
def account_register_cmd(username, email, password, firstname, lastname):
    client = AccountClient()
    client.registration(username, email, password, firstname, lastname)
    click.secho(
        "An account has been successfully created. "
        "Please check your mail to activate your account and verify your email address.",
        fg="green",
    )
