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

from platformio.datamodel import DataField, DataModel


class AuthorModel(DataModel):
    name = DataField(max_length=50, required=True)
    email = DataField(max_length=50)
    maintainer = DataField(default=False, type=bool)
    url = DataField(max_length=255)


class RepositoryModel(DataModel):
    type = DataField(max_length=3, required=True)
    url = DataField(max_length=255, required=True)
    branch = DataField(max_length=50)


class ExportModel(DataModel):
    include = [DataField()]
    exclude = [DataField()]


class ManifestModel(DataModel):

    name = DataField(max_length=100, required=True)
    version = DataField(
        required=True,
        max_length=50,
        validate_factory=lambda v: v if semantic_version.Version.coerce(v) else None,
    )

    description = DataField(max_length=1000)
    keywords = [DataField(max_length=255, regex=r"^[a-z][a-z\d\- ]*[a-z]$")]
    authors = [AuthorModel]

    homepage = DataField(max_length=255)
    license = DataField(max_length=255)
    platforms = [DataField(max_length=50, regex=r"^[a-z\d\-_\*]+$")]
    frameworks = [DataField(max_length=50, regex=r"^[a-z\d\-_\*]+$")]

    repository = RepositoryModel
    export = ExportModel
