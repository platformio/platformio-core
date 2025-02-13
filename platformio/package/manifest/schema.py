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

# pylint: disable=too-many-ancestors

import json
import re

import marshmallow
import requests
import semantic_version
from marshmallow import Schema, ValidationError, fields, validate, validates

from platformio.http import fetch_remote_content
from platformio.package.exception import ManifestValidationError
from platformio.util import memoized


class BaseSchema(Schema):
    class Meta:
        unknown = marshmallow.EXCLUDE  # pylint: disable=no-member

    def load_manifest(self, data):
        return self.load(data)

    def handle_error(self, error, data, **_):  # pylint: disable=arguments-differ
        raise ManifestValidationError(
            error.messages,
            data,
            error.valid_data if hasattr(error, "valid_data") else error.data,
        )


class StrictSchema(BaseSchema):
    def handle_error(self, error, data, **_):  # pylint: disable=arguments-differ
        # skip broken records
        if self.many:
            error.valid_data = [
                item for idx, item in enumerate(data) if idx not in error.messages
            ]
        else:
            error.valid_data = None
        raise error


class StrictListField(fields.List):
    def _deserialize(  # pylint: disable=arguments-differ
        self, value, attr, data, **kwargs
    ):
        try:
            return super()._deserialize(value, attr, data, **kwargs)
        except ValidationError as exc:
            if exc.data:
                exc.data = [item for item in exc.data if item is not None]
            raise exc


class AuthorSchema(StrictSchema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(validate=validate.Length(min=1, max=50))
    maintainer = fields.Bool(dump_default=False)
    url = fields.Url(validate=validate.Length(min=1, max=255))


class RepositorySchema(StrictSchema):
    type = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["git", "hg", "svn"],
            error="Invalid repository type, please use one of [git, hg, svn]",
        ),
    )
    url = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    branch = fields.Str(validate=validate.Length(min=1, max=50))


class DependencySchema(StrictSchema):
    owner = fields.Str(validate=validate.Length(min=1, max=100))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    version = fields.Str(validate=validate.Length(min=1, max=100))
    authors = StrictListField(fields.Str(validate=validate.Length(min=1, max=50)))
    platforms = StrictListField(
        fields.Str(
            validate=[
                validate.Length(min=1, max=50),
                validate.Regexp(
                    r"^([a-z\d\-_]+|\*)$", error="Only [a-z0-9-_*] chars are allowed"
                ),
            ]
        )
    )
    frameworks = StrictListField(
        fields.Str(
            validate=[
                validate.Length(min=1, max=50),
                validate.Regexp(
                    r"^([a-z\d\-_]+|\*)$", error="Only [a-z0-9-_*] chars are allowed"
                ),
            ]
        )
    )


class ExportSchema(BaseSchema):
    include = StrictListField(fields.Str)
    exclude = StrictListField(fields.Str)


class ExampleSchema(StrictSchema):
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=255),
            validate.Regexp(
                r"^[a-zA-Z\d\-\_/\. ]+$",
                error="Only [a-zA-Z0-9-_/. ] chars are allowed",
            ),
        ],
    )
    base = fields.Str(required=True)
    files = StrictListField(fields.Str, required=True)


# Fields


class ScriptField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, (str, list)):
            return value
        raise ValidationError(
            "Script value must be a command (string) or list of arguments"
        )


# Scheme


class ManifestSchema(BaseSchema):
    # Required fields
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=100),
            validate.Regexp(
                r"^[^:;/,@\<\>]+$", error="The next chars [:;/,@<>] are not allowed"
            ),
        ],
    )
    version = fields.Str(required=True, validate=validate.Length(min=1, max=50))

    # Optional fields

    authors = fields.Nested(AuthorSchema, many=True)
    description = fields.Str(validate=validate.Length(min=1, max=1000))
    homepage = fields.Url(validate=validate.Length(min=1, max=255))
    license = fields.Str(validate=validate.Length(min=1, max=255))
    repository = fields.Nested(RepositorySchema)
    dependencies = fields.Nested(DependencySchema, many=True)
    scripts = fields.Dict(
        keys=fields.Str(validate=validate.OneOf(["postinstall", "preuninstall"])),
        values=ScriptField(),
    )

    # library.json
    export = fields.Nested(ExportSchema)
    examples = fields.Nested(ExampleSchema, many=True)
    downloadUrl = fields.Url(validate=validate.Length(min=1, max=255))

    keywords = StrictListField(
        fields.Str(
            validate=[
                validate.Length(min=1, max=50),
                validate.Regexp(
                    r"^[a-z\d\-_\+\. ]+$", error="Only [a-z0-9+_-. ] chars are allowed"
                ),
            ]
        )
    )
    platforms = StrictListField(
        fields.Str(
            validate=[
                validate.Length(min=1, max=50),
                validate.Regexp(
                    r"^([a-z\d\-_]+|\*)$", error="Only [a-z0-9-_*] chars are allowed"
                ),
            ]
        )
    )
    frameworks = StrictListField(
        fields.Str(
            validate=[
                validate.Length(min=1, max=50),
                validate.Regexp(
                    r"^([a-z\d\-_]+|\*)$", error="Only [a-z0-9-_*] chars are allowed"
                ),
            ]
        )
    )
    headers = StrictListField(
        fields.Str(
            validate=[
                validate.Length(min=1, max=255),
            ]
        )
    )

    # platform.json specific
    title = fields.Str(validate=validate.Length(min=1, max=100))

    # package.json specific
    system = StrictListField(
        fields.Str(
            validate=[
                validate.Length(min=1, max=50),
                validate.Regexp(
                    r"^[a-z\d\-_]+$", error="Only [a-z0-9-_] chars are allowed"
                ),
            ]
        )
    )

    @validates("version")
    def validate_version(self, value):
        try:
            value = str(value)
            assert "." in value
            # check leading zeros
            try:
                semantic_version.Version(value)
            except ValueError as exc:
                if "Invalid leading zero" in str(exc):
                    raise exc
            semantic_version.Version.coerce(value)
        except (AssertionError, ValueError) as exc:
            raise ValidationError(
                "Invalid semantic versioning format, see https://semver.org/"
            ) from exc

    @validates("license")
    def validate_license(self, value):
        try:
            spdx = self.load_spdx_licenses()
        except requests.exceptions.RequestException as exc:
            raise ValidationError(
                "Could not load SPDX licenses for validation"
            ) from exc
        known_ids = set(item.get("licenseId") for item in spdx.get("licenses", []))
        if value in known_ids:
            return True
        # parse license expression
        # https://spdx.github.io/spdx-spec/SPDX-license-expressions/
        package_ids = [
            item.strip()
            for item in re.sub(r"(\s+(?:OR|AND|WITH)\s+|[\(\)])", " ", value).split(" ")
            if item.strip()
        ]
        if known_ids >= set(package_ids):
            return True
        raise ValidationError(
            "Invalid SPDX license identifier. See valid identifiers at "
            "https://spdx.org/licenses/"
        )

    @staticmethod
    @memoized(expire="1h")
    def load_spdx_licenses():
        version = "3.26.0"
        spdx_data_url = (
            "https://raw.githubusercontent.com/spdx/license-list-data/"
            f"v{version}/json/licenses.json"
        )
        return json.loads(fetch_remote_content(spdx_data_url))
