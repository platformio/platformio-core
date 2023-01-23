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

import glob
import hashlib
import io
import json
import os
import re
import shutil
import stat
import sys

import click

from platformio import exception, proc
from platformio.compat import IS_WINDOWS


class cd:
    def __init__(self, new_path):
        self.new_path = new_path
        self.prev_path = os.getcwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.prev_path)


def get_source_dir():
    curpath = os.path.abspath(__file__)
    if not os.path.isfile(curpath):
        for p in sys.path:
            if os.path.isfile(os.path.join(p, __file__)):
                curpath = os.path.join(p, __file__)
                break
    return os.path.dirname(curpath)


def get_assets_dir():
    return os.path.join(get_source_dir(), "assets")


def load_json(file_path):
    try:
        with open(file_path, mode="r", encoding="utf8") as f:
            return json.load(f)
    except ValueError as exc:
        raise exception.InvalidJSONFile(file_path) from exc


def humanize_file_size(filesize):
    base = 1024
    unit = 0
    suffix = "B"
    filesize = float(filesize)
    if filesize < base:
        return "%d%s" % (filesize, suffix)
    for i, suffix in enumerate("KMGTPEZY"):
        unit = base ** (i + 2)
        if filesize >= unit:
            continue
        if filesize % (base ** (i + 1)):
            return "%.2f%sB" % ((base * filesize / unit), suffix)
        break
    return "%d%sB" % ((base * filesize / unit), suffix)


def calculate_file_hashsum(algorithm, path):
    h = hashlib.new(algorithm)
    with io.open(path, "rb", buffering=0) as fp:
        while True:
            chunk = fp.read(io.DEFAULT_BUFFER_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def calculate_folder_size(path):
    assert os.path.isdir(path)
    result = 0
    for root, __, files in os.walk(path):
        for f in files:
            file_path = os.path.join(root, f)
            if not os.path.islink(file_path):
                result += os.path.getsize(file_path)
    return result


def get_platformio_udev_rules_path():
    return os.path.abspath(
        os.path.join(get_assets_dir(), "system", "99-platformio-udev.rules")
    )


def ensure_udev_rules():
    from platformio.util import get_systype  # pylint: disable=import-outside-toplevel

    def _rules_to_set(rules_path):
        result = set()
        with open(rules_path, encoding="utf8") as fp:
            for line in fp.readlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                result.add(line)
        return result

    if "linux" not in get_systype():
        return None
    installed_rules = [
        "/etc/udev/rules.d/99-platformio-udev.rules",
        "/lib/udev/rules.d/99-platformio-udev.rules",
    ]
    if not any(os.path.isfile(p) for p in installed_rules):
        raise exception.MissedUdevRules

    origin_path = get_platformio_udev_rules_path()
    if not os.path.isfile(origin_path):
        return None

    origin_rules = _rules_to_set(origin_path)
    for rules_path in installed_rules:
        if not os.path.isfile(rules_path):
            continue
        current_rules = _rules_to_set(rules_path)
        if not origin_rules <= current_rules:
            raise exception.OutdatedUdevRules(rules_path)

    return True


def path_endswith_ext(path, extensions):
    if not isinstance(extensions, (list, tuple)):
        extensions = [extensions]
    for ext in extensions:
        if path.endswith("." + ext):
            return True
    return False


def match_src_files(src_dir, src_filter=None, src_exts=None, followlinks=True):
    def _add_candidate(items, item, src_dir):
        if not src_exts or path_endswith_ext(item, src_exts):
            items.add(os.path.relpath(item, src_dir))

    def _find_candidates(pattern):
        candidates = set()
        for item in glob.glob(
            os.path.join(glob.escape(src_dir), pattern), recursive=True
        ):
            if not os.path.isdir(item):
                _add_candidate(candidates, item, src_dir)
                continue
            for root, dirs, files in os.walk(item, followlinks=followlinks):
                for d in dirs if not followlinks else []:
                    if os.path.islink(os.path.join(root, d)):
                        _add_candidate(candidates, os.path.join(root, d), src_dir)
                for f in files:
                    _add_candidate(candidates, os.path.join(root, f), src_dir)
        return candidates

    src_filter = src_filter or ""
    if isinstance(src_filter, (list, tuple)):
        src_filter = " ".join(src_filter)

    result = set()
    # correct fs directory separator
    src_filter = src_filter.replace("/", os.sep).replace("\\", os.sep)
    for (action, pattern) in re.findall(r"(\+|\-)<([^>]+)>", src_filter):
        candidates = _find_candidates(pattern)
        if action == "+":
            result |= candidates
        else:
            result -= candidates
    return sorted(list(result))


def to_unix_path(path):
    if not IS_WINDOWS or not path:
        return path
    return re.sub(r"[\\]+", "/", path)


def normalize_path(path):
    path = os.path.abspath(path)
    if not IS_WINDOWS or not path.startswith("\\\\"):
        return path
    try:
        result = proc.exec_command(["net", "use"])
        if result["returncode"] != 0:
            return path
        share_re = re.compile(r"\s([A-Z]\:)\s+(\\\\[^\s]+)")
        for line in result["out"].split("\n"):
            share = share_re.search(line)
            if not share:
                continue
            path = path.replace(share.group(2), share.group(1))
    except OSError:
        pass
    return path


def expanduser(path):
    """
    Be compatible with Python 3.8, on Windows skip HOME and check for USERPROFILE
    """
    if not IS_WINDOWS or not path.startswith("~") or "USERPROFILE" not in os.environ:
        return os.path.expanduser(path)
    return os.environ["USERPROFILE"] + path[1:]


def change_filemtime(path, mtime):
    os.utime(path, (mtime, mtime))


def rmtree(path):
    def _onerror(func, path, __):
        try:
            st_mode = os.stat(path).st_mode
            if st_mode & stat.S_IREAD:
                os.chmod(path, st_mode | stat.S_IWRITE)
            func(path)
        except Exception as exc:  # pylint: disable=broad-except
            click.secho(
                "%s \nPlease manually remove the file `%s`" % (str(exc), path),
                fg="red",
                err=True,
            )

    return shutil.rmtree(path, onerror=_onerror)
