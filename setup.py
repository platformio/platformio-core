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

import sys
from pathlib import Path

from setuptools import setup


def setup_package():
    # Isolated build hooks do not add the source tree to the import path.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from platformio import __description__
    from platformio.dependencies import get_pip_dependencies

    # Preserve build-time dependency selection for SOCKS and older OpenSSL.
    setup(description=__description__, install_requires=get_pip_dependencies())


setup_package()
