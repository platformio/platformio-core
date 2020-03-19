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

# pylint: disable=too-many-arguments, too-many-locals, too-many-branches
# pylint: disable=too-many-return-statements

import json
from glob import glob
from os.path import isdir, join

import click
import semantic_version

from platformio import app, exception, util
from platformio.compat import glob_escape
from platformio.managers.package import BasePkgManager
from platformio.managers.platform import PlatformFactory, PlatformManager
from platformio.package.exception import ManifestException
from platformio.package.manifest.parser import ManifestParserFactory
from platformio.project.config import ProjectConfig


class LibraryManager(BasePkgManager):

    FILE_CACHE_VALID = "30d"  # 1 month

    def __init__(self, package_dir=None):
        self.config = ProjectConfig.get_instance()
        super(LibraryManager, self).__init__(
            package_dir or self.config.get_optional_dir("globallib")
        )

    @property
    def manifest_names(self):
        return [".library.json", "library.json", "library.properties", "module.json"]

    def get_manifest_path(self, pkg_dir):
        path = BasePkgManager.get_manifest_path(self, pkg_dir)
        if path:
            return path

        # if library without manifest, returns first source file
        src_dir = join(glob_escape(pkg_dir))
        if isdir(join(pkg_dir, "src")):
            src_dir = join(src_dir, "src")
        chs_files = glob(join(src_dir, "*.[chS]"))
        if chs_files:
            return chs_files[0]
        cpp_files = glob(join(src_dir, "*.cpp"))
        if cpp_files:
            return cpp_files[0]

        return None

    def max_satisfying_repo_version(self, versions, requirements=None):
        def _cmp_dates(datestr1, datestr2):
            date1 = util.parse_date(datestr1)
            date2 = util.parse_date(datestr2)
            if date1 == date2:
                return 0
            return -1 if date1 < date2 else 1

        semver_spec = None
        try:
            semver_spec = (
                semantic_version.SimpleSpec(requirements) if requirements else None
            )
        except ValueError:
            pass

        item = {}

        for v in versions:
            semver_new = self.parse_semver_version(v["name"])
            if semver_spec:
                if not semver_new or semver_new not in semver_spec:
                    continue
                if not item or self.parse_semver_version(item["name"]) < semver_new:
                    item = v
            elif requirements:
                if requirements == v["name"]:
                    return v

            else:
                if not item or _cmp_dates(item["released"], v["released"]) == -1:
                    item = v
        return item

    def get_latest_repo_version(self, name, requirements, silent=False):
        item = self.max_satisfying_repo_version(
            util.get_api_result(
                "/lib/info/%d"
                % self.search_lib_id(
                    {"name": name, "requirements": requirements}, silent=silent
                ),
                cache_valid="1h",
            )["versions"],
            requirements,
        )
        return item["name"] if item else None

    def _install_from_piorepo(self, name, requirements):
        assert name.startswith("id="), name
        version = self.get_latest_repo_version(name, requirements)
        if not version:
            raise exception.UndefinedPackageVersion(
                requirements or "latest", util.get_systype()
            )
        dl_data = util.get_api_result(
            "/lib/download/" + str(name[3:]), dict(version=version), cache_valid="30d"
        )
        assert dl_data

        return self._install_from_url(
            name,
            dl_data["url"].replace("http://", "https://")
            if app.get_setting("strict_ssl")
            else dl_data["url"],
            requirements,
        )

    def search_lib_id(  # pylint: disable=too-many-branches
        self, filters, silent=False, interactive=False
    ):
        assert isinstance(filters, dict)
        assert "name" in filters

        # try to find ID within installed packages
        lib_id = self._get_lib_id_from_installed(filters)
        if lib_id:
            return lib_id

        # looking in PIO Library Registry
        if not silent:
            click.echo(
                "Looking for %s library in registry"
                % click.style(filters["name"], fg="cyan")
            )
        query = []
        for key in filters:
            if key not in ("name", "authors", "frameworks", "platforms"):
                continue
            values = filters[key]
            if not isinstance(values, list):
                values = [v.strip() for v in values.split(",") if v]
            for value in values:
                query.append(
                    '%s:"%s"' % (key[:-1] if key.endswith("s") else key, value)
                )

        lib_info = None
        result = util.get_api_result(
            "/v2/lib/search", dict(query=" ".join(query)), cache_valid="1h"
        )
        if result["total"] == 1:
            lib_info = result["items"][0]
        elif result["total"] > 1:
            if silent and not interactive:
                lib_info = result["items"][0]
            else:
                click.secho(
                    "Conflict: More than one library has been found "
                    "by request %s:" % json.dumps(filters),
                    fg="yellow",
                    err=True,
                )
                # pylint: disable=import-outside-toplevel
                from platformio.commands.lib import print_lib_item

                for item in result["items"]:
                    print_lib_item(item)

                if not interactive:
                    click.secho(
                        "Automatically chose the first available library "
                        "(use `--interactive` option to make a choice)",
                        fg="yellow",
                        err=True,
                    )
                    lib_info = result["items"][0]
                else:
                    deplib_id = click.prompt(
                        "Please choose library ID",
                        type=click.Choice([str(i["id"]) for i in result["items"]]),
                    )
                    for item in result["items"]:
                        if item["id"] == int(deplib_id):
                            lib_info = item
                            break

        if not lib_info:
            if list(filters) == ["name"]:
                raise exception.LibNotFound(filters["name"])
            raise exception.LibNotFound(str(filters))
        if not silent:
            click.echo(
                "Found: %s"
                % click.style(
                    "https://platformio.org/lib/show/{id}/{name}".format(**lib_info),
                    fg="blue",
                )
            )
        return int(lib_info["id"])

    def _get_lib_id_from_installed(self, filters):
        if filters["name"].startswith("id="):
            return int(filters["name"][3:])
        package_dir = self.get_package_dir(
            filters["name"], filters.get("requirements", filters.get("version"))
        )
        if not package_dir:
            return None
        manifest = self.load_manifest(package_dir)
        if "id" not in manifest:
            return None

        for key in ("frameworks", "platforms"):
            if key not in filters:
                continue
            if key not in manifest:
                return None
            if not util.items_in_list(
                util.items_to_list(filters[key]), util.items_to_list(manifest[key])
            ):
                return None

        if "authors" in filters:
            if "authors" not in manifest:
                return None
            manifest_authors = manifest["authors"]
            if not isinstance(manifest_authors, list):
                manifest_authors = [manifest_authors]
            manifest_authors = [
                a["name"]
                for a in manifest_authors
                if isinstance(a, dict) and "name" in a
            ]
            filter_authors = filters["authors"]
            if not isinstance(filter_authors, list):
                filter_authors = [filter_authors]
            if not set(filter_authors) <= set(manifest_authors):
                return None

        return int(manifest["id"])

    def install(  # pylint: disable=arguments-differ
        self,
        name,
        requirements=None,
        silent=False,
        after_update=False,
        interactive=False,
        force=False,
    ):
        _name, _requirements, _url = self.parse_pkg_uri(name, requirements)
        if not _url:
            name = "id=%d" % self.search_lib_id(
                {"name": _name, "requirements": _requirements},
                silent=silent,
                interactive=interactive,
            )
            requirements = _requirements
        pkg_dir = BasePkgManager.install(
            self,
            name,
            requirements,
            silent=silent,
            after_update=after_update,
            force=force,
        )

        if not pkg_dir:
            return None

        manifest = None
        try:
            manifest = ManifestParserFactory.new_from_dir(pkg_dir).as_dict()
        except ManifestException:
            pass
        if not manifest or not manifest.get("dependencies"):
            return pkg_dir

        if not silent:
            click.secho("Installing dependencies", fg="yellow")

        builtin_lib_storages = None
        for filters in manifest["dependencies"]:
            assert "name" in filters

            # avoid circle dependencies
            if not self.INSTALL_HISTORY:
                self.INSTALL_HISTORY = []
            history_key = str(filters)
            if history_key in self.INSTALL_HISTORY:
                continue
            self.INSTALL_HISTORY.append(history_key)

            if any(s in filters.get("version", "") for s in ("\\", "/")):
                self.install(
                    "{name}={version}".format(**filters),
                    silent=silent,
                    after_update=after_update,
                    interactive=interactive,
                    force=force,
                )
            else:
                try:
                    lib_id = self.search_lib_id(filters, silent, interactive)
                except exception.LibNotFound as e:
                    if builtin_lib_storages is None:
                        builtin_lib_storages = get_builtin_libs()
                    if not silent or is_builtin_lib(
                        builtin_lib_storages, filters["name"]
                    ):
                        click.secho("Warning! %s" % e, fg="yellow")
                    continue

                if filters.get("version"):
                    self.install(
                        lib_id,
                        filters.get("version"),
                        silent=silent,
                        after_update=after_update,
                        interactive=interactive,
                        force=force,
                    )
                else:
                    self.install(
                        lib_id,
                        silent=silent,
                        after_update=after_update,
                        interactive=interactive,
                        force=force,
                    )
        return pkg_dir


def get_builtin_libs(storage_names=None):
    items = []
    storage_names = storage_names or []
    pm = PlatformManager()
    for manifest in pm.get_installed():
        p = PlatformFactory.newPlatform(manifest["__pkg_dir"])
        for storage in p.get_lib_storages():
            if storage_names and storage["name"] not in storage_names:
                continue
            lm = LibraryManager(storage["path"])
            items.append(
                {
                    "name": storage["name"],
                    "path": storage["path"],
                    "items": lm.get_installed(),
                }
            )
    return items


def is_builtin_lib(storages, name):
    for storage in storages or []:
        if any(l.get("name") == name for l in storage["items"]):
            return True
    return False
