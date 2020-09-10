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

import click
from tabulate import tabulate

from platformio.clients.account import AccountClient
from platformio.commands.account import validate_email, validate_username


@click.group("org", short_help="Manage organizations")
def cli():
    pass


def validate_orgname(value):
    return validate_username(value, "Organization name")


@cli.command("create", short_help="Create a new organization")
@click.argument(
    "orgname",
    callback=lambda _, __, value: validate_orgname(value),
)
@click.option(
    "--email", callback=lambda _, __, value: validate_email(value) if value else value
)
@click.option(
    "--displayname",
)
def org_create(orgname, email, displayname):
    client = AccountClient()
    client.create_org(orgname, email, displayname)
    return click.secho(
        "The organization `%s` has been successfully created." % orgname,
        fg="green",
    )


@cli.command("list", short_help="List organizations and their members")
@click.option("--json-output", is_flag=True)
def org_list(json_output):
    client = AccountClient()
    orgs = client.list_orgs()
    if json_output:
        return click.echo(json.dumps(orgs))
    if not orgs:
        return click.echo("You do not have any organization")
    for org in orgs:
        click.echo()
        click.secho(org.get("orgname"), fg="cyan")
        click.echo("-" * len(org.get("orgname")))
        data = []
        if org.get("displayname"):
            data.append(("Display Name:", org.get("displayname")))
        if org.get("email"):
            data.append(("Email:", org.get("email")))
        data.append(
            (
                "Owners:",
                ", ".join((owner.get("username") for owner in org.get("owners"))),
            )
        )
        click.echo(tabulate(data, tablefmt="plain"))
    return click.echo()


@cli.command("update", short_help="Update organization")
@click.argument("cur_orgname")
@click.option(
    "--orgname",
    callback=lambda _, __, value: validate_orgname(value),
    help="A new orgname",
)
@click.option("--email")
@click.option("--displayname")
def org_update(cur_orgname, **kwargs):
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


@cli.command("destroy", short_help="Destroy organization")
@click.argument("orgname")
def account_destroy(orgname):
    client = AccountClient()
    click.confirm(
        "Are you sure you want to delete the `%s` organization account?\n"
        "Warning! All linked data will be permanently removed and can not be restored."
        % orgname,
        abort=True,
    )
    client.destroy_org(orgname)
    return click.secho(
        "Organization `%s` has been destroyed." % orgname,
        fg="green",
    )


@cli.command("add", short_help="Add a new owner to organization")
@click.argument(
    "orgname",
)
@click.argument(
    "username",
)
def org_add_owner(orgname, username):
    client = AccountClient()
    client.add_org_owner(orgname, username)
    return click.secho(
        "The new owner `%s` has been successfully added to the `%s` organization."
        % (username, orgname),
        fg="green",
    )


@cli.command("remove", short_help="Remove an owner from organization")
@click.argument(
    "orgname",
)
@click.argument(
    "username",
)
def org_remove_owner(orgname, username):
    client = AccountClient()
    client.remove_org_owner(orgname, username)
    return click.secho(
        "The `%s` owner has been successfully removed from the `%s` organization."
        % (username, orgname),
        fg="green",
    )
