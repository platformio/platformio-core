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

"""Tests for platformio.app validators."""

import os

import pytest

from platformio import app


def test_projects_dir_validate_accepts_existing_directory(tmp_path):
    """A path that points to an existing directory passes through validation."""
    result = app.projects_dir_validate(str(tmp_path))
    assert result == os.path.abspath(str(tmp_path))


def test_projects_dir_validate_raises_on_nonexistent_path(tmp_path):
    """
    Regression for platformio-core#5403: validation used \`assert\` which is
    stripped by python -O, so invalid paths were silently accepted.

    Use a deliberately bogus subpath under tmp_path so the test is hermetic.
    """
    missing = tmp_path / "definitely-does-not-exist"
    assert not missing.exists()
    with pytest.raises(ValueError):
        app.projects_dir_validate(str(missing))


def test_projects_dir_validate_raises_on_file_path(tmp_path):
    """Files are not directories and must be rejected."""
    a_file = tmp_path / "not_a_dir.txt"
    a_file.write_text("x")
    with pytest.raises(ValueError):
        app.projects_dir_validate(str(a_file))
