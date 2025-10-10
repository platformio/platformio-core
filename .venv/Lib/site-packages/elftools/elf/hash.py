#-------------------------------------------------------------------------------
# elftools: elf/hash.py
#
# ELF hash table sections
#
# Andreas Ziegler (andreas.ziegler@fau.de)
# This code is in the public domain
#-------------------------------------------------------------------------------

import struct

from ..common.utils import struct_parse
from .sections import Section


class ELFHashTable(object):
    """ Representation of an ELF hash table to find symbols in the
        symbol table - useful for super-stripped binaries without section
        headers where only the start of the symbol table is known from the
        dynamic segment. The layout and contents are nicely described at
        https://flapenguin.me/2017/04/24/elf-lookup-dt-hash/.

        The symboltable argument needs to implement a get_symbol() method -
        in a regular ELF file, this will be the linked symbol table section
        as indicated by the sh_link attribute. For super-stripped binaries,
        one should use the DynamicSegment object as the symboltable as it
        supports symbol lookup without access to a symbol table section.
    """

    def __init__(self, elffile, start_offset, symboltable):
        self.elffile = elffile
        self._symboltable = symboltable
        self.params = struct_parse(self.elffile.structs.Elf_Hash,
                                   self.elffile.stream,
                                   start_offset)

    def get_number_of_symbols(self):
        """ Get the number of symbols from the hash table parameters.
        """
        return self.params['nchains']

    def get_symbol(self, name):
        """ Look up a symbol from this hash table with the given name.
        """
        if self.params['nbuckets'] == 0:
            return None
        hval = self.elf_hash(name) % self.params['nbuckets']
        symndx = self.params['buckets'][hval]
        while symndx != 0:
            sym = self._symboltable.get_symbol(symndx)
            if sym.name == name:
                return sym
            symndx = self.params['chains'][symndx]
        return None

    @staticmethod
    def elf_hash(name):
        """ Compute the hash value for a given symbol name.
        """
        if not isinstance(name, bytes):
            name = name.encode('utf-8')
        h = 0
        x = 0
        for c in bytearray(name):
            h = (h << 4) + c
            x = h & 0xF0000000
            if x != 0:
                h ^= (x >> 24)
            h &= ~x
        return h


class ELFHashSection(Section, ELFHashTable):
    """ Section representation of an ELF hash table. In regular ELF files, this
        allows us to use the common functions defined on Section objects when
        dealing with the hash table.
    """
    def __init__(self, header, name, elffile, symboltable):
        Section.__init__(self, header, name, elffile)
        ELFHashTable.__init__(self, elffile, self['sh_offset'], symboltable)


class GNUHashTable(object):
    """ Representation of a GNU hash table to find symbols in the
        symbol table - useful for super-stripped binaries without section
        headers where only the start of the symbol table is known from the
        dynamic segment. The layout and contents are nicely described at
        https://flapenguin.me/2017/05/10/elf-lookup-dt-gnu-hash/.

        The symboltable argument needs to implement a get_symbol() method -
        in a regular ELF file, this will be the linked symbol table section
        as indicated by the sh_link attribute. For super-stripped binaries,
        one should use the DynamicSegment object as the symboltable as it
        supports symbol lookup without access to a symbol table section.
    """
    def __init__(self, elffile, start_offset, symboltable):
        self.elffile = elffile
        self._symboltable = symboltable
        self.params = struct_parse(self.elffile.structs.Gnu_Hash,
                                   self.elffile.stream,
                                   start_offset)
        # Element sizes in the hash table
        self._wordsize = self.elffile.structs.Elf_word('').sizeof()
        self._xwordsize = self.elffile.structs.Elf_xword('').sizeof()
        self._chain_pos = start_offset + 4 * self._wordsize + \
            self.params['bloom_size'] * self._xwordsize + \
            self.params['nbuckets'] * self._wordsize

    def get_number_of_symbols(self):
        """ Get the number of symbols in the hash table by finding the bucket
            with the highest symbol index and walking to the end of its chain.
        """
        # Find highest index in buckets array
        max_idx = max(self.params['buckets'])
        if max_idx < self.params['symoffset']:
            return self.params['symoffset']

        # Position the stream at the start of the corresponding chain
        max_chain_pos = self._chain_pos + \
            (max_idx - self.params['symoffset']) * self._wordsize
        self.elffile.stream.seek(max_chain_pos)
        hash_format = '<I' if self.elffile.little_endian else '>I'

        # Walk the chain to its end (lowest bit is set)
        while True:
            cur_hash = struct.unpack(hash_format, self.elffile.stream.read(self._wordsize))[0]
            if cur_hash & 1:
                return max_idx + 1

            max_idx += 1

    def _matches_bloom(self, H1):
        """ Helper function to check if the given hash could be in the hash
            table by testing it against the bloom filter.
        """
        arch_bits = self.elffile.elfclass
        H2 = H1 >> self.params['bloom_shift']
        word_idx = int(H1 / arch_bits) % self.params['bloom_size']
        BITMASK = (1 << (H1 % arch_bits)) | (1 << (H2 % arch_bits))
        return (self.params['bloom'][word_idx] & BITMASK) == BITMASK

    def get_symbol(self, name):
        """ Look up a symbol from this hash table with the given name.
        """
        namehash = self.gnu_hash(name)
        if not self._matches_bloom(namehash):
            return None

        symidx = self.params['buckets'][namehash % self.params['nbuckets']]
        if symidx < self.params['symoffset']:
            return None

        self.elffile.stream.seek(self._chain_pos + (symidx - self.params['symoffset']) * self._wordsize)
        hash_format = '<I' if self.elffile.little_endian else '>I'
        while True:
            cur_hash = struct.unpack(hash_format, self.elffile.stream.read(self._wordsize))[0]
            if cur_hash | 1 == namehash | 1:
                symbol = self._symboltable.get_symbol(symidx)
                if name == symbol.name:
                    return symbol

            if cur_hash & 1:
                break
            symidx += 1
        return None

    @staticmethod
    def gnu_hash(key):
        """ Compute the GNU-style hash value for a given symbol name.
        """
        if not isinstance(key, bytes):
            key = key.encode('utf-8')
        h = 5381
        for c in bytearray(key):
            h = h * 33 + c
        return h & 0xFFFFFFFF


class GNUHashSection(Section, GNUHashTable):
    """ Section representation of a GNU hash table. In regular ELF files, this
        allows us to use the common functions defined on Section objects when
        dealing with the hash table.
    """
    def __init__(self, header, name, elffile, symboltable):
        Section.__init__(self, header, name, elffile)
        GNUHashTable.__init__(self, elffile, self['sh_offset'], symboltable)
