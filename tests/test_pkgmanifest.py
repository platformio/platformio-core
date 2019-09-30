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

import pytest

from platformio.package.manifest import parser


def test_library_json_parser():
    contents = """
{
    "name": "TestPackage",
    "keywords": "kw1, KW2, kw3",
    "platforms": ["atmelavr", "espressif"],
    "url": "http://old.url.format",
    "exclude": [".gitignore", "tests"],
    "include": "mylib"
}
"""
    mp = parser.LibraryJsonManifestParser(contents)
    assert sorted(mp.as_dict().items()) == sorted(
        {
            "name": "TestPackage",
            "platforms": ["atmelavr", "espressif8266"],
            "export": {"exclude": [".gitignore", "tests"], "include": ["mylib"]},
            "keywords": ["kw1", "kw2", "kw3"],
            "homepage": "http://old.url.format",
        }.items()
    )


def test_module_json_parser():
    contents = """
{
  "author": "Name Surname <name@surname.com>",
  "description": "This is Yotta library",
  "homepage": "https://yottabuild.org",
  "keywords": [
    "mbed",
    "Yotta"
  ],
  "licenses": [
    {
      "type": "Apache-2.0",
      "url": "https://spdx.org/licenses/Apache-2.0"
    }
  ],
  "name": "YottaLibrary",
  "repository": {
    "type": "git",
    "url": "git@github.com:username/repo.git"
  },
  "version": "1.2.3"
}
"""
    mp = parser.ModuleJsonManifestParser(contents)
    assert sorted(mp.as_dict().items()) == sorted(
        {
            "name": "YottaLibrary",
            "description": "This is Yotta library",
            "homepage": "https://yottabuild.org",
            "keywords": ["mbed", "Yotta"],
            "license": "Apache-2.0",
            "platforms": ["*"],
            "frameworks": ["mbed"],
            "export": {"exclude": ["tests", "test", "*.doxyfile", "*.pdf"]},
            "authors": [
                {
                    "maintainer": False,
                    "email": "name@surname.com",
                    "name": "Name Surname",
                }
            ],
            "version": "1.2.3",
        }.items()
    )


def test_library_properties_parser():
    # test missed fields
    with pytest.raises(parser.ManifestParserException):
        parser.LibraryPropertiesManifestParser("name=TestPackage")

    # Base
    contents = """
name=TestPackage
version=1.2.3
author=SomeAuthor <info AT author.com>
sentence=This is Arduino library
"""
    mp = parser.LibraryPropertiesManifestParser(contents)
    assert sorted(mp.as_dict().items()) == sorted(
        {
            "name": "TestPackage",
            "version": "1.2.3",
            "description": "This is Arduino library",
            "repository": None,
            "platforms": ["*"],
            "frameworks": ["arduino"],
            "export": {
                "exclude": ["extras", "docs", "tests", "test", "*.doxyfile", "*.pdf"],
                "include": None,
            },
            "authors": [
                {"maintainer": False, "email": "info@author.com", "name": "SomeAuthor"}
            ],
            "keywords": ["uncategorized"],
            "homepage": None,
        }.items()
    )

    # Platforms ALL
    mp = parser.LibraryPropertiesManifestParser("architectures=*\n" + contents)
    assert mp.as_dict()["platforms"] == ["*"]
    # Platforms specific
    mp = parser.LibraryPropertiesManifestParser("architectures=avr, esp32\n" + contents)
    assert mp.as_dict()["platforms"] == ["atmelavr", "espressif32"]

    # Remote URL
    mp = parser.LibraryPropertiesManifestParser(
        contents,
        remote_url=(
            "https://raw.githubusercontent.com/username/reponame/master/"
            "libraries/TestPackage/library.properties"
        ),
    )
    assert mp.as_dict()["export"] == {
        "exclude": ["extras", "docs", "tests", "test", "*.doxyfile", "*.pdf"],
        "include": "libraries/TestPackage",
    }

    # Hope page
    mp = parser.LibraryPropertiesManifestParser(
        "url=https://github.com/username/reponame.git\n" + contents
    )
    assert mp.as_dict()["homepage"] is None
    assert mp.as_dict()["repository"] == {
        "type": "git",
        "url": "https://github.com/username/reponame.git",
    }


def test_library_json_model():
    contents = """
{
  "name": "ArduinoJson",
  "keywords": "JSON, rest, http, web",
  "description": "An elegant and efficient JSON library for embedded systems",
  "homepage": "https://arduinojson.org",
  "repository": {
    "type": "git",
    "url": "https://github.com/bblanchon/ArduinoJson.git"
  },
  "version": "6.12.0",
  "authors": {
    "name": "Benoit Blanchon",
    "url": "https://blog.benoitblanchon.fr"
  },
  "exclude": [
    "fuzzing",
    "scripts",
    "test",
    "third-party"
  ],
  "frameworks": "arduino",
  "platforms": "*",
  "license": "MIT"
}
"""
    model = parser.ManifestFactory.new(contents, parser.ManifestFileType.LIBRARY_JSON)
    assert sorted(model.as_dict().items()) == sorted(
        {
            "name": "ArduinoJson",
            "keywords": ["json", "rest", "http", "web"],
            "description": "An elegant and efficient JSON library for embedded systems",
            "homepage": "https://arduinojson.org",
            "repository": {
                "url": "https://github.com/bblanchon/ArduinoJson.git",
                "type": "git",
                "branch": None,
            },
            "version": "6.12.0",
            "authors": {
                "url": "https://blog.benoitblanchon.fr",
                "maintainer": False,
                "email": None,
                "name": "Benoit Blanchon",
            },
            "export": {
                "include": None,
                "exclude": ["fuzzing", "scripts", "test", "third-party"],
            },
            "frameworks": ["arduino"],
            "platforms": ["*"],
            "license": "MIT",
        }.items()
    )
