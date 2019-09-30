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

from platformio.datamodel import DataModelException
from platformio.package.manifest import parser
from platformio.package.manifest.model import ManifestModel, StrictManifestModel


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


def test_library_json_valid_model():
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
    data = parser.ManifestFactory.new(contents, parser.ManifestFileType.LIBRARY_JSON)
    model = ManifestModel(**data.as_dict())
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
            "authors": [
                {
                    "url": "https://blog.benoitblanchon.fr",
                    "maintainer": False,
                    "email": None,
                    "name": "Benoit Blanchon",
                }
            ],
            "export": {
                "exclude": ["fuzzing", "scripts", "test", "third-party"],
                "include": None,
            },
            "frameworks": ["arduino"],
            "platforms": ["*"],
            "license": "MIT",
        }.items()
    )


def test_library_properties_valid_model():
    contents = """
name=U8glib
version=1.19.1
author=oliver <olikraus@gmail.com>
maintainer=oliver <olikraus@gmail.com>
sentence=A library for monochrome TFTs and OLEDs
paragraph=Supported display controller: SSD1306, SSD1309, SSD1322, SSD1325
category=Display
url=https://github.com/olikraus/u8glib
architectures=avr,sam
"""
    data = parser.ManifestFactory.new(
        contents, parser.ManifestFileType.LIBRARY_PROPERTIES
    )
    model = ManifestModel(**data.as_dict())
    assert sorted(model.as_dict().items()) == sorted(
        {
            "license": None,
            "description": (
                "A library for monochrome TFTs and OLEDs. Supported display "
                "controller: SSD1306, SSD1309, SSD1322, SSD1325"
            ),
            "repository": {
                "url": "https://github.com/olikraus/u8glib",
                "type": "git",
                "branch": None,
            },
            "frameworks": ["arduino"],
            "platforms": ["atmelavr", "atmelsam"],
            "version": "1.19.1",
            "export": {
                "exclude": ["extras", "docs", "tests", "test", "*.doxyfile", "*.pdf"],
                "include": None,
            },
            "authors": [
                {
                    "url": None,
                    "maintainer": True,
                    "email": "olikraus@gmail.com",
                    "name": "oliver",
                }
            ],
            "keywords": ["display"],
            "homepage": None,
            "name": "U8glib",
        }.items()
    )


def test_broken_model():
    # "version" field is required
    with pytest.raises(
        DataModelException, match="Missed value for `ManifestModel.version` field"
    ):
        assert ManifestModel(name="MyPackage")

    # broken SemVer
    with pytest.raises(
        DataModelException,
        match="Invalid semantic versioning format for `ManifestModel.version` field",
    ):
        assert ManifestModel(name="MyPackage", version="broken_version")

    # the only name and version fields are required for base ManifestModel
    assert ManifestModel(name="MyPackage", version="1.0")

    # check strict model
    with pytest.raises(
        DataModelException,
        match="Missed value for `StrictManifestModel.description` field",
    ):
        assert StrictManifestModel(name="MyPackage", version="1.0")
