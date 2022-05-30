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

import json

import click

from platformio.account.client import AccountClient


@click.command("token", short_help="Get or regenerate Authentication Token")
@click.option("-p", "--password", prompt=True, hide_input=True)
@click.option("--regenerate", is_flag=True)
@click.option("--json-output", is_flag=True)
def account_token_cmd(password, regenerate, json_output):
    client = AccountClient()
    auth_token = client.auth_token(password, regenerate)
    if json_output:
        click.echo(json.dumps({"status": "success", "result": auth_token}))
        return
    click.secho("Personal Authentication Token: %s" % auth_token, fg="green")
