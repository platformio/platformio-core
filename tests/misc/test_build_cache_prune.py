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

import click
import pytest

from platformio import fs
from platformio.exception import UserSideException
from platformio.project.config import ProjectConfig
from platformio.system.build_cache import (
    STAMP_NAME,
    prune_build_cache,
    prune_build_cache_throttled,
)

DAY = 86400


def make_cache(tmp_path, entries):
    """entries: {relative path: (size, age in days)}"""
    for rel, (size, age_days) in entries.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x" * size)
        mtime = time.time() - age_days * DAY
        os.utime(str(path), (mtime, mtime))
    return str(tmp_path)


def remaining(tmp_path):
    return sorted(
        os.path.relpath(os.path.join(r, f), str(tmp_path))
        for r, __, files in os.walk(str(tmp_path))
        for f in files
    )


def test_parse_file_size():
    assert fs.parse_file_size("0") == 0
    assert fs.parse_file_size("512") == 512
    assert fs.parse_file_size("1KB") == 1024
    assert fs.parse_file_size("500mb") == 500 * 1024**2
    assert fs.parse_file_size("1.5 GB") == int(1.5 * 1024**3)
    with pytest.raises(ValueError):
        fs.parse_file_size("lots")


def test_disabled_by_default(tmp_path):
    cache = make_cache(tmp_path, {"aa/old": (10, 400)})
    assert prune_build_cache(cache) == (0, 0)
    assert remaining(tmp_path) == [os.path.join("aa", "old")]


def test_max_age(tmp_path):
    cache = make_cache(
        tmp_path,
        {
            "aa/old": (10, 60),
            "bb/new": (10, 1),
            ".sconsign311.dblite": (5, 90),
            "config": (5, 90),
        },
    )
    assert prune_build_cache(cache, max_age_days=45) == (1, 10)
    assert ".sconsign311.dblite" in remaining(tmp_path)
    assert os.path.join("bb", "new") in remaining(tmp_path)
    assert os.path.join("aa", "old") not in remaining(tmp_path)


def test_max_size_removes_least_recently_used(tmp_path):
    cache = make_cache(
        tmp_path, {"aa/a": (100, 30), "bb/b": (100, 20), "cc/c": (100, 10)}
    )
    assert prune_build_cache(cache, max_size=200) == (1, 100)
    assert remaining(tmp_path) == [os.path.join("bb", "b"), os.path.join("cc", "c")]


def test_dry_run_keeps_files(tmp_path):
    cache = make_cache(tmp_path, {"aa/old": (10, 60)})
    assert prune_build_cache(cache, max_age_days=45, dry_run=True) == (1, 10)
    assert remaining(tmp_path) == [os.path.join("aa", "old")]


def test_throttle(tmp_path):
    cache = make_cache(tmp_path, {"aa/old": (10, 60)})
    assert prune_build_cache_throttled(cache, max_age_days=45) == (1, 10)
    assert os.path.isfile(os.path.join(cache, STAMP_NAME))
    make_cache(tmp_path, {"bb/old2": (10, 60)})
    assert prune_build_cache_throttled(cache, max_age_days=45) == (0, 0)  # throttled
    old = time.time() - 2 * DAY
    os.utime(os.path.join(cache, STAMP_NAME), (old, old))
    assert prune_build_cache_throttled(cache, max_age_days=45) == (1, 10)
    assert remaining(tmp_path) == [STAMP_NAME]


def test_root_files_and_symlinks_are_never_pruned(tmp_path):
    cache = make_cache(tmp_path, {"config": (5, 400), "aa/old": (10, 400)})
    try:
        os.symlink(str(tmp_path / "aa" / "old"), str(tmp_path / "aa" / "link"))
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not supported for this platform/user")
    assert prune_build_cache(cache, max_age_days=1, max_size=1) == (1, 10)
    assert os.path.exists(str(tmp_path / "config"))
    assert os.path.islink(str(tmp_path / "aa" / "link"))


def test_both_limits(tmp_path):
    cache = make_cache(
        tmp_path, {"aa/a": (100, 60), "bb/b": (100, 20), "cc/c": (100, 10)}
    )
    assert prune_build_cache(cache, max_age_days=45, max_size=100) == (2, 200)
    assert remaining(tmp_path) == [os.path.join("cc", "c")]


def test_future_stamp_does_not_block_pruning(tmp_path):
    cache = make_cache(tmp_path, {"aa/old": (10, 60), STAMP_NAME: (0, -5)})
    assert prune_build_cache_throttled(cache, max_age_days=45) == (1, 10)


def test_invalid_options(tmp_path):
    path = str(tmp_path / "platformio.ini")
    for ini, ok in (
        ("build_cache_max_size = 10GB\nbuild_cache_max_age = 45", True),
        ("build_cache_max_size = lots", False),
        ("build_cache_max_age = -1", False),
    ):
        with open(path, "w", encoding="utf8") as fp:
            fp.write("[platformio]\n%s\n" % ini)
        config = ProjectConfig(path)
        names = ("build_cache_max_size", "build_cache_max_age")
        if ok:
            assert [config.get("platformio", n) for n in names] == ["10GB", 45]
        else:
            with pytest.raises((UserSideException, click.BadParameter, ValueError)):
                [config.get("platformio", n) for n in names]


def test_options_from_environment(tmp_path, monkeypatch):
    path = str(tmp_path / "platformio.ini")
    with open(path, "w", encoding="utf8") as fp:
        fp.write("[platformio]\n")
    monkeypatch.setenv("PLATFORMIO_BUILD_CACHE_MAX_AGE", "45")
    monkeypatch.setenv("PLATFORMIO_BUILD_CACHE_MAX_SIZE", "10GB")
    config = ProjectConfig(path)
    assert config.get("platformio", "build_cache_max_age") == 45
    assert config.get("platformio", "build_cache_max_size") == "10GB"
    monkeypatch.setenv("PLATFORMIO_BUILD_CACHE_MAX_SIZE", "lots")
    with pytest.raises(UserSideException):
        ProjectConfig(path).get("platformio", "build_cache_max_size")


def test_zero_size_disables_pruning(tmp_path):
    cache = make_cache(tmp_path, {"aa/old": (10, 400)})
    assert fs.parse_file_size("0") == 0
    assert prune_build_cache_throttled(cache, None, fs.parse_file_size("0")) == (0, 0)
    assert remaining(tmp_path) == [os.path.join("aa", "old")]
