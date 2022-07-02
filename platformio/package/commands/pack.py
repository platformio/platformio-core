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

from platformio.package.manifest.parser import ManifestParserFactory
from platformio.package.manifest.schema import ManifestSchema, ManifestValidationError
from platformio.package.pack import PackagePacker


@click.command("pack", short_help="Create a tarball from a package")
@click.argument(
    "package",
    default=os.getcwd,
    metavar="<source directory, tar.gz or zip>",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, resolve_path=True),
)
@click.option(
    "-o", "--output", help="A destination path (folder or a full path to file)"
)
def package_pack_cmd(package, output):
    p = PackagePacker(package)
    archive_path = p.pack(output)
    # validate manifest
    try:
        ManifestSchema().load_manifest(
            ManifestParserFactory.new_from_archive(archive_path).as_dict()
        )
    except ManifestValidationError as exc:
        os.remove(archive_path)
        raise exc
    click.secho('Wrote a tarball to "%s"' % archive_path, fg="green")
