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

import marshmallow
import requests
import semantic_version
from marshmallow import Schema, ValidationError, fields, validate, validates

from platformio.package.exception import ManifestValidationError
from platformio.util import memoized

MARSHMALLOW_2 = marshmallow.__version_info__ < (3,)


if MARSHMALLOW_2:

    class CompatSchema(Schema):
        pass


else:

    class CompatSchema(Schema):
        class Meta(object):  # pylint: disable=no-init
            unknown = marshmallow.EXCLUDE  # pylint: disable=no-member

        def handle_error(self, error, data, **_):  # pylint: disable=arguments-differ
            raise ManifestValidationError(
                error.messages,
                data,
                error.valid_data if hasattr(error, "valid_data") else error.data,
            )


class BaseSchema(CompatSchema):
    def load_manifest(self, data):
        if MARSHMALLOW_2:
            data, errors = self.load(data)
            if errors:
                raise ManifestValidationError(errors, data, data)
            return data
        return self.load(data)


class StrictSchema(BaseSchema):
    def handle_error(self, error, data, **_):  # pylint: disable=arguments-differ
        # skip broken records
        if self.many:
            error.valid_data = [
                item for idx, item in enumerate(data) if idx not in error.messages
            ]
        else:
            error.valid_data = None
        if MARSHMALLOW_2:
            error.data = error.valid_data
        raise error


class StrictListField(fields.List):
    def _deserialize(  # pylint: disable=arguments-differ
        self, value, attr, data, **kwargs
    ):
        try:
            return super(StrictListField, self)._deserialize(
                value, attr, data, **kwargs
            )
        except ValidationError as exc:
            if exc.data:
                exc.data = [item for item in exc.data if item is not None]
            raise exc


class AuthorSchema(StrictSchema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    email = fields.Email(validate=validate.Length(min=1, max=50))
    maintainer = fields.Bool(default=False)
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
            validate.Length(min=1, max=100),
            validate.Regexp(
                r"^[a-zA-Z\d\-\_/]+$", error="Only [a-zA-Z0-9-_/] chars are allowed"
            ),
        ],
    )
    base = fields.Str(required=True)
    files = StrictListField(fields.Str, required=True)


class ManifestSchema(BaseSchema):
    # Required fields
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    version = fields.Str(required=True, validate=validate.Length(min=1, max=50))

    # Optional fields

    authors = fields.Nested(AuthorSchema, many=True)
    description = fields.Str(validate=validate.Length(min=1, max=1000))
    homepage = fields.Url(validate=validate.Length(min=1, max=255))
    license = fields.Str(validate=validate.Length(min=1, max=255))
    repository = fields.Nested(RepositorySchema)
    dependencies = fields.Nested(DependencySchema, many=True)

    # library.json
    export = fields.Nested(ExportSchema)
    examples = fields.Nested(ExampleSchema, many=True)
    downloadUrl = fields.Url(validate=validate.Length(min=1, max=255))

    keywords = StrictListField(
        fields.Str(
            validate=[
                validate.Length(min=1, max=50),
                validate.Regexp(
                    r"^[a-z\d\-\+\. ]+$", error="Only [a-z0-9-+. ] chars are allowed"
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
    def validate_version(self, value):  # pylint: disable=no-self-use
        try:
            value = str(value)
            assert "." in value
            semantic_version.Version.coerce(value)
        except (AssertionError, ValueError):
            raise ValidationError(
                "Invalid semantic versioning format, see https://semver.org/"
            )

    @validates("license")
    def validate_license(self, value):
        try:
            spdx = self.load_spdx_licenses()
        except requests.exceptions.RequestException:
            raise ValidationError("Could not load SPDX licenses for validation")
        for item in spdx.get("licenses", []):
            if item.get("licenseId") == value:
                return
        raise ValidationError(
            "Invalid SPDX license identifier. See valid identifiers at "
            "https://spdx.org/licenses/"
        )

    @staticmethod
    @memoized(expire="1h")
    def load_spdx_licenses():
        r = requests.get(
            "https://raw.githubusercontent.com/spdx/license-list-data"
            "/v3.8/json/licenses.json"
        )
        r.raise_for_status()
        return r.json()
