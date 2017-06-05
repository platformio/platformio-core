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

import json
import re
from glob import glob
from os.path import isdir, join

import arrow
import click
import semantic_version

from platformio import app, commands, exception, util
from platformio.managers.package import BasePkgManager


class LibraryManager(BasePkgManager):

    def __init__(self, package_dir=None):
        if not package_dir:
            package_dir = join(util.get_home_dir(), "lib")
        BasePkgManager.__init__(self, package_dir)

    @property
    def manifest_names(self):
        return [
            ".library.json", "library.json", "library.properties",
            "module.json"
        ]

    def get_manifest_path(self, pkg_dir):
        path = BasePkgManager.get_manifest_path(self, pkg_dir)
        if path:
            return path

        # if library without manifest, returns first source file
        src_dir = join(util.glob_escape(pkg_dir))
        if isdir(join(pkg_dir, "src")):
            src_dir = join(src_dir, "src")
        chs_files = glob(join(src_dir, "*.[chS]"))
        if chs_files:
            return chs_files[0]
        cpp_files = glob(join(src_dir, "*.cpp"))
        if cpp_files:
            return cpp_files[0]

        return None

    def load_manifest(self, pkg_dir):
        manifest = BasePkgManager.load_manifest(self, pkg_dir)
        if not manifest:
            return manifest

        # if Arduino library.properties
        if "sentence" in manifest:
            manifest['frameworks'] = ["arduino"]
            manifest['description'] = manifest['sentence']
            del manifest['sentence']

        if "author" in manifest:
            manifest['authors'] = [{"name": manifest['author']}]
            del manifest['author']

        if "authors" in manifest and not isinstance(manifest['authors'], list):
            manifest['authors'] = [manifest['authors']]

        if "keywords" not in manifest:
            keywords = []
            for keyword in re.split(r"[\s/]+",
                                    manifest.get("category", "Uncategorized")):
                keyword = keyword.strip()
                if not keyword:
                    continue
                keywords.append(keyword.lower())
            manifest['keywords'] = keywords
            if "category" in manifest:
                del manifest['category']

        # don't replace VCS URL
        if "url" in manifest and "description" in manifest:
            manifest['homepage'] = manifest['url']
            del manifest['url']

        if "architectures" in manifest:
            platforms = []
            platforms_map = {
                "avr": "atmelavr",
                "sam": "atmelsam",
                "samd": "atmelsam",
                "esp8266": "espressif8266",
                "arc32": "intel_arc32"
            }
            for arch in manifest['architectures'].split(","):
                arch = arch.strip()
                if arch == "*":
                    platforms = "*"
                    break
                if arch in platforms_map:
                    platforms.append(platforms_map[arch])
            manifest['platforms'] = platforms
            del manifest['architectures']

        # convert listed items via comma to array
        for key in ("keywords", "frameworks", "platforms"):
            if key not in manifest or \
                    not isinstance(manifest[key], basestring):
                continue
            manifest[key] = [
                i.strip() for i in manifest[key].split(",") if i.strip()
            ]

        return manifest

    @staticmethod
    def normalize_dependencies(dependencies):
        if not dependencies:
            return []
        items = []
        if isinstance(dependencies, dict):
            if "name" in dependencies:
                items.append(dependencies)
            else:
                for name, version in dependencies.items():
                    items.append({"name": name, "version": version})
        elif isinstance(dependencies, list):
            items = [d for d in dependencies if "name" in d]
        for item in items:
            for k in ("frameworks", "platforms"):
                if k not in item or isinstance(k, list):
                    continue
                if item[k] == "*":
                    del item[k]
                elif isinstance(item[k], basestring):
                    item[k] = [
                        i.strip() for i in item[k].split(",") if i.strip()
                    ]
        return items

    @staticmethod
    def max_satisfying_repo_version(versions, requirements=None):

        def _cmp_dates(datestr1, datestr2):
            date1 = arrow.get(datestr1)
            date2 = arrow.get(datestr2)
            if date1 == date2:
                return 0
            return -1 if date1 < date2 else 1

        item = None
        reqspec = None
        if requirements:
            try:
                reqspec = semantic_version.Spec(requirements)
            except ValueError:
                pass
        for v in versions:
            specver = None
            try:
                specver = semantic_version.Version(v['name'], partial=True)
            except ValueError:
                pass

            if reqspec:
                if not specver or specver not in reqspec:
                    continue
                if not item or semantic_version.Version(
                        item['name'], partial=True) < specver:
                    item = v
            elif requirements:
                if requirements == v['name']:
                    return v
            else:
                if not item or _cmp_dates(item['released'],
                                          v['released']) == -1:
                    item = v
        return item

    def get_latest_repo_version(self, name, requirements, silent=False):
        item = self.max_satisfying_repo_version(
            util.get_api_result(
                "/lib/info/%d" % self.get_pkg_id_by_name(
                    name, requirements, silent=silent),
                cache_valid="1d")['versions'], requirements)
        return item['name'] if item else None

    def get_pkg_id_by_name(self,
                           name,
                           requirements,
                           silent=False,
                           interactive=False):
        if name.startswith("id="):
            return int(name[3:])
        # try to find ID from installed packages
        package_dir = self.get_package_dir(name, requirements)
        if package_dir:
            manifest = self.load_manifest(package_dir)
            if "id" in manifest:
                return int(manifest['id'])
        return int(
            self.search_for_library({
                "name": name
            }, silent, interactive)['id'])

    def _install_from_piorepo(self, name, requirements):
        assert name.startswith("id="), name
        version = self.get_latest_repo_version(name, requirements)
        if not version:
            raise exception.UndefinedPackageVersion(requirements or "latest",
                                                    util.get_systype())
        dl_data = util.get_api_result(
            "/lib/download/" + str(name[3:]),
            dict(version=version),
            cache_valid="30d")
        assert dl_data

        return self._install_from_url(name, dl_data['url'].replace(
            "http://", "https://") if app.get_setting("enable_ssl") else
                                      dl_data['url'], requirements)

    def install(  # pylint: disable=arguments-differ
            self,
            name,
            requirements=None,
            silent=False,
            trigger_event=True,
            interactive=False):
        pkg_dir = None
        try:
            _name, _requirements, _url = self.parse_pkg_input(
                name, requirements)
            if not _url:
                name = "id=%d" % self.get_pkg_id_by_name(
                    _name,
                    _requirements,
                    silent=silent,
                    interactive=interactive)
                requirements = _requirements
            pkg_dir = BasePkgManager.install(self, name, requirements, silent,
                                             trigger_event)
        except exception.InternetIsOffline as e:
            if not silent:
                click.secho(str(e), fg="yellow")
            return

        if not pkg_dir:
            return

        manifest = self.load_manifest(pkg_dir)
        if "dependencies" not in manifest:
            return pkg_dir

        if not silent:
            click.secho("Installing dependencies", fg="yellow")

        for filters in self.normalize_dependencies(manifest['dependencies']):
            assert "name" in filters
            if any([s in filters.get("version", "") for s in ("\\", "/")]):
                self.install("{name}={version}".format(**filters))
            else:
                try:
                    lib_info = self.search_for_library(filters, silent,
                                                       interactive)
                except exception.LibNotFound as e:
                    if not silent:
                        click.secho("Warning! %s" % e, fg="yellow")
                    continue

                if filters.get("version"):
                    self.install(
                        lib_info['id'],
                        requirements=filters.get("version"),
                        silent=silent,
                        trigger_event=trigger_event)
                else:
                    self.install(
                        lib_info['id'],
                        silent=silent,
                        trigger_event=trigger_event)
        return pkg_dir

    @staticmethod
    def search_for_library(  # pylint: disable=too-many-branches
            filters,
            silent=False,
            interactive=False):
        assert isinstance(filters, dict)
        assert "name" in filters
        if not silent:
            click.echo("Looking for %s library in registry" % click.style(
                filters['name'], fg="cyan"))
        query = []
        for key in filters:
            if key not in ("name", "authors", "frameworks", "platforms"):
                continue
            values = filters[key]
            if not isinstance(values, list):
                values = [v.strip() for v in values.split(",") if v]
            for value in values:
                query.append('%s:"%s"' % (key[:-1]
                                          if key.endswith("s") else key,
                                          value))

        lib_info = None
        result = util.get_api_result(
            "/v2/lib/search", dict(query=" ".join(query)), cache_valid="3d")
        if result['total'] == 1:
            lib_info = result['items'][0]
        elif result['total'] > 1:
            if silent and not interactive:
                lib_info = result['items'][0]
            else:
                click.secho(
                    "Conflict: More than one library has been found "
                    "by request %s:" % json.dumps(filters),
                    fg="yellow",
                    err=True)
                for item in result['items']:
                    commands.lib.print_lib_item(item)

                if not interactive:
                    click.secho(
                        "Automatically chose the first available library "
                        "(use `--interactive` option to make a choice)",
                        fg="yellow",
                        err=True)
                    lib_info = result['items'][0]
                else:
                    deplib_id = click.prompt(
                        "Please choose library ID",
                        type=click.Choice(
                            [str(i['id']) for i in result['items']]))
                    for item in result['items']:
                        if item['id'] == int(deplib_id):
                            lib_info = item
                            break

        if not lib_info:
            if filters.keys() == ["name"]:
                raise exception.LibNotFound(filters['name'])
            else:
                raise exception.LibNotFound(str(filters))
        if not silent:
            click.echo("Found: %s" % click.style(
                "http://platformio.org/lib/show/{id}/{name}".format(
                    **lib_info),
                fg="blue"))
        return lib_info
