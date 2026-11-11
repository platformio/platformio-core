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
import os
from datetime import datetime, timezone
from uuid import uuid4

import click

from platformio import __version__, fs
from platformio.package.inventory import collect_project_inventory
from platformio.package.license import normalize_declared_license
from platformio.project.config import ProjectConfig


def _package(spdx_id, name, version=None, license_expression=None):
    result = {
        "SPDXID": spdx_id,
        "name": name,
        "downloadLocation": "NOASSERTION",
        "filesAnalyzed": False,
        "licenseConcluded": "NOASSERTION",
        "licenseDeclared": normalize_declared_license(license_expression)
        or "NOASSERTION",
        "copyrightText": "NOASSERTION",
    }
    if version is not None:
        result["versionInfo"] = version
    return result


def _relationship(source, kind, target):
    return {
        "spdxElementId": source,
        "relationshipType": kind,
        "relatedSpdxElement": target,
    }


def _spdx_document(name, inventory):
    project_id = "SPDXRef-Project"
    document_id = "SPDXRef-DOCUMENT"
    packages = [_package(project_id, name)]
    package_ids = {None: project_id}
    for item in inventory["packages"]:
        package_id = f"SPDXRef-Package-{item['id']}"
        package_ids[item["id"]] = package_id
        packages.append(
            _package(package_id, item["name"], item["version"], item["license"])
        )
    relationships = [_relationship(document_id, "DESCRIBES", project_id)]
    edges = dict.fromkeys(
        (edge["from"], edge["to"])
        for edge in inventory["dependencies"]
        if edge["to"] is not None
    )
    relationships.extend(
        _relationship(package_ids[source], "DEPENDS_ON", package_ids[target])
        for source, target in edges
    )
    unresolved = sum(edge["to"] is None for edge in inventory["dependencies"])
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": document_id,
        "name": name,
        "documentNamespace": f"https://platformio.org/spdx/{uuid4()}",
        "creationInfo": {
            "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "creators": [f"Tool: PlatformIO Core {__version__}"],
        },
        "comment": (
            f"Declared package inventory with {unresolved} unresolved dependencies. "
            "Source-discovered libraries are outside this inventory."
        ),
        "packages": packages,
        "relationships": relationships,
    }


@click.command("sbom", short_help="Export the project's declared packages as SPDX")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False),
)
@click.option("-e", "--environment")
@click.option(
    "--standard", type=click.Choice(["spdx"]), default="spdx", expose_value=False
)
@click.option(
    "--format", type=click.Choice(["json"]), default="json", expose_value=False
)
def project_sbom_cmd(project_dir, environment):
    if environment is None:
        with fs.cd(project_dir):
            config = ProjectConfig.get_instance()
            config.validate(silent=True)
            environments = config.envs()
        if len(environments) != 1:
            raise click.UsageError("Select one project environment with --environment.")
        environment = environments[0]
    inventory = collect_project_inventory(project_dir, [environment])[environment]
    name = f"{os.path.basename(os.path.abspath(project_dir))}-{environment}"
    click.echo(json.dumps(_spdx_document(name, inventory), indent=2))
