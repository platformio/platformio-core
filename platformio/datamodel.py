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


class DataFieldException(DataModelException):
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super(DataFieldException, self).__init__()

    def __str__(self):
        return "%s for `%s.%s` field" % (
            self.message,
            self.field.parent.__class__.__name__,
            self.field.name,
        )

    def __repr__(self):
        return str(self)


class ListOfType(object):
    def __init__(self, type):
        self.type = type


class DictOfType(object):
    def __init__(self, type):
        self.type = type


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

        self._parent = None
        self._name = None
        self.value = None

    def __repr__(self):
        return '<DataField %s="%s">' % (
            self.title,
            self.default if self.value is None else self.value,
        )

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.title = self.title or value.title()

    def validate(self, value):
        try:
            if self.required and value is None:
                raise ValueError("Missed value")
            if self.validate_factory is not None:
                return self.validate_factory(self, value) or self.default
            if value is None:
                return self.default
            if inspect.isclass(self.type) and issubclass(self.type, DataModel):
                return self.type(**self.ensure_value_is_dict(value))
            if inspect.isclass(self.type) and issubclass(self.type, (str, bool)):
                return getattr(self, "_validate_%s_value" % self.type.__name__)(value)
        except ValueError as e:
            raise DataFieldException(self, str(e))
        return value

    @staticmethod
    def ensure_value_is_dict(value):
        if not isinstance(value, dict):
            raise ValueError("Value should be type of dict, not `%s`" % type(value))
        return value

    def _validate_str_value(self, value):
        if not isinstance(value, string_types):
            value = str(value)
        if self.min_length and len(value) < self.min_length:
            raise ValueError(
                "Minimum allowed length is %d characters" % self.min_length
            )
        if self.max_length and len(value) > self.max_length:
            raise ValueError(
                "Maximum allowed length is %d characters" % self.max_length
            )
        if self.regex and not re.match(self.regex, value):
            raise ValueError(
                "Value `%s` does not match RegExp `%s` pattern" % (value, self.regex)
            )
        return value

    @staticmethod
    def _validate_bool_value(value):
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "yes", "1")


class DataModel(object):

    _field_names = None
    _exceptions = None

    def __init__(self, **kwargs):
        self._field_names = []
        self._exceptions = set()
        for name, field in get_class_attributes(self).items():
            if not isinstance(field, DataField):
                continue
            field.parent = self
            field.name = name
            self._field_names.append(name)

            raw_value = kwargs.get(name)
            value = None
            try:
                if isinstance(field.type, ListOfType):
                    value = self._validate_list_of_type(field, name, raw_value)
                elif isinstance(field.type, DictOfType):
                    value = self._validate_dict_of_type(field, name, raw_value)
                else:
                    value = field.validate(raw_value)
            except DataFieldException as e:
                self._exceptions.add(e)
                if isinstance(self, StrictDataModel):
                    raise e
            finally:
                setattr(self, name, value)

    def _validate_list_of_type(self, field, name, value):
        data_type = field.type.type
        # check if ListOfType is not required
        value = field.validate(value)
        if not value:
            return None
        if not isinstance(value, list):
            raise DataFieldException(field, "Value should be a list")

        if isinstance(data_type, DataField):
            result = []
            data_type.parent = self
            data_type.name = name
            for v in value:
                try:
                    result.append(data_type.validate(v))
                except DataFieldException as e:
                    self._exceptions.add(e)
                    if isinstance(self, StrictDataModel):
                        raise e
            return result

        assert issubclass(data_type, DataModel)

        result = []
        for v in value:
            try:
                if not isinstance(v, dict):
                    raise DataFieldException(
                        field, "Value `%s` should be type of dictionary" % v
                    )
                m = data_type(**v)
                me = m.get_exceptions()
                if not me:
                    result.append(m)
                else:
                    self._exceptions |= set(me)
            except DataFieldException as e:
                self._exceptions.add(e)
                if isinstance(self, StrictDataModel):
                    raise e
        return result

    def _validate_dict_of_type(self, field, _, value):
        data_type = field.type.type
        assert issubclass(data_type, DataModel)

        # check if DictOfType is not required
        value = field.validate(value)
        if not value:
            return None
        if not isinstance(value, dict):
            raise DataFieldException(
                field, "Value `%s` should be type of dictionary" % value
            )
        result = {}
        for k, v in value.items():
            try:
                if not isinstance(v, dict):
                    raise DataFieldException(
                        field, "Value `%s` should be type of dictionary" % v
                    )
                m = data_type(**v)
                me = m.get_exceptions()
                if not me:
                    result[k] = m
                else:
                    self._exceptions |= set(me)
            except DataFieldException as e:
                self._exceptions.add(e)
                if isinstance(self, StrictDataModel):
                    raise e
        return result

    def __eq__(self, other):
        assert isinstance(other, DataModel)
        if self.get_field_names() != other.get_field_names():
            return False
        return self.as_dict() == other.as_dict()

    def __repr__(self):
        fields = []
        for name in self._field_names:
            fields.append('%s="%s"' % (name, getattr(self, name)))
        return "<%s %s>" % (self.__class__.__name__, " ".join(fields))

    def get_field_names(self):
        return self._field_names

    def get_exceptions(self):
        result = list(self._exceptions)
        for name in self._field_names:
            value = getattr(self, name)
            if isinstance(value, DataModel):
                result.extend(value.get_exceptions())
                continue
            if not isinstance(value, (dict, list)):
                continue
            for v in value.values() if isinstance(value, dict) else value:
                if not isinstance(v, DataModel):
                    continue
                result.extend(v.get_exceptions())
        return result

    def as_dict(self):
        result = {}
        for name in self._field_names:
            value = getattr(self, name)
            if isinstance(value, DataModel):
                value = getattr(self, name).as_dict()
            if isinstance(value, dict):
                for k, v in value.items():
                    if not isinstance(v, DataModel):
                        continue
                    value[k] = v.as_dict()
            elif isinstance(value, list):
                value = [v.as_dict() if isinstance(v, DataModel) else v for v in value]
            result[name] = value
        return result


class StrictDataModel(DataModel):
    pass
