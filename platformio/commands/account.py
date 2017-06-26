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

import sys

import click

from platformio.managers.core import pioplus_call


@click.group("account", short_help="Manage PIO Account")
def cli():
    pass


@cli.command("register", short_help="Create new PIO Account")
@click.option("-u", "--username")
def account_register(**kwargs):
    pioplus_call(sys.argv[1:])


@cli.command("login", short_help="Log in to PIO Account")
@click.option("-u", "--username")
@click.option("-p", "--password")
def account_login(**kwargs):
    pioplus_call(sys.argv[1:])


@cli.command("logout", short_help="Log out of PIO Account")
def account_logout():
    pioplus_call(sys.argv[1:])


@cli.command("password", short_help="Change password")
@click.option("--old-password")
@click.option("--new-password")
def account_password(**kwargs):
    pioplus_call(sys.argv[1:])


@cli.command("token", short_help="Get or regenerate Authentication Token")
@click.option("-p", "--password")
@click.option("--regenerate", is_flag=True)
@click.option("--json-output", is_flag=True)
def account_token(**kwargs):
    pioplus_call(sys.argv[1:])


@cli.command("forgot", short_help="Forgot password")
@click.option("-u", "--username")
def account_forgot(**kwargs):
    pioplus_call(sys.argv[1:])


@cli.command("show", short_help="PIO Account information")
@click.option("--offline", is_flag=True)
@click.option("--json-output", is_flag=True)
def account_show(**kwargs):
    pioplus_call(sys.argv[1:])
