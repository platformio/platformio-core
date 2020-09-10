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

import click
from tabulate import tabulate

from platformio.clients.account import AccountClient


def validate_orgname_teamname(value, teamname_validate=False):
    if ":" not in value:
        raise click.BadParameter(
            "Please specify organization and team name in the next"
            " format - orgname:teamname. For example, mycompany:DreamTeam"
        )
    teamname = str(value.strip().split(":", 1)[1])
    if teamname_validate:
        validate_teamname(teamname)
    return value


def validate_teamname(value):
    if not value:
        return value
    value = str(value).strip()
    if not re.match(r"^[a-z\d](?:[a-z\d]|[\-_ ](?=[a-z\d])){0,19}$", value, flags=re.I):
        raise click.BadParameter(
            "Invalid team name format. "
            "Team name must only contain alphanumeric characters, "
            "single hyphens, underscores, spaces. It can not "
            "begin or end with a hyphen or a underscore and must"
            " not be longer than 20 characters."
        )
    return value


@click.group("team", short_help="Manage organization teams")
def cli():
    pass


@cli.command("create", short_help="Create a new team")
@click.argument(
    "orgname_teamname",
    metavar="ORGNAME:TEAMNAME",
    callback=lambda _, __, value: validate_orgname_teamname(
        value, teamname_validate=True
    ),
)
@click.option(
    "--description",
)
def team_create(orgname_teamname, description):
    orgname, teamname = orgname_teamname.split(":", 1)
    client = AccountClient()
    client.create_team(orgname, teamname, description)
    return click.secho(
        "The team %s has been successfully created." % teamname,
        fg="green",
    )


@cli.command("list", short_help="List teams")
@click.argument("orgname", required=False)
@click.option("--json-output", is_flag=True)
def team_list(orgname, json_output):
    client = AccountClient()
    data = {}
    if not orgname:
        for item in client.list_orgs():
            teams = client.list_teams(item.get("orgname"))
            data[item.get("orgname")] = teams
    else:
        teams = client.list_teams(orgname)
        data[orgname] = teams
    if json_output:
        return click.echo(json.dumps(data[orgname] if orgname else data))
    if not any(data.values()):
        return click.secho("You do not have any teams.", fg="yellow")
    for org_name in data:
        for team in data[org_name]:
            click.echo()
            click.secho("%s:%s" % (org_name, team.get("name")), fg="cyan")
            click.echo("-" * len("%s:%s" % (org_name, team.get("name"))))
            table_data = []
            if team.get("description"):
                table_data.append(("Description:", team.get("description")))
            table_data.append(
                (
                    "Members:",
                    ", ".join(
                        (member.get("username") for member in team.get("members"))
                    )
                    if team.get("members")
                    else "-",
                )
            )
            click.echo(tabulate(table_data, tablefmt="plain"))
    return click.echo()


@cli.command("update", short_help="Update team")
@click.argument(
    "orgname_teamname",
    metavar="ORGNAME:TEAMNAME",
    callback=lambda _, __, value: validate_orgname_teamname(value),
)
@click.option(
    "--name",
    callback=lambda _, __, value: validate_teamname(value),
    help="A new team name",
)
@click.option(
    "--description",
)
def team_update(orgname_teamname, **kwargs):
    orgname, teamname = orgname_teamname.split(":", 1)
    client = AccountClient()
    team = client.get_team(orgname, teamname)
    del team["id"]
    del team["members"]
    new_team = team.copy()
    if not any(kwargs.values()):
        for field in team:
            new_team[field] = click.prompt(
                field.replace("_", " ").capitalize(), default=team[field]
            )
            if field == "name":
                validate_teamname(new_team[field])
    else:
        new_team.update({key: value for key, value in kwargs.items() if value})
    client.update_team(orgname, teamname, new_team)
    return click.secho(
        "The team %s has been successfully updated." % teamname,
        fg="green",
    )


@cli.command("destroy", short_help="Destroy a team")
@click.argument(
    "orgname_teamname",
    metavar="ORGNAME:TEAMNAME",
    callback=lambda _, __, value: validate_orgname_teamname(value),
)
def team_destroy(orgname_teamname):
    orgname, teamname = orgname_teamname.split(":", 1)
    click.confirm(
        click.style(
            "Are you sure you want to destroy the %s team?" % teamname, fg="yellow"
        ),
        abort=True,
    )
    client = AccountClient()
    client.destroy_team(orgname, teamname)
    return click.secho(
        "The team %s has been successfully destroyed." % teamname,
        fg="green",
    )


@cli.command("add", short_help="Add a new member to team")
@click.argument(
    "orgname_teamname",
    metavar="ORGNAME:TEAMNAME",
    callback=lambda _, __, value: validate_orgname_teamname(value),
)
@click.argument(
    "username",
)
def team_add_member(orgname_teamname, username):
    orgname, teamname = orgname_teamname.split(":", 1)
    client = AccountClient()
    client.add_team_member(orgname, teamname, username)
    return click.secho(
        "The new member %s has been successfully added to the %s team."
        % (username, teamname),
        fg="green",
    )


@cli.command("remove", short_help="Remove a member from team")
@click.argument(
    "orgname_teamname",
    metavar="ORGNAME:TEAMNAME",
    callback=lambda _, __, value: validate_orgname_teamname(value),
)
@click.argument("username")
def team_remove_owner(orgname_teamname, username):
    orgname, teamname = orgname_teamname.split(":", 1)
    client = AccountClient()
    client.remove_team_member(orgname, teamname, username)
    return click.secho(
        "The %s member has been successfully removed from the %s team."
        % (username, teamname),
        fg="green",
    )
