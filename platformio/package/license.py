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

from packaging.licenses import InvalidLicenseExpression, canonicalize_license_expression


def normalize_declared_license(value):
    """Return a standard SPDX expression when the manifest declares one."""
    if not isinstance(value, str):
        return None
    try:
        expression = canonicalize_license_expression(value)
    except InvalidLicenseExpression:
        return None
    if "LicenseRef-" in expression:
        return None
    return expression
