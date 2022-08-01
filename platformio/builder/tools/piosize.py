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

# pylint: disable=too-many-locals

import json
import sys
from os import environ, makedirs, remove
from os.path import isdir, join, splitdrive

from elftools.elf.descriptions import describe_sh_flags
from elftools.elf.elffile import ELFFile

from platformio.compat import IS_WINDOWS
from platformio.proc import exec_command


def _run_tool(cmd, env, tool_args):
    sysenv = environ.copy()
    sysenv["PATH"] = str(env["ENV"]["PATH"])

    build_dir = env.subst("$BUILD_DIR")
    if not isdir(build_dir):
        makedirs(build_dir)
    tmp_file = join(build_dir, "size-data-longcmd.txt")

    with open(tmp_file, mode="w", encoding="utf8") as fp:
        fp.write("\n".join(tool_args))

    cmd.append("@" + tmp_file)
    result = exec_command(cmd, env=sysenv)
    remove(tmp_file)

    return result


def _get_symbol_locations(env, elf_path, addrs):
    if not addrs:
        return {}
    cmd = [env.subst("$CC").replace("-gcc", "-addr2line"), "-e", elf_path]
    result = _run_tool(cmd, env, addrs)
    locations = [line for line in result["out"].split("\n") if line]
    assert len(addrs) == len(locations)

    return dict(zip(addrs, [l.strip() for l in locations]))


def _get_demangled_names(env, mangled_names):
    if not mangled_names:
        return {}
    result = _run_tool(
        [env.subst("$CC").replace("-gcc", "-c++filt")], env, mangled_names
    )
    demangled_names = [line for line in result["out"].split("\n") if line]
    assert len(mangled_names) == len(demangled_names)

    return dict(
        zip(
            mangled_names,
            [dn.strip().replace("::__FUNCTION__", "") for dn in demangled_names],
        )
    )


def _determine_section(sections, symbol_addr):
    for section, info in sections.items():
        if not _is_flash_section(info) and not _is_ram_section(info):
            continue
        if symbol_addr in range(info["start_addr"], info["start_addr"] + info["size"]):
            return section
    return "unknown"


def _is_ram_section(section):
    return (
        section.get("type", "") in ("SHT_NOBITS", "SHT_PROGBITS")
        and section.get("flags", "") == "WA"
    )


def _is_flash_section(section):
    return section.get("type", "") == "SHT_PROGBITS" and "A" in section.get("flags", "")


def _is_valid_symbol(symbol_name, symbol_type, symbol_address):
    return symbol_name and symbol_address != 0 and symbol_type != "STT_NOTYPE"


def _collect_sections_info(elffile):
    sections = {}
    for section in elffile.iter_sections():
        if section.is_null() or section.name.startswith(".debug"):
            continue

        section_type = section["sh_type"]
        section_flags = describe_sh_flags(section["sh_flags"])
        section_size = section.data_size

        sections[section.name] = {
            "size": section_size,
            "start_addr": section["sh_addr"],
            "type": section_type,
            "flags": section_flags,
        }

    return sections


def _collect_symbols_info(env, elffile, elf_path, sections):
    symbols = []

    symbol_section = elffile.get_section_by_name(".symtab")
    if symbol_section.is_null():
        sys.stderr.write("Couldn't find symbol table. Is ELF file stripped?")
        env.Exit(1)

    sysenv = environ.copy()
    sysenv["PATH"] = str(env["ENV"]["PATH"])

    symbol_addrs = []
    mangled_names = []
    for s in symbol_section.iter_symbols():
        symbol_info = s.entry["st_info"]
        symbol_addr = s["st_value"]
        symbol_size = s["st_size"]
        symbol_type = symbol_info["type"]

        if not _is_valid_symbol(s.name, symbol_type, symbol_addr):
            continue

        symbol = {
            "addr": symbol_addr,
            "bind": symbol_info["bind"],
            "name": s.name,
            "type": symbol_type,
            "size": symbol_size,
            "section": _determine_section(sections, symbol_addr),
        }

        if s.name.startswith("_Z"):
            mangled_names.append(s.name)

        symbol_addrs.append(hex(symbol_addr))
        symbols.append(symbol)

    symbol_locations = _get_symbol_locations(env, elf_path, symbol_addrs)
    demangled_names = _get_demangled_names(env, mangled_names)
    for symbol in symbols:
        if symbol["name"].startswith("_Z"):
            symbol["demangled_name"] = demangled_names.get(symbol["name"])
        location = symbol_locations.get(hex(symbol["addr"]))
        if not location or "?" in location:
            continue
        if IS_WINDOWS:
            drive, tail = splitdrive(location)
            location = join(drive.upper(), tail)
        symbol["file"] = location
        symbol["line"] = 0
        if ":" in location:
            file_, line = location.rsplit(":", 1)
            if line.isdigit():
                symbol["file"] = file_
                symbol["line"] = int(line)
    return symbols


def _calculate_firmware_size(sections):
    flash_size = ram_size = 0
    for section_info in sections.values():
        if _is_flash_section(section_info):
            flash_size += section_info.get("size", 0)
        if _is_ram_section(section_info):
            ram_size += section_info.get("size", 0)

    return ram_size, flash_size


def DumpSizeData(_, target, source, env):  # pylint: disable=unused-argument
    data = {"device": {}, "memory": {}, "version": 1}

    board = env.BoardConfig()
    if board:
        data["device"] = {
            "mcu": board.get("build.mcu", ""),
            "cpu": board.get("build.cpu", ""),
            "frequency": board.get("build.f_cpu"),
            "flash": int(board.get("upload.maximum_size", 0)),
            "ram": int(board.get("upload.maximum_ram_size", 0)),
        }
        if data["device"]["frequency"] and data["device"]["frequency"].endswith("L"):
            data["device"]["frequency"] = int(data["device"]["frequency"][0:-1])

    elf_path = env.subst("$PIOMAINPROG")

    with open(elf_path, "rb") as fp:
        elffile = ELFFile(fp)

        if not elffile.has_dwarf_info():
            sys.stderr.write("Elf file doesn't contain DWARF information")
            env.Exit(1)

        sections = _collect_sections_info(elffile)
        firmware_ram, firmware_flash = _calculate_firmware_size(sections)
        data["memory"]["total"] = {
            "ram_size": firmware_ram,
            "flash_size": firmware_flash,
            "sections": sections,
        }

        files = {}
        for symbol in _collect_symbols_info(env, elffile, elf_path, sections):
            file_path = symbol.get("file") or "unknown"
            if not files.get(file_path, {}):
                files[file_path] = {"symbols": [], "ram_size": 0, "flash_size": 0}

            symbol_size = symbol.get("size", 0)
            section = sections.get(symbol.get("section", ""), {})
            if _is_ram_section(section):
                files[file_path]["ram_size"] += symbol_size
            if _is_flash_section(section):
                files[file_path]["flash_size"] += symbol_size

            files[file_path]["symbols"].append(symbol)

        data["memory"]["files"] = []
        for k, v in files.items():
            file_data = {"path": k}
            file_data.update(v)
            data["memory"]["files"].append(file_data)

    with open(
        join(env.subst("$BUILD_DIR"), "sizedata.json"), mode="w", encoding="utf8"
    ) as fp:
        fp.write(json.dumps(data))


def exists(_):
    return True


def generate(env):
    env.AddMethod(DumpSizeData)
    return env
