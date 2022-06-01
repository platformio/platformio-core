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
from platformio.account.validate import validate_email, validate_orgname


@click.command("update", short_help="Update organization")
@click.argument("cur_orgname")
@click.option(
    "--orgname",
    callback=lambda _, __, value: validate_orgname(value),
    help="A new orgname",
)
@click.option("--email")
@click.option("--displayname")
def org_update_cmd(cur_orgname, **kwargs):
    client = AccountClient()
    org = client.get_org(cur_orgname)
    del org["owners"]
    new_org = org.copy()
    if not any(kwargs.values()):
        for field in org:
            new_org[field] = click.prompt(
                field.replace("_", " ").capitalize(), default=org[field]
            )
            if field == "email":
                validate_email(new_org[field])
            if field == "orgname":
                validate_orgname(new_org[field])
    else:
        new_org.update(
            {key.replace("new_", ""): value for key, value in kwargs.items() if value}
        )
    client.update_org(cur_orgname, new_org)
    return click.secho(
        "The organization `%s` has been successfully updated." % cur_orgname,
        fg="green",
    )
