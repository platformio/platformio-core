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


@click.command("login", short_help="Log in to PlatformIO Account")
@click.option("-u", "--username", prompt="Username or email")
@click.option("-p", "--password", prompt=True, hide_input=True)
def account_login_cmd(username, password):
    client = AccountClient()
    client.login(username, password)
    click.secho("Successfully logged in!", fg="green")
