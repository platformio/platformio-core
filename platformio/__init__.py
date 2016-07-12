# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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

VERSION = (2, 11, 1)
__version__ = ".".join([str(s) for s in VERSION])

__title__ = "platformio"
__description__ = (
    "An open source ecosystem for IoT development. "
    "Cross-platform build system and library manager. "
    "Continuous and IDE integration. "
    "Arduino and MBED compatible. Ready for Cloud compiling."
)
__url__ = "http://platformio.org"

__author__ = "Ivan Kravets"
__email__ = "me@ikravets.com"

__license__ = "Apache Software License"
__copyright__ = "Copyright 2014-2016 Ivan Kravets"

__apiurl__ = "http://api.platformio.org"
__apiip__ = "198.7.57.247"


if sys.version_info >= (3, 0, 0):
    msg = ("PlatformIO version %s does not run under Python version %s.\n"
           "Python 3 is not yet supported.\n")
    sys.stderr.write(msg % (__version__, sys.version.split()[0]))
    sys.exit(1)
