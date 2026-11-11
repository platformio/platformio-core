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

import os

import click

from platformio.package.inventory import collect_project_inventory
from platformio.package.license import normalize_declared_license


def _find_violations(inventory, allowed):
    for package in inventory["packages"]:
        name = package["name"]
        expression = normalize_declared_license(package["license"])
        if expression is None:
            yield f"{name}: no recognized SPDX license declaration"
        elif expression not in allowed:
            yield f"{name}: license {expression} is outside the allowlist"
    for edge in inventory["dependencies"]:
        if edge["to"] is not None:
            continue
        requested = edge["requested"]
        name = requested["name"] or "unnamed dependency"
        yield f"{name}: unresolved {edge['type']} dependency"


@click.command("license-check", short_help="Check declared dependency licenses")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False),
)
@click.option("-e", "--environment", "environments", multiple=True)
@click.option(
    "--allow-license",
    multiple=True,
    required=True,
    help="Accept a complete SPDX expression. Repeat to allow more expressions.",
)
def project_license_check_cmd(project_dir, environments, allow_license):
    allowed = set()
    for value in allow_license:
        expression = normalize_declared_license(value)
        if expression is None:
            raise click.BadParameter(
                "Enter a standard SPDX expression.", param_hint="--allow-license"
            )
        allowed.add(expression)

    inventory = collect_project_inventory(project_dir, environments)
    failed = False
    for env, packages in inventory.items():
        for violation in _find_violations(packages, allowed):
            click.echo(f"[{env}] {violation}", err=True)
            failed = True
    if failed:
        raise click.exceptions.Exit(1)
