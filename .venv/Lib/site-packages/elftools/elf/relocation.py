#-------------------------------------------------------------------------------
# elftools: elf/relocation.py
#
# ELF relocations
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from collections import namedtuple

from ..common.exceptions import ELFRelocationError
from ..common.utils import elf_assert, struct_parse
from .sections import Section
from .enums import (
    ENUM_RELOC_TYPE_i386, ENUM_RELOC_TYPE_x64, ENUM_RELOC_TYPE_MIPS,
    ENUM_RELOC_TYPE_ARM, ENUM_RELOC_TYPE_AARCH64, ENUM_RELOC_TYPE_PPC64,
    ENUM_RELOC_TYPE_S390X, ENUM_RELOC_TYPE_BPF, ENUM_RELOC_TYPE_LOONGARCH,
    ENUM_D_TAG)
from ..construct import Container


class Relocation(object):
    """ Relocation object - representing a single relocation entry. Allows
        dictionary-like access to the entry's fields.

        Can be either a REL or RELA relocation.
    """
    def __init__(self, entry, elffile):
        self.entry = entry
        self.elffile = elffile

    def is_RELA(self):
        """ Is this a RELA relocation? If not, it's REL.
        """
        return 'r_addend' in self.entry

    def __getitem__(self, name):
        """ Dict-like access to entries
        """
        return self.entry[name]

    def __repr__(self):
        return '<Relocation (%s): %s>' % (
                'RELA' if self.is_RELA() else 'REL',
                self.entry)

    def __str__(self):
        return self.__repr__()


class RelocationTable(object):
    """ Shared functionality between relocation sections and relocation tables
    """

    def __init__(self, elffile, offset, size, is_rela):
        self._stream = elffile.stream
        self._elffile = elffile
        self._elfstructs = elffile.structs
        self._size = size
        self._offset = offset
        self._is_rela = is_rela

        if is_rela:
            self.entry_struct = self._elfstructs.Elf_Rela
        else:
            self.entry_struct = self._elfstructs.Elf_Rel

        self.entry_size = self.entry_struct.sizeof()

    def is_RELA(self):
        """ Is this a RELA relocation section? If not, it's REL.
        """
        return self._is_rela

    def num_relocations(self):
        """ Number of relocations in the section
        """
        return self._size // self.entry_size

    def get_relocation(self, n):
        """ Get the relocation at index #n from the section (Relocation object)
        """
        entry_offset = self._offset + n * self.entry_size
        entry = struct_parse(
            self.entry_struct,
            self._stream,
            stream_pos=entry_offset)
        return Relocation(entry, self._elffile)

    def iter_relocations(self):
        """ Yield all the relocations in the section
        """
        for i in range(self.num_relocations()):
            yield self.get_relocation(i)


class RelocationSection(Section, RelocationTable):
    """ ELF relocation section. Serves as a collection of Relocation entries.
    """
    def __init__(self, header, name, elffile):
        Section.__init__(self, header, name, elffile)
        RelocationTable.__init__(self, self.elffile,
            self['sh_offset'], self['sh_size'], header['sh_type'] == 'SHT_RELA')

        elf_assert(header['sh_type'] in ('SHT_REL', 'SHT_RELA'),
            'Unknown relocation type section')
        elf_assert(header['sh_entsize'] == self.entry_size,
            'Expected sh_entsize of %s section to be %s' % (
                header['sh_type'], self.entry_size))


