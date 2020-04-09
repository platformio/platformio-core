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

import json
import re
import sys

import click

from platformio import exception
from platformio.commands.account.client import AccountClient
from platformio.managers.core import pioplus_call


@click.group("account", short_help="Manage PIO Account")
def cli():
    pass


def validate_username(value):
    value = str(value).strip()
    if not re.match(r"^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){3,38}$", value, flags=re.I):
        raise click.BadParameter(
            "Invalid username format. "
            "Username must contain at least 4 characters including single hyphens,"
            " and cannot begin or end with a hyphen"
        )
    return value


def validate_email(value):
    value = str(value).strip()
    if not re.match(r"^[a-z\d_.+-]+@[a-z\d\-]+\.[a-z\d\-.]+$", value, flags=re.I):
        raise click.BadParameter("Invalid E-Mail address")
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


@cli.command("register", short_help="Create new PIO Account")
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
@click.option("--first-name", prompt=True)
@click.option("--last-name", prompt=True)
def account_register(username, email, password, first_name, last_name):
    client = AccountClient()
    try:
        client.registration(username, email, password, first_name, last_name)
        return click.secho(
            "An account has been successfully created. "
            "Please check your mail to activate your account and verify your email address.",
            fg="green",
        )
    except exception.AccountAlreadyAuthenticated as e:
        return click.secho(str(e), fg="yellow",)


@cli.command("login", short_help="Log in to PIO Account")
@click.option("-u", "--username", prompt="Username or e-mail")
@click.option("-p", "--password", prompt=True, hide_input=True)
def account_login(username, password):
    client = AccountClient()
    try:
        client.login(username, password)
        return click.secho("Successfully logged in!", fg="green")
    except exception.AccountAlreadyAuthenticated as e:
        return click.secho(str(e), fg="yellow",)


@cli.command("logout", short_help="Log out of PIO Account")
def account_logout():
    client = AccountClient()
    try:
        client.logout()
        return click.secho("Successfully logged out!", fg="green")
    except exception.AccountNotAuthenticated as e:
        return click.secho(str(e), fg="yellow",)


@cli.command("password", short_help="Change password")
@click.option("--old-password", prompt=True, hide_input=True)
@click.option("--new-password", prompt=True, hide_input=True, confirmation_prompt=True)
def account_password(old_password, new_password):
    client = AccountClient()
    try:
        client.change_password(old_password, new_password)
        return click.secho("Password successfully changed!", fg="green")
    except exception.AccountNotAuthenticated as e:
        return click.secho(str(e), fg="yellow",)


@cli.command("token", short_help="Get or regenerate Authentication Token")
@click.option("-p", "--password", prompt=True, hide_input=True)
@click.option("--regenerate", is_flag=True)
@click.option("--json-output", is_flag=True)
def account_token(password, regenerate, json_output):
    client = AccountClient()
    try:
        auth_token = client.auth_token(password, regenerate)
        if json_output:
            return click.echo(json.dumps({"status": "success", "result": auth_token}))
        return click.secho("Personal Authentication Token: %s" % auth_token, fg="green")
    except exception.AccountNotAuthenticated as e:
        return click.secho(str(e), fg="yellow",)


@cli.command("forgot", short_help="Forgot password")
@click.option("--username", prompt="Username or e-mail")
def account_forgot(username):
    client = AccountClient()
    try:
        client.forgot_password(username)
        return click.secho(
            "If this account is registered, we will send the "
            "further instructions to your E-Mail.",
            fg="green",
        )
    except exception.AccountAlreadyAuthenticated as e:
        return click.secho(str(e), fg="yellow",)


@cli.command("update", short_help="Update profile information")
@click.option("--current-password", prompt=True, hide_input=True)
def account_update(current_password):
    client = AccountClient()
    try:
        profile = client.get_profile()
        new_profile = {}
        for field in profile:
            new_profile[field] = click.prompt(
                field.replace("_", " ").capitalize(), default=profile[field]
            )
            if field == "email":
                validate_email(new_profile[field])
            if field == "username":
                validate_username(new_profile[field])
        client.update_profile(new_profile, current_password)
        if new_profile["email"] != profile["email"]:
            try:
                client.logout()
            except exception.AccountNotAuthenticated:
                pass
            return click.secho(
                "Profile successfully updated! "
                "Please check your mail to verify your new email address and re-login.",
                fg="green",
            )
        if new_profile["username"] != profile["username"]:
            try:
                client.logout()
            except exception.AccountNotAuthenticated:
                pass
            return click.secho(
                "Profile successfully updated! Please re-login.", fg="green"
            )
        return click.secho("Profile successfully updated!", fg="green")
    except exception.AccountNotAuthenticated as e:
        return click.secho(str(e), fg="yellow",)


@cli.command("show", short_help="PIO Account information")
@click.option("--offline", is_flag=True)
@click.option("--json-output", is_flag=True)
def account_show(**kwargs):
    pioplus_call(sys.argv[1:])
