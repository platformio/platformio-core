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

import os
import time

STAMP_NAME = ".pio-prune"
PRUNE_INTERVAL = 24 * 3600


def _collect_entries(cache_dir):
    """Cache entries live in sub-folders; files at the root belong to SCons/PIO
    (`config`, `.sconsign*`, the prune stamp) and are never touched"""
    entries = []  # (mtime, size, path)
    for root, __, files in os.walk(cache_dir):
        if os.path.normpath(root) == os.path.normpath(cache_dir):
            continue
        for name in files:
            path = os.path.join(root, name)
            try:
                if os.path.islink(path):
                    continue
                st = os.stat(path)
            except OSError:  # removed by a parallel build
                continue
            entries.append((st.st_mtime, st.st_size, path))
    entries.sort()  # oldest first
    return entries


def prune_build_cache(cache_dir, max_age_days=None, max_size=None, dry_run=False):
    """Remove stale entries from the SCons `build_cache_dir`.

    SCons updates the mtime of a cache file on every hit, so mtime is the time of
    last use. Entries older than `max_age_days` go first, then the least recently
    used ones until the cache fits `max_size` (bytes). Returns (files, bytes).
    """
    if not os.path.isdir(cache_dir) or not (max_age_days or max_size):
        return 0, 0
    entries = _collect_entries(cache_dir)

    expired = []
    if max_age_days:
        threshold = time.time() - max_age_days * 86400
        expired = [e for e in entries if e[0] < threshold]
        entries = entries[len(expired) :]
    if max_size:
        total = sum(e[1] for e in entries)
        while entries and total > max_size:
            entry = entries.pop(0)
            total -= entry[1]
            expired.append(entry)

    removed_files = removed_bytes = 0
    for __, size, path in expired:
        if not dry_run:
            try:
                os.remove(path)
            except OSError:
                continue
        removed_files += 1
        removed_bytes += size
    return removed_files, removed_bytes


def prune_build_cache_throttled(cache_dir, max_age_days=None, max_size=None):
    """Best-effort `prune_build_cache`, at most once a day (stamp in the cache)"""
    if not os.path.isdir(cache_dir) or not (max_age_days or max_size):
        return 0, 0
    stamp = os.path.join(cache_dir, STAMP_NAME)
    try:
        if 0 <= time.time() - os.path.getmtime(stamp) < PRUNE_INTERVAL:
            return 0, 0
    except OSError:
        pass
    try:
        result = prune_build_cache(cache_dir, max_age_days, max_size)
        with open(stamp, "w", encoding="utf8"):
            pass
    except Exception:  # pylint: disable=broad-except
        # pruning must never break a build
        return 0, 0
    return result
