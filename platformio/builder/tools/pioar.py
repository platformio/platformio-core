# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import atexit
from os import remove
from tempfile import mkstemp

MAX_SOURCES_LENGTH = 8000  # Windows CLI has limit with command length to 8192


def _huge_sources_hook(sources):
    if len(str(sources)) < MAX_SOURCES_LENGTH:
        return sources

    _, tmp_file = mkstemp()
    with open(tmp_file, "w") as f:
        f.write(str(sources).replace("\\", "/"))

    atexit.register(remove, tmp_file)

    return "@%s" % tmp_file


def exists(_):
    return True


def generate(env):

    env.Replace(
        _huge_sources_hook=_huge_sources_hook,
        ARCOM=env.get("ARCOM", "").replace(
            "$SOURCES", "${_huge_sources_hook(SOURCES)}"))

    return env
