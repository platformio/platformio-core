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

from platformio.project.commands.metadata import project_metadata_cmd


def test_metadata_dump(clirunner, validate_cliresult, tmpdir):
    tmpdir.join("platformio.ini").write(
        """
[env:native]
platform = native
"""
    )

    component_dir = tmpdir.mkdir("lib").mkdir("component")
    component_dir.join("library.json").write(
        """
{
    "name": "component",
    "version": "1.0.0"
}
    """
    )
    component_dir.mkdir("include").join("component.h").write(
        """
#define I_AM_COMPONENT

void dummy(void);
    """
    )
    component_dir.mkdir("src").join("component.cpp").write(
        """
#include <component.h>

void dummy(void ) {};
    """
    )

    tmpdir.mkdir("src").join("main.c").write(
        """
#include <component.h>

#ifndef I_AM_COMPONENT
#error "I_AM_COMPONENT"
#endif

int main() {
}
"""
    )

    metadata_path = tmpdir.join("metadata.json")
    result = clirunner.invoke(
        project_metadata_cmd,
        [
            "--project-dir",
            str(tmpdir),
            "-e",
            "native",
            "--json-output",
            "--json-output-path",
            str(metadata_path),
        ],
    )
    validate_cliresult(result)
    with open(str(metadata_path), encoding="utf8") as fp:
        metadata = json.load(fp)["native"]
    assert len(metadata["includes"]["build"]) == 3
    assert len(metadata["includes"]["compatlib"]) == 2
