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

import inspect
import re

from platformio.compat import get_class_attributes, string_types
from platformio.exception import PlatformioException

# pylint: disable=too-many-instance-attributes
# pylint: disable=redefined-builtin, too-many-arguments


class DataModelException(PlatformioException):
    pass


class DataField(object):
    def __init__(
        self,
        default=None,
        type=str,
        required=False,
        min_length=None,
        max_length=None,
        regex=None,
        validate_factory=None,
        title=None,
    ):
        self.default = default
        self.type = type
        self.required = required
        self.min_length = min_length
        self.max_length = max_length
        self.regex = regex
        self.validate_factory = validate_factory
        self.title = title

        self._value = None

    def __repr__(self):
        return '<DataField %s="%s">' % (
            self.title,
            self.default if self._value is None else self._value,
        )

    def validate(self, value, parent, attr):
        if self.title is None:
            self.title = attr.title()
        try:
            if self.required and value is None:
                raise ValueError("Required field, value is None")
            if self.validate_factory is not None:
                value = self.validate_factory(value)
            if value is None:
                return self.default
            if issubclass(self.type, (str, list, bool)):
                return getattr(self, "_validate_%s_value" % self.type.__name__)(value)
        except (AssertionError, ValueError) as e:
            raise DataModelException(
                "%s for %s.%s" % (str(e), parent.__class__.__name__, attr)
            )
        return value

    def _validate_str_value(self, value):
        if not isinstance(value, string_types):
            value = str(value)
        assert self.min_length is None or len(value) >= self.min_length, (
            "Minimum allowed length is %d characters" % self.min_length
        )
        assert self.max_length is None or len(value) <= self.max_length, (
            "Maximum allowed length is %d characters" % self.max_length
        )
        assert self.regex is None or re.match(
            self.regex, value
        ), "Value `%s` does not match RegExp `%s` pattern" % (value, self.regex)
        return value

    @staticmethod
    def _validate_bool_value(value):
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "yes", "1")


class DataModel(object):
    __PRIVATE_ATTRIBUTES__ = ("__PRIVATE_ATTRIBUTES__", "_init_type", "as_dict")

    def __init__(self, data=None):
        data = data or {}
        assert isinstance(data, dict)

        for attr, scheme_or_model in get_class_attributes(self).items():
            if attr in self.__PRIVATE_ATTRIBUTES__:
                continue
            if isinstance(scheme_or_model, list):
                assert len(scheme_or_model) == 1
                if data.get(attr) is None:
                    setattr(self, attr, None)
                    continue

                if not isinstance(data.get(attr), list):
                    raise DataModelException("Value should be a list for %s" % (attr))
                setattr(
                    self,
                    attr,
                    [
                        self._init_type(scheme_or_model[0], v, attr)
                        for v in data.get(attr)
                    ],
                )
            else:
                setattr(
                    self, attr, self._init_type(scheme_or_model, data.get(attr), attr)
                )

    def __repr__(self):
        attrs = []
        for name, value in get_class_attributes(self).items():
            if name in self.__PRIVATE_ATTRIBUTES__:
                continue
            attrs.append('%s="%s"' % (name, value))
        return "<%s %s>" % (self.__class__.__name__, " ".join(attrs))

    def _init_type(self, type_, value, attr):
        if inspect.isclass(type_) and issubclass(type_, DataModel):
            return type_(value)
        if isinstance(type_, DataField):
            return type_.validate(value, parent=self, attr=attr)
        raise DataModelException("Undeclared or unknown data type for %s" % attr)

    def as_dict(self):
        result = {}
        for name, value in get_class_attributes(self).items():
            if name in self.__PRIVATE_ATTRIBUTES__:
                continue
            if isinstance(value, DataModel):
                result[name] = value.as_dict()
            elif value and isinstance(value, list) and isinstance(value[0], DataModel):
                result[name] = value[0].as_dict()
            else:
                result[name] = value
        return result
