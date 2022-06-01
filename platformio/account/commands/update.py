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

from platformio.account.client import AccountClient, AccountNotAuthorized
from platformio.account.validate import validate_email, validate_username


@click.command("update", short_help="Update profile information")
@click.option("--current-password", prompt=True, hide_input=True)
@click.option("--username")
@click.option("--email")
@click.option("--firstname")
@click.option("--lastname")
def account_update_cmd(current_password, **kwargs):
    client = AccountClient()
    profile = client.get_profile()
    new_profile = profile.copy()
    if not any(kwargs.values()):
        for field in profile:
            new_profile[field] = click.prompt(
                field.replace("_", " ").capitalize(), default=profile[field]
            )
            if field == "email":
                validate_email(new_profile[field])
            if field == "username":
                validate_username(new_profile[field])
    else:
        new_profile.update({key: value for key, value in kwargs.items() if value})
    client.update_profile(new_profile, current_password)
    click.secho("Profile successfully updated!", fg="green")
    username_changed = new_profile["username"] != profile["username"]
    email_changed = new_profile["email"] != profile["email"]
    if not username_changed and not email_changed:
        return None
    try:
        client.logout()
    except AccountNotAuthorized:
        pass
    if email_changed:
        click.secho(
            "Please check your mail to verify your new email address and re-login. ",
            fg="yellow",
        )
        return None
    click.secho("Please re-login.", fg="yellow")
    return None
