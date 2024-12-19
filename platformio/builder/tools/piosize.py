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
from os import environ
from os.path import join, splitdrive
from pathlib import Path

from elftools.elf.descriptions import describe_sh_flags
from elftools.elf.elffile import ELFFile

from platformio.compat import IS_WINDOWS


def _get_source_path(top_DIE):
    src_file_dir = (
        top_DIE.attributes["DW_AT_name"].value.decode("utf-8").replace("\\", "/")
        if ("DW_AT_name" in top_DIE.attributes)
        else "?"
    )
    comp_dir = (
        top_DIE.attributes["DW_AT_comp_dir"].value.decode("utf-8").replace("\\", "/")
        if ("DW_AT_comp_dir" in top_DIE.attributes)
        else ""
    )

    return str(Path.resolve(Path(comp_dir) / Path(src_file_dir)).as_posix())


def _collect_dwarf_info(elffile):
    dwarf_list = []
    dwarfinfo = elffile.get_dwarf_info()
    src_path = ""

    for CU in dwarfinfo.iter_CUs():
        top_DIE = CU.get_top_DIE()

        if top_DIE.tag == "DW_TAG_compile_unit":
            src_path = _get_source_path(top_DIE)

        for DIE in top_DIE.iter_children():
            die_name_attr = DIE.attributes.get("DW_AT_name", None)
            die_name = die_name_attr.value.decode("utf-8") if die_name_attr else ""

            if die_name != "":
                if (DIE.tag == "DW_TAG_subprogram") or (
                    DIE.tag == "DW_TAG_variable" and "DW_AT_location" in DIE.attributes
                ):
                    src_line_attr = DIE.attributes.get("DW_AT_decl_line", None)
                    src_line = src_line_attr.value if src_line_attr else ""

                    dwarf_list.append(
                        {
                            "dw_name": die_name,
                            "src_path": src_path,
                            "src_line": src_line,
                        }
                    )

    sorted_dwarf_list = sorted(
        dwarf_list, key=lambda x: len(x["dw_name"]), reverse=False
    )
    return sorted_dwarf_list


def _get_dwarf_info(symbol, dwarfs):
    location = "?"
    line = ""
    demangled_name = ""

    for d in dwarfs:
        if d["dw_name"] in symbol["name"]:
            location = d["src_path"]
            line = d["src_line"]
            demangled_name = d["dw_name"]

    if demangled_name == "":
        demangled_name = symbol["name"]

    return location, line, demangled_name


def _collect_sections_info(env, elffile):
    sections = {}
    for section in elffile.iter_sections():
        if section.is_null() or section.name.startswith(".debug"):
            continue

        section_type = section["sh_type"]
        section_flags = describe_sh_flags(section["sh_flags"])
        section_size = section.data_size

        section_data = {
            "name": section.name,
            "size": section_size,
            "start_addr": section["sh_addr"],
            "type": section_type,
            "flags": section_flags,
        }

        sections[section.name] = section_data
        sections[section.name]["in_flash"] = env.pioSizeIsFlashSection(section_data)
        sections[section.name]["in_ram"] = env.pioSizeIsRamSection(section_data)

    return sections


def _collect_symbols_info(env, elffile, sections):
    symbols = []

    symbol_section = elffile.get_section_by_name(".symtab")
    if symbol_section.is_null():
        sys.stderr.write("Couldn't find symbol table. Is ELF file stripped?")
        env.Exit(1)

    sysenv = environ.copy()
    sysenv["PATH"] = str(env["ENV"]["PATH"])

    symbol_addrs = []
    for s in symbol_section.iter_symbols():
        symbol_info = s.entry["st_info"]
        symbol_addr = s["st_value"]
        symbol_size = s["st_size"]
        symbol_type = symbol_info["type"]

        if not env.pioSizeIsValidSymbol(s.name, symbol_size, symbol_type, symbol_addr):
            continue

        symbol = {
            "addr": symbol_addr,
            "bind": symbol_info["bind"],
            "name": s.name,
            "type": symbol_type,
            "size": symbol_size,
            "section": env.pioSizeDetermineSection(sections, symbol_addr),
        }

        symbol_addrs.append(hex(symbol_addr))
        symbols.append(symbol)

    sorted_symbols = sorted(symbols, key=lambda x: len(x["name"]), reverse=True)
    sorted_dwarf = _collect_dwarf_info(elffile)

    for symbol in sorted_symbols:

        location, line, demangled_name = _get_dwarf_info(symbol, sorted_dwarf)
        symbol["demangled_name"] = demangled_name

        if not location or "?" in location:
            continue
        if IS_WINDOWS:
            drive, tail = splitdrive(location)
            location = join(drive.upper(), tail)
        symbol["file"] = location
        symbol["line"] = line if (line != "") else 0

    return sorted_symbols


def pioSizeDetermineSection(_, sections, symbol_addr):
    for section, info in sections.items():
        if not info.get("in_flash", False) and not info.get("in_ram", False):
            continue
        if symbol_addr in range(info["start_addr"], info["start_addr"] + info["size"]):
            return section
    return "unknown"


def pioSizeIsValidSymbol(_, symbol_name, symbol_size, symbol_type, symbol_address):
    return (
        symbol_name
        and symbol_size != 0
        and symbol_address != 0
        and symbol_type != "STT_NOTYPE"
    )


def pioSizeIsRamSection(_, section):
    return (
        section.get("type", "") in ("SHT_NOBITS", "SHT_PROGBITS")
        and section.get("flags", "") == "WA"
    )


def pioSizeIsFlashSection(_, section):
    return section.get("type", "") == "SHT_PROGBITS" and "A" in section.get("flags", "")


def pioSizeCalculateFirmwareSize(_, sections):
    flash_size = ram_size = 0
    for section_info in sections.values():
        if section_info.get("in_flash", False):
            flash_size += section_info.get("size", 0)
        if section_info.get("in_ram", False):
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

        sections = _collect_sections_info(env, elffile)
        firmware_ram, firmware_flash = env.pioSizeCalculateFirmwareSize(sections)
        data["memory"]["total"] = {
            "ram_size": firmware_ram,
            "flash_size": firmware_flash,
            "sections": sections,
        }

        files = {}
        for symbol in _collect_symbols_info(env, elffile, sections):
            file_path = symbol.get("file") or "unknown"
            if not files.get(file_path, {}):
                files[file_path] = {"symbols": [], "ram_size": 0, "flash_size": 0}

            symbol_size = symbol.get("size", 0)
            section = sections.get(symbol.get("section", ""), {})
            if not section:
                continue
            if section.get("in_ram", False):
                files[file_path]["ram_size"] += symbol_size
            if section.get("in_flash", False):
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
    env.AddMethod(pioSizeIsRamSection)
    env.AddMethod(pioSizeIsFlashSection)
    env.AddMethod(pioSizeCalculateFirmwareSize)
    env.AddMethod(pioSizeDetermineSection)
    env.AddMethod(pioSizeIsValidSymbol)
    env.AddMethod(DumpSizeData)
    return env
