# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

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
        f.write(_sources)

    return "@%s" % tmp_file


def exists(_):
    return True


def generate(env):

    env.Replace(
        _huge_sources_hook=_huge_sources_hook,
        ARCOM=env.get("ARCOM", "").replace(
            "$SOURCES", "${_huge_sources_hook(SOURCES)}"))

    return env
