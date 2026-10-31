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

from platformio.package.commands.list import _get_tree_chars

UNICODE_CHARS = ("\u2502   ", "\u251c\u2500\u2500", "\u2514\u2500\u2500")
ASCII_CHARS = ("|   ", "|--", "`--")


def test_tree_chars_on_utf8():
    assert _get_tree_chars("utf-8") == UNICODE_CHARS


def test_tree_chars_fall_back_to_ascii_on_legacy_codepage():
    # Legacy Windows code pages cannot encode box-drawing characters
    assert _get_tree_chars("cp1252") == ASCII_CHARS
    assert _get_tree_chars("cp1251") == ASCII_CHARS


def test_tree_chars_fall_back_to_ascii_on_unknown_encoding():
    assert _get_tree_chars("definitely-not-an-encoding") == ASCII_CHARS
