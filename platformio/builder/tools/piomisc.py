# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import atexit
import re
from glob import glob
from os import remove
from os.path import basename, join


class InoToCPPConverter(object):

    PROTOTYPE_RE = re.compile(
        r"""^(
        (\s*[a-z_\d]+){1,2}         # return type
        (\s+[a-z_\d]+\s*)           # name of prototype
        \([a-z_,\.\*\&\[\]\s\d]*\)  # arguments
        )\s*\{                      # must end with {
        """,
        re.X | re.M | re.I
    )

    DETECTMAIN_RE = re.compile(r"void\s+(setup|loop)\s*\(", re.M | re.I)

    STRIPCOMMENTS_RE = re.compile(r"(/\*.*?\*/|^\s*//[^\r\n]*$)",
                                  re.M | re.S)

    def __init__(self, nodes):
        self.nodes = nodes

    def is_main_node(self, contents):
        return self.DETECTMAIN_RE.search(contents)

    @staticmethod
    def _replace_comments_callback(match):
        if "\n" in match.group(1):
            return "\n" * match.group(1).count("\n")
        else:
            return " "

    def _parse_prototypes(self, contents):
        prototypes = []
        reserved_keywords = set(["if", "else", "while"])
        for item in self.PROTOTYPE_RE.findall(contents):
            if set([item[1].strip(), item[2].strip()]) & reserved_keywords:
                continue
            prototypes.append(item[0])
        return prototypes

    def append_prototypes(self, fname, contents, prototypes):
        contents = self.STRIPCOMMENTS_RE.sub(self._replace_comments_callback,
                                             contents)
        result = []
        is_appended = False
        linenum = 0
        for line in contents.splitlines():
            linenum += 1
            line = line.strip()

            if not is_appended and line and not line.startswith("#"):
                is_appended = True
                result.append("%s;" % ";\n".join(prototypes))
                result.append('#line %d "%s"' % (linenum, fname))

            result.append(line)

        return result

    def convert(self):
        prototypes = []
        data = []
        for node in self.nodes:
            ino_contents = node.get_text_contents()
            prototypes += self._parse_prototypes(ino_contents)

            item = (basename(node.get_path()), ino_contents)
            if self.is_main_node(ino_contents):
                data = [item] + data
            else:
                data.append(item)

        if not data:
            return None

        result = ["#include <Arduino.h>"]
        is_first = True

        for name, contents in data:
            if is_first and prototypes:
                result += self.append_prototypes(name, contents, prototypes)
            else:
                result.append('#line 1 "%s"' % name)
                result.append(contents)
            is_first = False

        return "\n".join(result)


def ConvertInoToCpp(env):

    def delete_tmpcpp_file(file_):
        remove(file_)

    ino_nodes = (env.Glob(join("$PROJECTSRC_DIR", "*.ino")) +
                 env.Glob(join("$PROJECTSRC_DIR", "*.pde")))

    c = InoToCPPConverter(ino_nodes)
    data = c.convert()

    if not data:
        return

    tmpcpp_file = join(env.subst("$PROJECTSRC_DIR"), "tmp_ino_to.cpp")
    with open(tmpcpp_file, "w") as f:
        f.write(data)

    atexit.register(delete_tmpcpp_file, tmpcpp_file)


def DumpIDEData(env):
    data = {
        "defines": [],
        "includes": []
    }

    # includes from framework and libs
    for item in env.get("VARIANT_DIRS", []):
        if "$BUILDSRC_DIR" in item[0]:
            continue
        data['includes'].append(env.subst(item[1]))

    # includes from toolchain
    toolchain_dir = env.subst(
        join("$PIOPACKAGES_DIR", "$PIOPACKAGE_TOOLCHAIN"))
    toolchain_incglobs = [
        join(toolchain_dir, "*", "include"),
        join(toolchain_dir, "lib", "gcc", "*", "*", "include")
    ]
    for g in toolchain_incglobs:
        data['includes'].extend(glob(g))

    # global symbols
    for item in env.get("CPPDEFINES", []):
        if isinstance(item, list):
            item = "=".join(item)
        data['defines'].append(env.subst(item))

    # special symbol for Atmel AVR MCU
    board = env.get("BOARD_OPTIONS", {})
    if board and board['platform'] == "atmelavr":
        data['defines'].append(
            "__AVR_%s__" % board['build']['mcu'].upper()
            .replace("ATMEGA", "ATmega")
            .replace("ATTINY", "ATtiny")
        )

    return data


def exists(_):
    return True


def generate(env):
    env.AddMethod(ConvertInoToCpp)
    env.AddMethod(DumpIDEData)
    return env
