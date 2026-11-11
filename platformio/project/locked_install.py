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
import logging
import os
import shutil
import tempfile
from pathlib import Path

from semantic_version import Version

from platformio import fs, util
from platformio.exception import UserSideException
from platformio.package.inventory import collect_project_inventory
from platformio.package.meta import PackageSpec, PackageType
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig
from platformio.project.dependency_lock import (
    LOCK_FILENAME,
    LOCK_VERSION,
    SHA256_RE,
    artifact_checksum,
    environment_fingerprint,
    package_managers,
    registry_artifact,
)
from platformio.registry.mirror import RegistryFileMirrorIterator


def _valid_registry_name(value):
    return (
        isinstance(value, str)
        and bool(value.strip())
        and value not in (".", "..")
        and all(char.isprintable() and char not in "/\\?#%" for char in value)
    )


def _validate_pin(pin):
    try:
        valid = all(
            (
                pin["type"]
                in (PackageType.PLATFORM, PackageType.TOOL, PackageType.LIBRARY),
                isinstance(pin["id"], int)
                and not isinstance(pin["id"], bool)
                and pin["id"] > 0,
                _valid_registry_name(pin["owner"]),
                _valid_registry_name(pin["name"]),
                str(Version(pin["version"])) == pin["version"],
                bool(SHA256_RE.fullmatch(pin["sha256"])),
            )
        )
    except (KeyError, TypeError, ValueError):
        valid = False
    if not valid:
        raise UserSideException("Invalid package entry in platformio.lock.")


def _read_selected_lock(config, environments):
    try:
        with open(LOCK_FILENAME, encoding="utf8") as stream:
            lock = json.load(stream)
    except (OSError, UnicodeError, ValueError) as exc:
        raise UserSideException(f"Could not read {LOCK_FILENAME}: {exc}") from exc
    if not isinstance(lock, dict) or lock.get("version") != LOCK_VERSION:
        raise UserSideException(f"Unsupported {LOCK_FILENAME} format.")
    if lock.get("system") != util.get_systype():
        raise UserSideException(
            f"{LOCK_FILENAME} was generated for a different system."
        )
    entries = lock.get("environments")
    if not isinstance(entries, dict):
        raise UserSideException(f"Invalid environments in {LOCK_FILENAME}.")
    selected = {}
    for env in environments or config.envs():
        entry = entries.get(env)
        if not isinstance(entry, dict):
            raise UserSideException(f"{LOCK_FILENAME} has no entry for {env!r}.")
        if entry.get("config_sha256") != environment_fingerprint(config, env):
            raise UserSideException(
                f"{LOCK_FILENAME} is stale for environment {env!r}."
            )
        pins = entry.get("packages")
        if not isinstance(pins, list):
            raise UserSideException(f"Invalid packages in {LOCK_FILENAME} for {env!r}.")
        for pin in pins:
            _validate_pin(pin)
        selected[env] = pins
    return selected


def _stage_archive(manager, pin, destination):
    artifact = registry_artifact(manager, pin)
    checksum = pin["sha256"]
    if artifact_checksum(artifact) != checksum:
        raise UserSideException(f"Registry archive checksum changed for {pin['name']}.")
    for url, _ in RegistryFileMirrorIterator(artifact["download_url"]):
        # Copy the cached archive before checking it and passing it to the unpacker.
        shutil.copyfile(manager.download(url, checksum), destination)
        if fs.calculate_file_hashsum("sha256", destination) == checksum:
            return
    raise UserSideException(
        f"Could not verify the locked archive checksum for {pin['name']}."
    )


def _install_archive(manager, pin, archive):
    spec = PackageSpec(
        id=pin["id"],
        owner=pin["owner"],
        name=pin["name"],
        requirements=f"=={pin['version']}",
    )
    manager.lock()
    try:
        installed = manager.install_from_uri(f"file://{archive}", spec)
        manager.memcache_reset()
        manager.call_pkg_script(installed, "postinstall")
        if pin["type"] == PackageType.PLATFORM:
            platform = PlatformFactory.new(installed)
            platform.ensure_engine_compatible()
            return platform
        return None
    finally:
        manager.unlock()


def _package_identity(package, id_field):
    return package["type"], package[id_field], package["version"]


def _verify_selection(project_dir, selections):
    inventory = collect_project_inventory(project_dir, list(selections))
    for env, pins in selections.items():
        selected = inventory[env]
        expected = {_package_identity(pin, "id") for pin in pins}
        actual = {
            _package_identity(package, "registry_id")
            for package in selected["packages"]
        }
        if expected != actual or any(
            edge["to"] is None for edge in selected["dependencies"]
        ):
            raise UserSideException(
                f"Environment {env!r} resolves packages outside {LOCK_FILENAME}. "
                "Check for conflicting installed packages and refresh the lock if needed."
            )


def _prepare_installs(config, selections, tmp, silent):
    archives = {}
    installs = {}
    for env, pins in selections.items():
        managers = package_managers(config, env)
        for pin in pins:
            manager = managers[pin["type"]]
            if silent:
                manager.set_log_level(logging.WARN)
            key = (*_package_identity(pin, "id"), pin["sha256"])
            if key not in archives:
                archive = Path(tmp) / str(len(archives))
                _stage_archive(manager, pin, archive)
                archives[key] = archive
            installs.setdefault(
                (manager.package_dir, key), (manager, pin, archives[key], env)
            )
    return installs.values()


def install_locked_packages(project_dir, environments, silent=False):
    with fs.cd(project_dir), tempfile.TemporaryDirectory(prefix="pio-locked-") as tmp:
        config = ProjectConfig.get_instance()
        config.validate(environments)
        selections = _read_selected_lock(config, environments)
        installs = _prepare_installs(config, selections, tmp, silent)
        platforms = []
        for manager, pin, archive, env in installs:
            platform = _install_archive(manager, pin, archive)
            if platform is not None:
                platforms.append((platform, env))
        for platform, env in platforms:
            platform.configure_project_packages(env)
            platform.on_installed()
        _verify_selection(os.getcwd(), selections)