class RelrRelocationTable(object):
    """ RELR compressed relocation table. This stores relative relocations
        in a compressed format. An entry with an even value serves as an
        'anchor' that defines a base address. Following this entry are one or
        more bitmaps for consecutive addresses after the anchor which determine
        if the corresponding relocation exists (if the bit is 1) or if it is
        skipped. Addends are stored at the respective addresses (as in REL
        relocations).
    """

    def __init__(self, elffile, offset, size, entrysize):
        self._elffile = elffile
        self._offset = offset
        self._size = size
        self._relr_struct = self._elffile.structs.Elf_Relr
        self._entrysize = self._relr_struct.sizeof()
        self._cached_relocations = None

        elf_assert(self._entrysize == entrysize,
            'Expected RELR entry size to be %s, got %s' % (
                self._entrysize, entrysize))

    def iter_relocations(self):
        """ Yield all the relocations in the section
        """

        # If DT_RELRSZ is zero, offset is meaningless and could be None.
        if self._size == 0:
            return []

        limit = self._offset + self._size
        relr = self._offset
        # The addresses of relocations in a bitmap are calculated from a base
        # value provided in an initial 'anchor' relocation.
        base = None
        while relr < limit:
            entry = struct_parse(self._relr_struct,
                                 self._elffile.stream,
                                 stream_pos=relr)
            entry_offset = entry['r_offset']
            if (entry_offset & 1) == 0:
                # We found an anchor, take the current value as the base address
                # for the following bitmaps and move the 'where' pointer to the
                # beginning of the first bitmap.
                base = entry_offset
                base += self._entrysize
                yield Relocation(entry, self._elffile)
            else:
                # We're processing a bitmap.
                elf_assert(base is not None, 'RELR bitmap without base address')
                i = 0
                while True:
                    # Iterate over all bits except the least significant one.
                    entry_offset = (entry_offset >> 1)
                    if entry_offset == 0:
                        break
                    # if the current LSB is set, we have a relocation at the
                    # corresponding address so generate a Relocation with the
                    # matching offset
                    if (entry_offset & 1) != 0:
                        calc_offset = base + i * self._entrysize
                        yield Relocation(Container(r_offset = calc_offset),
                                         self._elffile)
                    i += 1
                # Advance 'base' past the current bitmap (8 == CHAR_BIT). There
                # are 63 (or 31 for 32-bit ELFs) entries in each bitmap, and
                # every bit corresponds to an ELF_addr-sized relocation.
                base += (8 * self._entrysize - 1) * self._elffile.structs.Elf_addr('').sizeof()
            # Advance to the next entry
            relr += self._entrysize

    def num_relocations(self):
        """ Number of relocations in the section
        """
        if self._cached_relocations is None:
            self._cached_relocations = list(self.iter_relocations())
        return len(self._cached_relocations)

    def get_relocation(self, n):
        """ Get the relocation at index #n from the section (Relocation object)
        """
        if self._cached_relocations is None:
            self._cached_relocations = list(self.iter_relocations())
        return self._cached_relocations[n]


class RelrRelocationSection(Section, RelrRelocationTable):
    """ ELF RELR relocation section. Serves as a collection of RELR relocation entries.
    """
    def __init__(self, header, name, elffile):
        Section.__init__(self, header, name, elffile)
        RelrRelocationTable.__init__(self, self.elffile,
            self['sh_offset'], self['sh_size'], self['sh_entsize'])


