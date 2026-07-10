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

import pytest

from platformio.project.integration import jsonc


def test_loads_plain_json():
    assert jsonc.loads('{"a": [1, 2]}') == {"a": [1, 2]}


def test_loads_line_comments():
    text = """{
    // leading comment
    "recommendations": [
        "a", // trailing comment
        "b"
    ]
}"""
    assert jsonc.loads(text) == {"recommendations": ["a", "b"]}


def test_loads_block_comments():
    text = """{
    /* block
       comment */
    "recommendations": ["a", "b"]
}"""
    assert jsonc.loads(text) == {"recommendations": ["a", "b"]}


def test_loads_trailing_commas():
    text = """{
    "recommendations": [
        "a",
        "b",
    ],
}"""
    assert jsonc.loads(text) == {"recommendations": ["a", "b"]}


def test_loads_preserves_comment_markers_inside_strings():
    text = '{"url": "http://example.com", "note": "a // b /* c */"}'
    assert jsonc.loads(text) == {
        "url": "http://example.com",
        "note": "a // b /* c */",
    }


def test_loads_invalid_raises():
    with pytest.raises(ValueError):
        jsonc.loads("{ not valid }")


def test_ensure_no_change_when_present():
    text = """{
    "recommendations": [
        "platformio.platformio-ide"
    ]
}"""
    result, changed = jsonc.ensure_array_items(
        text, "recommendations", ["platformio.platformio-ide"]
    )
    assert changed is False
    assert result == text


def test_ensure_inserts_preserving_inline_comment():
    text = """{
    "recommendations": [
        "esbenp.prettier-vscode" // team formatter
    ]
}"""
    result, changed = jsonc.ensure_array_items(
        text, "recommendations", ["platformio.platformio-ide"]
    )
    assert changed is True
    # user's entry and comment are preserved
    assert "esbenp.prettier-vscode" in result
    assert "// team formatter" in result
    parsed = jsonc.loads(result)
    assert parsed["recommendations"] == [
        "esbenp.prettier-vscode",
        "platformio.platformio-ide",
    ]


def test_ensure_inserts_preserving_block_comment():
    text = """{
    /* our team config */
    "recommendations": [
        "esbenp.prettier-vscode"
    ]
}"""
    result, changed = jsonc.ensure_array_items(
        text, "recommendations", ["platformio.platformio-ide"]
    )
    assert changed is True
    assert "/* our team config */" in result
    assert jsonc.loads(result)["recommendations"] == [
        "esbenp.prettier-vscode",
        "platformio.platformio-ide",
    ]


def test_ensure_into_empty_array():
    text = '{\n    "recommendations": []\n}'
    result, changed = jsonc.ensure_array_items(
        text, "recommendations", ["platformio.platformio-ide"]
    )
    assert changed is True
    assert jsonc.loads(result)["recommendations"] == ["platformio.platformio-ide"]


def test_ensure_into_array_with_trailing_comma():
    text = """{
    "recommendations": [
        "esbenp.prettier-vscode",
    ]
}"""
    result, changed = jsonc.ensure_array_items(
        text, "recommendations", ["platformio.platformio-ide"]
    )
    assert changed is True
    parsed = jsonc.loads(result)
    assert parsed["recommendations"] == [
        "esbenp.prettier-vscode",
        "platformio.platformio-ide",
    ]


def test_ensure_creates_missing_key():
    text = """{
    "unwantedRecommendations": [
        "ms-vscode.cpptools-extension-pack"
    ]
}"""
    result, changed = jsonc.ensure_array_items(
        text, "recommendations", ["platformio.platformio-ide"]
    )
    assert changed is True
    parsed = jsonc.loads(result)
    assert parsed["recommendations"] == ["platformio.platformio-ide"]
    # existing key untouched
    assert parsed["unwantedRecommendations"] == ["ms-vscode.cpptools-extension-pack"]


def test_ensure_only_inserts_missing_items():
    text = """{
    "recommendations": [
        "platformio.platformio-ide"
    ]
}"""
    result, changed = jsonc.ensure_array_items(
        text,
        "recommendations",
        ["platformio.platformio-ide", "esbenp.prettier-vscode"],
    )
    assert changed is True
    parsed = jsonc.loads(result)
    assert parsed["recommendations"] == [
        "platformio.platformio-ide",
        "esbenp.prettier-vscode",
    ]


def test_ensure_invalid_jsonc_raises():
    with pytest.raises(ValueError):
        jsonc.ensure_array_items("{ not json }", "recommendations", ["x"])
