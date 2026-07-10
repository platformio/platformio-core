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

"""Minimal helpers for working with JSONC (JSON with Comments).

VS Code configuration files such as ``.vscode/extensions.json`` are JSONC:
regular JSON that additionally allows ``//`` line comments, ``/* */`` block
comments, and trailing commas. The helpers here let PlatformIO parse those
files and insert entries *in place* without discarding the user's comments,
ordering, or formatting.
"""

import json
import re


def _blank_out(text, blank_strings):
    """Return a copy of ``text`` with comment characters replaced by spaces so
    that JSON structure can be located with plain string searches. String
    literals are left intact unless ``blank_strings`` is set, in which case
    their contents are blanked too (useful when scanning for structural
    brackets that must not match a bracket inside a string)."""
    out = []
    i = 0
    length = len(text)
    in_string = False
    while i < length:
        char = text[i]
        if in_string:
            if char == "\\" and i + 1 < length:
                out.append("  " if blank_strings else text[i : i + 2])
                i += 2
                continue
            if char == '"':
                in_string = False
                out.append('"')
            else:
                out.append(" " if blank_strings else char)
            i += 1
            continue
        if char == '"':
            in_string = True
            out.append('"')
            i += 1
            continue
        if char == "/" and i + 1 < length and text[i + 1] == "/":
            while i < length and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        if char == "/" and i + 1 < length and text[i + 1] == "*":
            while i < length and not (
                text[i] == "*" and i + 1 < length and text[i + 1] == "/"
            ):
                out.append(" ")
                i += 1
            for _ in range(min(2, length - i)):  # blank the closing "*/"
                out.append(" ")
                i += 1
            continue
        out.append(char)
        i += 1
    return "".join(out)


def loads(text):
    """Parse a JSONC string (comments and trailing commas allowed)."""
    without_comments = _blank_out(text, blank_strings=False)
    without_trailing_commas = re.sub(r",(\s*[}\]])", r"\1", without_comments)
    return json.loads(without_trailing_commas)


def _find_array_span(text, key):
    """Return the ``(open_bracket_idx, close_bracket_idx)`` of the array value
    for a top-level ``"key": [ ... ]`` pair, or ``None`` if it is absent."""
    comments_blanked = _blank_out(text, blank_strings=False)
    match = re.search(r'"%s"\s*:\s*\[' % re.escape(key), comments_blanked)
    if not match:
        return None
    open_idx = match.end() - 1
    fully_blanked = _blank_out(text, blank_strings=True)
    close_idx = fully_blanked.find("]", open_idx + 1)
    if close_idx == -1:
        return None
    return (open_idx, close_idx)


def _line_indent(text, idx):
    line_start = text.rfind("\n", 0, idx) + 1
    indent = ""
    for char in text[line_start:idx]:
        if char in " \t":
            indent += char
        else:
            break
    return indent


def _insert_new_array(text, key, items):
    """Add a brand-new ``"key": [ ... ]`` block right after the opening brace of
    the top-level object."""
    comments_blanked = _blank_out(text, blank_strings=False)
    brace_idx = comments_blanked.find("{")
    if brace_idx == -1:
        raise ValueError("No top-level JSON object found")
    base_indent = _line_indent(text, brace_idx)
    key_indent = base_indent + "    "
    item_indent = key_indent + "    "
    items_block = "".join('\n%s"%s",' % (item_indent, item) for item in items).rstrip(
        ","
    )
    block = '\n%s"%s": [%s\n%s],' % (key_indent, key, items_block, key_indent)
    return text[: brace_idx + 1] + block + text[brace_idx + 1 :]


def _insert_into_array(text, items, open_idx, close_idx):
    """Insert ``items`` just before the closing bracket of an existing array,
    matching the indentation of the array's existing elements."""
    fully_blanked = _blank_out(text, blank_strings=True)

    # Derive element indentation from the first existing element, otherwise
    # from the closing bracket's line plus one indent level.
    item_indent = None
    for idx in range(open_idx + 1, close_idx):
        if text[idx - 1] == "\n":
            cursor = idx
            while cursor < close_idx and text[cursor] in " \t":
                cursor += 1
            if cursor < close_idx and fully_blanked[cursor] == '"':
                item_indent = text[idx:cursor]
                break
    close_indent = _line_indent(text, close_idx)
    if item_indent is None:
        item_indent = close_indent + "    "

    # Find the last significant character before the closing bracket.
    last = close_idx - 1
    while last > open_idx and fully_blanked[last] in " \t\r\n":
        last -= 1
    last_significant = fully_blanked[last]

    addition = ""
    if last_significant not in ("[", ","):
        addition += ","
    addition += "".join('\n%s"%s",' % (item_indent, item) for item in items)
    addition = addition.rstrip(",")

    tail = ""
    if last_significant == "[":  # array had no multi-line elements
        tail = "\n" + close_indent

    return text[: last + 1] + addition + tail + text[last + 1 :]


def ensure_array_items(text, key, items):
    """Ensure every value in ``items`` is present in the JSONC array ``key``.

    Missing values are inserted in place, preserving existing comments,
    ordering, and formatting. Returns ``(new_text, changed)``. Raises
    ``ValueError`` if ``text`` is not parseable JSONC.
    """
    data = loads(text)
    if not isinstance(data, dict):
        raise ValueError("Expected a top-level JSON object")
    existing = data.get(key, [])
    missing = [item for item in items if item not in existing]
    if not missing:
        return (text, False)
    span = _find_array_span(text, key)
    if span is None:
        return (_insert_new_array(text, key, missing), True)
    return (_insert_into_array(text, missing, span[0], span[1]), True)