class RelocationHandler(object):
    """ Handles the logic of relocations in ELF files.
    """
    def __init__(self, elffile):
        self.elffile = elffile

    def find_relocations_for_section(self, section):
        """ Given a section, find the relocation section for it in the ELF
            file. Return a RelocationSection object, or None if none was
            found.
        """
        reloc_section_names = (
                '.rel' + section.name,
                '.rela' + section.name)
        # Find the relocation section aimed at this one. Currently assume
        # that either .rel or .rela section exists for this section, but
        # not both.
        for relsection in self.elffile.iter_sections():
            if (    isinstance(relsection, RelocationSection) and
                    relsection.name in reloc_section_names):
                return relsection
        return None

    def apply_section_relocations(self, stream, reloc_section):
        """ Apply all relocations in reloc_section (a RelocationSection object)
            to the given stream, that contains the data of the section that is
            being relocated. The stream is modified as a result.
        """
        # The symbol table associated with this relocation section
        symtab = self.elffile.get_section(reloc_section['sh_link'])
        for reloc in reloc_section.iter_relocations():
            self._do_apply_relocation(stream, reloc, symtab)

    def _do_apply_relocation(self, stream, reloc, symtab):
        # Preparations for performing the relocation: obtain the value of
        # the symbol mentioned in the relocation, as well as the relocation
        # recipe which tells us how to actually perform it.
        # All peppered with some sanity checking.
        if reloc['r_info_sym'] >= symtab.num_symbols():
            raise ELFRelocationError(
                'Invalid symbol reference in relocation: index %s' % (
                    reloc['r_info_sym']))
        sym_value = symtab.get_symbol(reloc['r_info_sym'])['st_value']

        reloc_type = reloc['r_info_type']
        recipe = None

        if self.elffile.get_machine_arch() == 'x86':
            if reloc.is_RELA():
                raise ELFRelocationError(
                    'Unexpected RELA relocation for x86: %s' % reloc)
            recipe = self._RELOCATION_RECIPES_X86.get(reloc_type, None)
        elif self.elffile.get_machine_arch() == 'x64':
            if not reloc.is_RELA():
                raise ELFRelocationError(
                    'Unexpected REL relocation for x64: %s' % reloc)
            recipe = self._RELOCATION_RECIPES_X64.get(reloc_type, None)
        elif self.elffile.get_machine_arch() == 'MIPS':
            if reloc.is_RELA():
                if reloc_type == ENUM_RELOC_TYPE_MIPS['R_MIPS_64']:
                    if reloc['r_type2'] != 0 or reloc['r_type3'] != 0 or reloc['r_ssym'] != 0:
                        raise ELFRelocationError(
                            'Multiple relocations in R_MIPS_64 are not implemented: %s' % reloc)
                recipe = self._RELOCATION_RECIPES_MIPS_RELA.get(reloc_type, None)
            else:
                recipe = self._RELOCATION_RECIPES_MIPS_REL.get(reloc_type, None)
        elif self.elffile.get_machine_arch() == 'ARM':
            if reloc.is_RELA():
                raise ELFRelocationError(
                    'Unexpected RELA relocation for ARM: %s' % reloc)
            recipe = self._RELOCATION_RECIPES_ARM.get(reloc_type, None)
        elif self.elffile.get_machine_arch() == 'AArch64':
            recipe = self._RELOCATION_RECIPES_AARCH64.get(reloc_type, None)
        elif self.elffile.get_machine_arch() == '64-bit PowerPC':
            recipe = self._RELOCATION_RECIPES_PPC64.get(reloc_type, None)
        elif self.elffile.get_machine_arch() == 'IBM S/390':
            recipe = self._RELOCATION_RECIPES_S390X.get(reloc_type, None)
        elif self.elffile.get_machine_arch() == 'Linux BPF - in-kernel virtual machine':
            recipe = self._RELOCATION_RECIPES_EBPF.get(reloc_type, None)
        elif self.elffile.get_machine_arch() == 'LoongArch':
            if not reloc.is_RELA():
                raise ELFRelocationError(
                    'Unexpected REL relocation for LoongArch: %s' % reloc)
            recipe = self._RELOCATION_RECIPES_LOONGARCH.get(reloc_type, None)

        if recipe is None:
            raise ELFRelocationError(
                    'Unsupported relocation type: %s' % reloc_type)

        # So now we have everything we need to actually perform the relocation.
        # Let's get to it:

        # 0. Find out which struct we're going to be using to read this value
        #    from the stream and write it back.
        if recipe.bytesize == 4:
            value_struct = self.elffile.structs.Elf_word('')
        elif recipe.bytesize == 8:
            value_struct = self.elffile.structs.Elf_word64('')
        elif recipe.bytesize == 1:
            value_struct = self.elffile.structs.Elf_byte('')
        elif recipe.bytesize == 2:
            value_struct = self.elffile.structs.Elf_half('')
        else:
            raise ELFRelocationError('Invalid bytesize %s for relocation' %
                    recipe.bytesize)

        # 1. Read the value from the stream (with correct size and endianness)
        original_value = struct_parse(
            value_struct,
            stream,
            stream_pos=reloc['r_offset'])
        # 2. Apply the relocation to the value, acting according to the recipe
        relocated_value = recipe.calc_func(
            value=original_value,
            sym_value=sym_value,
            offset=reloc['r_offset'],
            addend=reloc['r_addend'] if recipe.has_addend else 0)
        # 3. Write the relocated value back into the stream
        stream.seek(reloc['r_offset'])

        # Make sure the relocated value fits back by wrapping it around. This
        # looks like a problem, but it seems to be the way this is done in
        # binutils too.
        relocated_value = relocated_value % (2 ** (recipe.bytesize * 8))
        value_struct.build_stream(relocated_value, stream)

    # Relocations are represented by "recipes". Each recipe specifies:
    #  bytesize: The number of bytes to read (and write back) to the section.
    #            This is the unit of data on which relocation is performed.
    #  has_addend: Does this relocation have an extra addend?
    #  calc_func: A function that performs the relocation on an extracted
    #             value, and returns the updated value.
    #
    _RELOCATION_RECIPE_TYPE = namedtuple('_RELOCATION_RECIPE_TYPE',
        'bytesize has_addend calc_func')

    def _reloc_calc_identity(value, sym_value, offset, addend=0):
        return value

    def _reloc_calc_sym_plus_value(value, sym_value, offset, addend=0):
        return sym_value + value + addend

    def _reloc_calc_sym_plus_value_pcrel(value, sym_value, offset, addend=0):
        return sym_value + value - offset

    def _reloc_calc_sym_plus_addend(value, sym_value, offset, addend=0):
        return sym_value + addend

    def _reloc_calc_sym_plus_addend_pcrel(value, sym_value, offset, addend=0):
        return sym_value + addend - offset

    def _reloc_calc_value_minus_sym_addend(value, sym_value, offset, addend=0):
        return value - sym_value - addend

    def _arm_reloc_calc_sym_plus_value_pcrel(value, sym_value, offset, addend=0):
        return sym_value // 4 + value - offset // 4

    def _bpf_64_32_reloc_calc_sym_plus_addend(value, sym_value, offset, addend=0):
        return (sym_value + addend) // 8 - 1

    _RELOCATION_RECIPES_ARM = {
        ENUM_RELOC_TYPE_ARM['R_ARM_ABS32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=False,
            calc_func=_reloc_calc_sym_plus_value),
        ENUM_RELOC_TYPE_ARM['R_ARM_CALL']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=False,
            calc_func=_arm_reloc_calc_sym_plus_value_pcrel),
    }

    _RELOCATION_RECIPES_AARCH64 = {
        ENUM_RELOC_TYPE_AARCH64['R_AARCH64_ABS64']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=True, calc_func=_reloc_calc_sym_plus_addend),
        ENUM_RELOC_TYPE_AARCH64['R_AARCH64_ABS32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True, calc_func=_reloc_calc_sym_plus_addend),
        ENUM_RELOC_TYPE_AARCH64['R_AARCH64_PREL32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True,
            calc_func=_reloc_calc_sym_plus_addend_pcrel),
    }

    # https://dmz-portal.mips.com/wiki/MIPS_relocation_types
    _RELOCATION_RECIPES_MIPS_REL = {
        ENUM_RELOC_TYPE_MIPS['R_MIPS_NONE']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=False, calc_func=_reloc_calc_identity),
        ENUM_RELOC_TYPE_MIPS['R_MIPS_32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=False,
            calc_func=_reloc_calc_sym_plus_value),
    }
    _RELOCATION_RECIPES_MIPS_RELA = {
        ENUM_RELOC_TYPE_MIPS['R_MIPS_NONE']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True, calc_func=_reloc_calc_identity),
        ENUM_RELOC_TYPE_MIPS['R_MIPS_32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True,
            calc_func=_reloc_calc_sym_plus_value),
        ENUM_RELOC_TYPE_MIPS['R_MIPS_64']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=True,
            calc_func=_reloc_calc_sym_plus_value),
    }

    _RELOCATION_RECIPES_PPC64 = {
        ENUM_RELOC_TYPE_PPC64['R_PPC64_ADDR32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True, calc_func=_reloc_calc_sym_plus_addend),
        ENUM_RELOC_TYPE_PPC64['R_PPC64_REL32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True, calc_func=_reloc_calc_sym_plus_addend_pcrel),
        ENUM_RELOC_TYPE_PPC64['R_PPC64_ADDR64']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=True, calc_func=_reloc_calc_sym_plus_addend),
    }

    _RELOCATION_RECIPES_X86 = {
        ENUM_RELOC_TYPE_i386['R_386_NONE']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=False, calc_func=_reloc_calc_identity),
        ENUM_RELOC_TYPE_i386['R_386_32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=False,
            calc_func=_reloc_calc_sym_plus_value),
        ENUM_RELOC_TYPE_i386['R_386_PC32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=False,
            calc_func=_reloc_calc_sym_plus_value_pcrel),
    }

    _RELOCATION_RECIPES_X64 = {
        ENUM_RELOC_TYPE_x64['R_X86_64_NONE']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=True, calc_func=_reloc_calc_identity),
        ENUM_RELOC_TYPE_x64['R_X86_64_64']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=True, calc_func=_reloc_calc_sym_plus_addend),
        ENUM_RELOC_TYPE_x64['R_X86_64_PC32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True,
            calc_func=_reloc_calc_sym_plus_addend_pcrel),
        ENUM_RELOC_TYPE_x64['R_X86_64_32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True, calc_func=_reloc_calc_sym_plus_addend),
        ENUM_RELOC_TYPE_x64['R_X86_64_32S']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True, calc_func=_reloc_calc_sym_plus_addend),
    }

    # https://www.kernel.org/doc/html/latest/bpf/llvm_reloc.html#different-relocation-types
    _RELOCATION_RECIPES_EBPF = {
        ENUM_RELOC_TYPE_BPF['R_BPF_NONE']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=False, calc_func=_reloc_calc_identity),
        ENUM_RELOC_TYPE_BPF['R_BPF_64_64']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=False, calc_func=_reloc_calc_identity),
        ENUM_RELOC_TYPE_BPF['R_BPF_64_32']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=False, calc_func=_bpf_64_32_reloc_calc_sym_plus_addend),
        ENUM_RELOC_TYPE_BPF['R_BPF_64_NODYLD32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=False, calc_func=_reloc_calc_identity),
        ENUM_RELOC_TYPE_BPF['R_BPF_64_ABS64']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=False, calc_func=_reloc_calc_identity),
        ENUM_RELOC_TYPE_BPF['R_BPF_64_ABS32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=False, calc_func=_reloc_calc_identity),
    }

    # https://github.com/loongson/la-abi-specs/blob/release/laelf.adoc
    _RELOCATION_RECIPES_LOONGARCH = {
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_NONE']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=False, calc_func=_reloc_calc_identity),
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True,
            calc_func=_reloc_calc_sym_plus_addend),
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_64']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=True,
            calc_func=_reloc_calc_sym_plus_addend),
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_ADD8']: _RELOCATION_RECIPE_TYPE(
            bytesize=1, has_addend=True,
            calc_func=_reloc_calc_sym_plus_value),
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_SUB8']: _RELOCATION_RECIPE_TYPE(
            bytesize=1, has_addend=True,
            calc_func=_reloc_calc_value_minus_sym_addend),
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_ADD16']: _RELOCATION_RECIPE_TYPE(
            bytesize=2, has_addend=True,
            calc_func=_reloc_calc_sym_plus_value),
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_SUB16']: _RELOCATION_RECIPE_TYPE(
            bytesize=2, has_addend=True,
            calc_func=_reloc_calc_value_minus_sym_addend),
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_ADD32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True,
            calc_func=_reloc_calc_sym_plus_value),
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_SUB32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True,
            calc_func=_reloc_calc_value_minus_sym_addend),
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_ADD64']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=True,
            calc_func=_reloc_calc_sym_plus_value),
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_SUB64']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=True,
            calc_func=_reloc_calc_value_minus_sym_addend),
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_32_PCREL']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True,
            calc_func=_reloc_calc_sym_plus_addend_pcrel),
        ENUM_RELOC_TYPE_LOONGARCH['R_LARCH_64_PCREL']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=True,
            calc_func=_reloc_calc_sym_plus_addend_pcrel),
    }

    _RELOCATION_RECIPES_S390X = {
        ENUM_RELOC_TYPE_S390X['R_390_32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True, calc_func=_reloc_calc_sym_plus_addend),
        ENUM_RELOC_TYPE_S390X['R_390_PC32']: _RELOCATION_RECIPE_TYPE(
            bytesize=4, has_addend=True, calc_func=_reloc_calc_sym_plus_addend_pcrel),
        ENUM_RELOC_TYPE_S390X['R_390_64']: _RELOCATION_RECIPE_TYPE(
            bytesize=8, has_addend=True, calc_func=_reloc_calc_sym_plus_addend),
    }


