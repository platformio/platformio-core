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

import hashlib
import json
import os
import re

from platformio import fs, util
from platformio.exception import UserSideException
from platformio.package.inventory import collect_project_inventory
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageSpec, PackageType
from platformio.package.version import cast_version_to_semver
from platformio.project.config import ProjectConfig

LOCK_FILENAME = "platformio.lock"
LOCK_VERSION = 1
SHA256_RE = re.compile(r"[0-9a-f]{64}")


def environment_fingerprint(config, env):
    options = config.items(env=env, as_dict=True)
    encoded = json.dumps(options, sort_keys=True, separators=(",", ":")).encode("utf8")
    return hashlib.sha256(encoded).hexdigest()


def registry_artifact(manager, package):
    spec = PackageSpec(owner=package["owner"], name=package["name"])
    release = manager.fetch_registry_package(spec)
    if release["id"] != package["id"]:
        raise UserSideException(f"Registry identity changed for {spec.humanize()}.")
    for version in release.get("versions", ()):
        if str(cast_version_to_semver(version["name"])) != package["version"]:
            continue
        artifact = manager.pick_compatible_pkg_file(version["files"])
        if artifact is not None:
            return artifact
    raise UserSideException(
        f"No compatible registry archive for {spec.humanize()}@{package['version']}."
    )


def artifact_checksum(artifact):
    checksum = (artifact.get("checksum") or {}).get("sha256", "")
    if not isinstance(checksum, str) or not SHA256_RE.fullmatch(checksum):
        raise UserSideException("The registry archive has no valid SHA-256 checksum.")
    return checksum


def package_managers(config, env):
    return {
        PackageType.PLATFORM: PlatformPackageManager(),
        PackageType.TOOL: ToolPackageManager(),
        PackageType.LIBRARY: LibraryPackageManager(
            os.path.join(config.get("platformio", "libdeps_dir"), env)
        ),
    }


def _environment_lock(config, env, inventory):
    if any(edge["to"] is None for edge in inventory["dependencies"]):
        raise UserSideException(f"Environment {env!r} has unresolved dependencies.")
    if any(edge["requested"]["external"] for edge in inventory["dependencies"]):
        raise UserSideException(f"Environment {env!r} has non-registry dependencies.")

    managers = package_managers(config, env)
    packages = []
    for item in inventory["packages"]:
        if not item["registry_id"] or not item["owner"]:
            raise UserSideException(
                f"{item['name']} in {env!r} has no installed registry identity."
            )
        package = {
            "type": item["type"],
            "id": item["registry_id"],
            "owner": item["owner"],
            "name": item["name"],
            "version": item["version"],
        }
        artifact = registry_artifact(managers[item["type"]], package)
        package["sha256"] = artifact_checksum(artifact)
        packages.append(package)
    return {
        "config_sha256": environment_fingerprint(config, env),
        "packages": sorted(
            packages, key=lambda item: (item["type"], item["id"], item["version"])
        ),
    }


def generate_project_lock(project_dir, environments):
    with fs.cd(project_dir):
        config = ProjectConfig.get_instance()
        inventory = collect_project_inventory(os.getcwd(), environments)
        return {
            "version": LOCK_VERSION,
            "system": util.get_systype(),
            "environments": {
                env: _environment_lock(config, env, items)
                for env, items in inventory.items()
            },
        }
