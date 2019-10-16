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

import semantic_version

from platformio.datamodel import DataField, DataModel, ListOfType, StrictDataModel


def validate_semver_field(_, value):
    value = str(value)
    if "." not in value:
        raise ValueError("Invalid semantic versioning format")
    return value if semantic_version.Version.coerce(value) else None


class AuthorModel(DataModel):
    name = DataField(max_length=50, required=True)
    email = DataField(max_length=50)
    maintainer = DataField(default=False, type=bool)
    url = DataField(max_length=255)


class StrictAuthorModel(AuthorModel, StrictDataModel):
    pass


class RepositoryModel(DataModel):
    type = DataField(max_length=3, required=True)
    url = DataField(max_length=255, required=True)
    branch = DataField(max_length=50)


class ExportModel(DataModel):
    include = DataField(type=ListOfType(DataField()))
    exclude = DataField(type=ListOfType(DataField()))


class ExampleModel(DataModel):
    name = DataField(max_length=100, regex=r"^[a-zA-Z\d\-\_/]+$", required=True)
    base = DataField(required=True)
    files = DataField(type=ListOfType(DataField()), required=True)


class ManifestModel(DataModel):

    # Required fields
    name = DataField(max_length=100, required=True)
    version = DataField(
        max_length=50, validate_factory=validate_semver_field, required=True
    )
    description = DataField(max_length=1000, required=True)
    keywords = DataField(
        type=ListOfType(DataField(max_length=255, regex=r"^[a-z\d\-\+\. ]+$")),
        required=True,
    )
    authors = DataField(type=ListOfType(AuthorModel), required=True)

    homepage = DataField(max_length=255)
    license = DataField(max_length=255)
    platforms = DataField(
        type=ListOfType(DataField(max_length=50, regex=r"^([a-z\d\-_]+|\*)$"))
    )
    frameworks = DataField(
        type=ListOfType(DataField(max_length=50, regex=r"^([a-z\d\-_]+|\*)$"))
    )

    repository = DataField(type=RepositoryModel)
    export = DataField(type=ExportModel)
    examples = DataField(type=ListOfType(ExampleModel))

    # platform.json specific
    title = DataField(max_length=100)

    # package.json specific
    system = DataField(
        type=ListOfType(DataField(max_length=50, regex=r"^[a-z\d\-_]+$"))
    )


class StrictManifestModel(ManifestModel, StrictDataModel):
    authors = DataField(type=ListOfType(StrictAuthorModel), required=True)
