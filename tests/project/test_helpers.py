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

from platformio.project.helpers import compute_project_checksum


class DummyProjectConfig:
    def __init__(self, include_dir, src_dir, lib_dir):
        self._dirs = {
            "include_dir": str(include_dir),
            "src_dir": str(src_dir),
            "lib_dir": str(lib_dir),
        }

    def to_json(self):
        return "{}"

    def get(self, section, option):
        assert section == "platformio"
        return self._dirs[option]


def test_checksum_ignores_generated_ino_cpp(tmp_path):
    include_dir = tmp_path / "include"
    src_dir = tmp_path / "src"
    lib_dir = tmp_path / "lib"
    for directory in (include_dir, src_dir, lib_dir):
        directory.mkdir()

    config = DummyProjectConfig(include_dir, src_dir, lib_dir)
    (src_dir / "main.ino").write_text("void setup() {}\nvoid loop() {}\n")
    checksum = compute_project_checksum(config)

    (src_dir / "main.ino.cpp").write_text("#include <Arduino.h>\n")
    assert compute_project_checksum(config) == checksum


def test_checksum_tracks_regular_cpp_files(tmp_path):
    include_dir = tmp_path / "include"
    src_dir = tmp_path / "src"
    lib_dir = tmp_path / "lib"
    for directory in (include_dir, src_dir, lib_dir):
        directory.mkdir()

    config = DummyProjectConfig(include_dir, src_dir, lib_dir)
    checksum = compute_project_checksum(config)

    (src_dir / "main.cpp").write_text("int main() { return 0; }\n")
    assert compute_project_checksum(config) != checksum
