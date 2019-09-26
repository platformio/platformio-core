# Copyright (c) 2019-present PlatformIO <contact@platformio.org>
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

import sys
from os import environ
from os.path import join

from elftools.elf.descriptions import describe_sh_flags
from elftools.elf.elffile import ELFFile

from platformio.compat import dump_json_to_unicode
from platformio.proc import exec_command


def _get_file_location(env, elf_path, addr, sysenv):
    cmd = [env.subst("$CC").replace(
        "-gcc", "-addr2line"), "-e", elf_path, hex(addr)]
    result = exec_command(cmd, env=sysenv)
    location = result['out'].strip().replace("\\", "/")
    return location


def _determine_section(sections, symbol_addr):
    for section, info in sections.items():
        if symbol_addr in range(info['start_addr'],
                                info['start_addr'] + info['size']):
            return section
    return "unknown"


def _demangle_cpp_name(env, symbol_name, sysenv):
    cmd = [env.subst("$CC").replace("-gcc", "-c++filt"), symbol_name]
    result = exec_command(cmd, env=sysenv)
    demangled_name = result['out'].strip()
    if "(" in demangled_name:
        demangled_name = demangled_name[0:demangled_name.find("(")]
    return demangled_name


def _is_ram_section(section):
    if section.get("type", "") in (
            "SHT_NOBITS", "SHT_PROGBITS") and section.get("flags", "") == "WA":
        return True
    return False


def _is_flash_section(section):
    if section.get("type") == "SHT_PROGBITS" and "A" in section.get("flags"):
        return True
    return False


def _is_valid_symbol(symbol_name, symbol_type, symbol_address):
    return symbol_name and symbol_address != 0 and symbol_type != "STT_NOTYPE"


def _collect_sections_info(elffile):
    sections = {}
    for section in elffile.iter_sections():
        if section.is_null():
            continue

        section_type = section['sh_type']
        section_flags = describe_sh_flags(section['sh_flags'])
        section_size = section.data_size

        sections[section.name] = {
            "size": section_size,
            "start_addr": section['sh_addr'],
            "type": section_type,
            "flags": section_flags
        }

    return sections


def _collect_symbols_info(env, elffile, elf_path, sections):
    symbols = []

    symbol_section = elffile.get_section_by_name('.symtab')
    if symbol_section.is_null():
        sys.stderr.write("Couldn't find symbol table. Is ELF file stripped?")
        env.Exit(1)

    sysenv = environ.copy()
    sysenv["PATH"] = str(env["ENV"]["PATH"])

    for s in symbol_section.iter_symbols():
        symbol_info = s.entry['st_info']
        symbol_addr = s['st_value']
        symbol_size = s['st_size']
        symbol_type = symbol_info['type']

        if not _is_valid_symbol(s.name, symbol_type, symbol_addr):
            continue

        symbol = {
            "addr": symbol_addr,
            "bind": symbol_info['bind'],
            "location": _get_file_location(env, elf_path, symbol_addr, sysenv),
            "name": s.name,
            "type": symbol_type,
            "size": symbol_size,
            "section": _determine_section(sections, symbol_addr)
        }

        if s.name.startswith("_Z"):
            symbol['demangled_name'] = _demangle_cpp_name(env, s.name, sysenv)

        symbols.append(symbol)

    return symbols


def _calculate_firmware_size(sections):
    flash_size = ram_size = 0
    for section_info in sections.values():
        if _is_flash_section(section_info):
            flash_size += section_info.get("size", 0)
        if _is_ram_section(section_info):
            ram_size += section_info.get("size", 0)

    return ram_size, flash_size


def DumpSizeData(_, target, source, env):
    data = {
        "memory": {},
        "version": 1
    }

    elf_path = env.subst("$PIOMAINPROG")

    with open(elf_path, "rb") as fp:
        elffile = ELFFile(fp)

        if not elffile.has_dwarf_info():
            sys.stderr.write("Elf file doesn't contain DWARF information")
            env.Exit(1)

        sections = _collect_sections_info(elffile)
        firmware_ram, firmware_flash = _calculate_firmware_size(sections)
        data['memory']['total'] = {
            "ram_size": firmware_ram,
            "flash_size": firmware_flash,
            "sections": sections
        }

        files = dict()
        for symbol in _collect_symbols_info(env, elffile, elf_path, sections):
            file_path, _ = symbol.get("location").rsplit(":", 1)
            if not file_path or file_path.startswith("?"):
                file_path = "unknown"

            if not files.get(file_path, {}):
                files[file_path] = {
                    "symbols": [],
                    "ram_size": 0,
                    "flash_size": 0
                }

            symbol_size = symbol.get("size", 0)
            section = sections.get(symbol.get("section", ""), {})
            if _is_ram_section(section):
                files[file_path]['ram_size'] += symbol_size
            if _is_flash_section(section):
                files[file_path]['flash_size'] += symbol_size

            files[file_path]['symbols'].append(symbol)

        data['memory']['files'] = files

    with open(join(env.subst("$BUILD_DIR"), "sizedata.json"), "w") as fp:
        fp.write(dump_json_to_unicode(data))


def ConfigureSizeDataTarget(env):
    for flags_section in ("ASFLAGS", "CCFLAGS", "LINKFLAGS"):
        if not any("-g" in f for f in env.get(flags_section, [])):
            env.Prepend(**{flags_section: ["-g"]})


def exists(_):
    return True


def generate(env):
    env.AddMethod(DumpSizeData)
    env.AddMethod(ConfigureSizeDataTarget)
    return env
