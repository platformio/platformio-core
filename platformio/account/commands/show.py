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
from tabulate import tabulate

from platformio import util
from platformio.account.client import AccountClient


@click.command("show", short_help="PlatformIO Account information")
@click.option("--offline", is_flag=True)
@click.option("--json-output", is_flag=True)
def account_show_cmd(offline, json_output):
    client = AccountClient()
    info = client.get_account_info(offline)
    if json_output:
        click.echo(json.dumps(info))
        return
    click.echo()
    if info.get("profile"):
        print_profile(info["profile"])
    if info.get("packages"):
        print_packages(info["packages"])
    if info.get("subscriptions"):
        print_subscriptions(info["subscriptions"])
    click.echo()


def print_profile(profile):
    click.secho("Profile", fg="cyan", bold=True)
    click.echo("=" * len("Profile"))
    data = []
    if profile.get("username"):
        data.append(("Username:", profile["username"]))
    if profile.get("email"):
        data.append(("Email:", profile["email"]))
    if profile.get("firstname"):
        data.append(("First name:", profile["firstname"]))
    if profile.get("lastname"):
        data.append(("Last name:", profile["lastname"]))
    click.echo(tabulate(data, tablefmt="plain"))


def print_packages(packages):
    click.echo()
    click.secho("Packages", fg="cyan")
    click.echo("=" * len("Packages"))
    for package in packages:
        click.echo()
        click.secho(package.get("name"), bold=True)
        click.echo("-" * len(package.get("name")))
        if package.get("description"):
            click.echo(package.get("description"))
        data = []
        expire = "-"
        if "subscription" in package:
            expire = util.parse_datetime(
                package["subscription"].get("end_at")
                or package["subscription"].get("next_bill_at")
            ).strftime("%Y-%m-%d")
        data.append(("Expire:", expire))
        services = []
        for key in package:
            if not key.startswith("service."):
                continue
            if isinstance(package[key], dict):
                services.append(package[key].get("title"))
            else:
                services.append(package[key])
        if services:
            data.append(("Services:", ", ".join(services)))
        click.echo(tabulate(data, tablefmt="plain"))


def print_subscriptions(subscriptions):
    click.echo()
    click.secho("Subscriptions", fg="cyan")
    click.echo("=" * len("Subscriptions"))
    for subscription in subscriptions:
        click.echo()
        click.secho(subscription.get("product_name"), bold=True)
        click.echo("-" * len(subscription.get("product_name")))
        data = [("State:", subscription.get("status"))]
        begin_at = util.parse_datetime(subscription.get("begin_at")).strftime("%c")
        data.append(("Start date:", begin_at or "-"))
        end_at = subscription.get("end_at")
        if end_at:
            end_at = util.parse_datetime(subscription.get("end_at")).strftime("%c")
        data.append(("End date:", end_at or "-"))
        next_bill_at = subscription.get("next_bill_at")
        if next_bill_at:
            next_bill_at = util.parse_datetime(
                subscription.get("next_bill_at")
            ).strftime("%c")
        data.append(("Next payment:", next_bill_at or "-"))
        data.append(
            ("Edit:", click.style(subscription.get("update_url"), fg="blue") or "-")
        )
        data.append(
            ("Cancel:", click.style(subscription.get("cancel_url"), fg="blue") or "-")
        )
        click.echo(tabulate(data, tablefmt="plain"))
