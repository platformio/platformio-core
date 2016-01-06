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

from hashlib import md5
from os.path import join
from tempfile import gettempdir

MAX_SOURCES_LENGTH = 8000  # Windows CLI has limit with command length to 8192


def _huge_sources_hook(sources):
    _sources = str(sources).replace("\\", "/")
    if len(str(_sources)) < MAX_SOURCES_LENGTH:
        return sources

    tmp_file = join(gettempdir(), "pioarargs-%s" % md5(_sources).hexdigest())
    with open(tmp_file, "w") as f:
        # fix space in paths
        for line in _sources.split(".o "):
            if not line.endswith(".o"):
                line += ".o"
            f.write('"%s" ' % line)

    return '@"%s"' % tmp_file


def exists(_):
    return True


def generate(env):

    env.Replace(
        _huge_sources_hook=_huge_sources_hook,
        ARCOM=env.get("ARCOM", "").replace(
            "$SOURCES", "${_huge_sources_hook(SOURCES)}"))

    return env
