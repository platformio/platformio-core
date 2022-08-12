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

import atexit
import glob
import io
import os
import re
import tempfile

import click

from platformio.compat import get_filesystem_encoding, get_locale_encoding


class InoToCPPConverter:

    PROTOTYPE_RE = re.compile(
        r"""^(
        (?:template\<.*\>\s*)?      # template
        ([a-z_\d\&]+\*?\s+){1,2}    # return type
        ([a-z_\d]+\s*)              # name of prototype
        \([a-z_,\.\*\&\[\]\s\d]*\)  # arguments
        )\s*(\{|;)                  # must end with `{` or `;`
        """,
        re.X | re.M | re.I,
    )
    DETECTMAIN_RE = re.compile(r"void\s+(setup|loop)\s*\(", re.M | re.I)
    PROTOPTRS_TPLRE = r"\([^&\(]*&(%s)[^\)]*\)"

    def __init__(self, env):
        self.env = env
        self._main_ino = None
        self._safe_encoding = None

    def read_safe_contents(self, path):
        error_reported = False
        for encoding in (
            "utf-8",
            None,
            get_filesystem_encoding(),
            get_locale_encoding(),
            "latin-1",
        ):
            try:
                with io.open(path, encoding=encoding) as fp:
                    contents = fp.read()
                    self._safe_encoding = encoding
                    return contents
            except UnicodeDecodeError:
                if not error_reported:
                    error_reported = True
                    click.secho(
                        "Unicode decode error has occurred, please remove invalid "
                        "(non-ASCII or non-UTF8) characters from %s file or convert it to UTF-8"
                        % path,
                        fg="yellow",
                        err=True,
                    )
        return ""

    def write_safe_contents(self, path, contents):
        with io.open(
            path, "w", encoding=self._safe_encoding, errors="backslashreplace"
        ) as fp:
            return fp.write(contents)

    def is_main_node(self, contents):
        return self.DETECTMAIN_RE.search(contents)

    def convert(self, nodes):
        contents = self.merge(nodes)
        if not contents:
            return None
        return self.process(contents)

    def merge(self, nodes):
        assert nodes
        lines = []
        for node in nodes:
            contents = self.read_safe_contents(node.get_path())
            _lines = ['# 1 "%s"' % node.get_path().replace("\\", "/"), contents]
            if self.is_main_node(contents):
                lines = _lines + lines
                self._main_ino = node.get_path()
            else:
                lines.extend(_lines)

        if not self._main_ino:
            self._main_ino = nodes[0].get_path()

        return "\n".join(["#include <Arduino.h>"] + lines) if lines else None

    def process(self, contents):
        out_file = self._main_ino + ".cpp"
        assert self._gcc_preprocess(contents, out_file)
        contents = self.read_safe_contents(out_file)
        contents = self._join_multiline_strings(contents)
        self.write_safe_contents(out_file, self.append_prototypes(contents))
        return out_file

    def _gcc_preprocess(self, contents, out_file):
        tmp_path = tempfile.mkstemp()[1]
        self.write_safe_contents(tmp_path, contents)
        self.env.Execute(
            self.env.VerboseAction(
                '$CXX -o "{0}" -x c++ -fpreprocessed -dD -E "{1}"'.format(
                    out_file, tmp_path
                ),
                "Converting " + os.path.basename(out_file[:-4]),
            )
        )
        atexit.register(_delete_file, tmp_path)
        return os.path.isfile(out_file)

    def _join_multiline_strings(self, contents):
        if "\\\n" not in contents:
            return contents
        newlines = []
        linenum = 0
        stropen = False
        for line in contents.split("\n"):
            _linenum = self._parse_preproc_line_num(line)
            if _linenum is not None:
                linenum = _linenum
            else:
                linenum += 1

            if line.endswith("\\"):
                if line.startswith('"'):
                    stropen = True
                    newlines.append(line[:-1])
                    continue
                if stropen:
                    newlines[len(newlines) - 1] += line[:-1]
                    continue
            elif stropen and line.endswith(('",', '";')):
                newlines[len(newlines) - 1] += line
                stropen = False
                newlines.append(
                    '#line %d "%s"' % (linenum, self._main_ino.replace("\\", "/"))
                )
                continue

            newlines.append(line)

        return "\n".join(newlines)

    @staticmethod
    def _parse_preproc_line_num(line):
        if not line.startswith("#"):
            return None
        tokens = line.split(" ", 3)
        if len(tokens) > 2 and tokens[1].isdigit():
            return int(tokens[1])
        return None

    def _parse_prototypes(self, contents):
        prototypes = []
        reserved_keywords = set(["if", "else", "while"])
        for match in self.PROTOTYPE_RE.finditer(contents):
            if (
                set([match.group(2).strip(), match.group(3).strip()])
                & reserved_keywords
            ):
                continue
            prototypes.append(match)
        return prototypes

    def _get_total_lines(self, contents):
        total = 0
        if contents.endswith("\n"):
            contents = contents[:-1]
        for line in contents.split("\n")[::-1]:
            linenum = self._parse_preproc_line_num(line)
            if linenum is not None:
                return total + linenum
            total += 1
        return total

    def append_prototypes(self, contents):
        prototypes = self._parse_prototypes(contents) or []

        # skip already declared prototypes
        declared = set(m.group(1).strip() for m in prototypes if m.group(4) == ";")
        prototypes = [m for m in prototypes if m.group(1).strip() not in declared]

        if not prototypes:
            return contents

        prototype_names = set(m.group(3).strip() for m in prototypes)
        split_pos = prototypes[0].start()
        match_ptrs = re.search(
            self.PROTOPTRS_TPLRE % ("|".join(prototype_names)),
            contents[:split_pos],
            re.M,
        )
        if match_ptrs:
            split_pos = contents.rfind("\n", 0, match_ptrs.start()) + 1

        result = []
        result.append(contents[:split_pos].strip())
        result.append("%s;" % ";\n".join([m.group(1) for m in prototypes]))
        result.append(
            '#line %d "%s"'
            % (
                self._get_total_lines(contents[:split_pos]),
                self._main_ino.replace("\\", "/"),
            )
        )
        result.append(contents[split_pos:].strip())
        return "\n".join(result)


def FindInoNodes(env):
    src_dir = glob.escape(env.subst("$PROJECT_SRC_DIR"))
    return env.Glob(os.path.join(src_dir, "*.ino")) + env.Glob(
        os.path.join(src_dir, "*.pde")
    )


def ConvertInoToCpp(env):
    ino_nodes = env.FindInoNodes()
    if not ino_nodes:
        return
    c = InoToCPPConverter(env)
    out_file = c.convert(ino_nodes)

    atexit.register(_delete_file, out_file)


def _delete_file(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
    except:  # pylint: disable=bare-except
        pass


def generate(env):
    env.AddMethod(FindInoNodes)
    env.AddMethod(ConvertInoToCpp)


def exists(_):
    return True
