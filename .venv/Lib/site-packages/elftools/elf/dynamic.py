#-------------------------------------------------------------------------------
# elftools: elf/dynamic.py
#
# ELF Dynamic Tags
#
# Mike Frysinger (vapier@gentoo.org)
# This code is in the public domain
#-------------------------------------------------------------------------------
import itertools

from collections import defaultdict
from .hash import ELFHashTable, GNUHashTable
from .sections import Section, Symbol
from .enums import ENUM_D_TAG
from .segments import Segment
from .relocation import RelocationTable, RelrRelocationTable
from ..common.exceptions import ELFError
from ..common.utils import elf_assert, struct_parse, parse_cstring_from_stream


class _DynamicStringTable(object):
    """ Bare string table based on values found via ELF dynamic tags and
        loadable segments only.  Good enough for get_string() only.
    """
    def __init__(self, stream, table_offset):
        self._stream = stream
        self._table_offset = table_offset

    def get_string(self, offset):
        """ Get the string stored at the given offset in this string table.
        """
        s = parse_cstring_from_stream(self._stream, self._table_offset + offset)
        return s.decode('utf-8') if s else ''


class DynamicTag(object):
    """ Dynamic Tag object - representing a single dynamic tag entry from a
        dynamic section.

        Allows dictionary-like access to the dynamic structure. For special
        tags (those listed in the _HANDLED_TAGS set below), creates additional
        attributes for convenience. For example, .soname will contain the actual
        value of DT_SONAME (fetched from the dynamic symbol table).
    """
    _HANDLED_TAGS = frozenset(
        ['DT_NEEDED', 'DT_RPATH', 'DT_RUNPATH', 'DT_SONAME',
         'DT_SUNW_FILTER'])

    def __init__(self, entry, stringtable):
        if stringtable is None:
            raise ELFError('Creating DynamicTag without string table')
        self.entry = entry
        if entry.d_tag in self._HANDLED_TAGS:
            setattr(self, entry.d_tag[3:].lower(),
                    stringtable.get_string(self.entry.d_val))

    def __getitem__(self, name):
        """ Implement dict-like access to entries
        """
        return self.entry[name]

    def __repr__(self):
        return '<DynamicTag (%s): %r>' % (self.entry.d_tag, self.entry)

    def __str__(self):
        if self.entry.d_tag in self._HANDLED_TAGS:
            s = '"%s"' % getattr(self, self.entry.d_tag[3:].lower())
        else:
            s = '%#x' % self.entry.d_ptr
        return '<DynamicTag (%s) %s>' % (self.entry.d_tag, s)


class Dynamic(object):
    """ Shared functionality between dynamic sections and segments.
    """
    def __init__(self, stream, elffile, stringtable, position, empty):
        """
        stream:
            The file-like object from which to load data

        elffile:
            The parent elffile object

        stringtable:
            A stringtable reference to use for parsing string references in
            entries

        position:
            The file offset of the dynamic segment/section

        empty:
            Whether this is a degenerate case with zero entries. Normally, every
            dynamic table will have at least one entry, the DT_NULL terminator.
        """
        self.elffile = elffile
        self.elfstructs = elffile.structs
        self._stream = stream
        self._num_tags = -1 if not empty else 0
        self._offset = position
        self._tagsize = self.elfstructs.Elf_Dyn.sizeof()
        self._empty = empty

        # Do not access this directly yourself; use _get_stringtable() instead.
        self._stringtable = stringtable

    def get_table_offset(self, tag_name):
        """ Return the virtual address and file offset of a dynamic table.
        """
        ptr = None
        for tag in self._iter_tags(type=tag_name):
            ptr = tag['d_ptr']
            break

        # If we found a virtual address, locate the offset in the file
        # by using the program headers.
        offset = None
        if ptr:
            offset = next(self.elffile.address_offsets(ptr), None)

        return ptr, offset

    def _get_stringtable(self):
        """ Return a string table for looking up dynamic tag related strings.

            This won't be a "full" string table object, but will at least
            support the get_string() function.
        """
        if self._stringtable:
            return self._stringtable

        # If the ELF has stripped its section table (which is unusual, but
        # perfectly valid), we need to use the dynamic tags to locate the
        # dynamic string table.
        _, table_offset = self.get_table_offset('DT_STRTAB')
        if table_offset is not None:
            self._stringtable = _DynamicStringTable(self._stream, table_offset)
            return self._stringtable

        # That didn't work for some reason.  Let's use the section header
        # even though this ELF is super weird.
        self._stringtable = self.elffile.get_section_by_name('.dynstr')
        return self._stringtable

    def _iter_tags(self, type=None):
        """ Yield all raw tags (limit to |type| if specified)
        """
        if self._empty:
            return
        for n in itertools.count():
            tag = self._get_tag(n)
            if type is None or tag['d_tag'] == type:
                yield tag
            if tag['d_tag'] == 'DT_NULL':
                break

    def iter_tags(self, type=None):
        """ Yield all tags (limit to |type| if specified)
        """
        for tag in self._iter_tags(type=type):
            yield DynamicTag(tag, self._get_stringtable())

    def _get_tag(self, n):
        """ Get the raw tag at index #n from the file
        """
        if self._num_tags != -1 and n >= self._num_tags:
            raise IndexError(n)
        offset = self._offset + n * self._tagsize
        return struct_parse(
            self.elfstructs.Elf_Dyn,
            self._stream,
            stream_pos=offset)

    def get_tag(self, n):
        """ Get the tag at index #n from the file (DynamicTag object)
        """
        return DynamicTag(self._get_tag(n), self._get_stringtable())

    def num_tags(self):
        """ Number of dynamic tags in the file, including the DT_NULL tag
        """
        if self._num_tags != -1:
            return self._num_tags

        for n in itertools.count():
            tag = self.get_tag(n)
            if tag.entry.d_tag == 'DT_NULL':
                self._num_tags = n + 1
                return self._num_tags

    def get_relocation_tables(self):
        """ Load all available relocation tables from DYNAMIC tags.

            Returns a dictionary mapping found table types (REL, RELA,
            RELR, JMPREL) to RelocationTable objects.
        """

        result = {}

        if list(self.iter_tags('DT_REL')):
            result['REL'] = RelocationTable(self.elffile,
                self.get_table_offset('DT_REL')[1],
                next(self.iter_tags('DT_RELSZ'))['d_val'], False)

            relentsz = next(self.iter_tags('DT_RELENT'))['d_val']
            elf_assert(result['REL'].entry_size == relentsz,
                'Expected DT_RELENT to be %s' % relentsz)

        if list(self.iter_tags('DT_RELA')):
            result['RELA'] = RelocationTable(self.elffile,
                self.get_table_offset('DT_RELA')[1],
                next(self.iter_tags('DT_RELASZ'))['d_val'], True)

            relentsz = next(self.iter_tags('DT_RELAENT'))['d_val']
            elf_assert(result['RELA'].entry_size == relentsz,
                'Expected DT_RELAENT to be %s' % relentsz)

        if list(self.iter_tags('DT_RELR')):
            result['RELR'] = RelrRelocationTable(self.elffile,
                self.get_table_offset('DT_RELR')[1],
                next(self.iter_tags('DT_RELRSZ'))['d_val'],
                next(self.iter_tags('DT_RELRENT'))['d_val'])

        if list(self.iter_tags('DT_JMPREL')):
            result['JMPREL'] = RelocationTable(self.elffile,
                self.get_table_offset('DT_JMPREL')[1],
                next(self.iter_tags('DT_PLTRELSZ'))['d_val'],
                next(self.iter_tags('DT_PLTREL'))['d_val'] == ENUM_D_TAG['DT_RELA'])

        return result


class DynamicSection(Section, Dynamic):
    """ ELF dynamic table section.  Knows how to process the list of tags.
    """
    def __init__(self, header, name, elffile):
        Section.__init__(self, header, name, elffile)
        stringtable = elffile.get_section(header['sh_link'], ('SHT_STRTAB', 'SHT_NOBITS'))
        Dynamic.__init__(self, self.stream, self.elffile, stringtable,
            self['sh_offset'], self['sh_type'] == 'SHT_NOBITS')


class DynamicSegment(Segment, Dynamic):
    """ ELF dynamic table segment.  Knows how to process the list of tags.
    """
    def __init__(self, header, stream, elffile):
        # The string table section to be used to resolve string names in
        # the dynamic tag array is the one pointed at by the sh_link field
        # of the dynamic section header.
        # So we must look for the dynamic section contained in the dynamic
        # segment, we do so by searching for the dynamic section whose content
        # is located at the same offset as the dynamic segment
        stringtable = None
        for section in elffile.iter_sections():
            if (isinstance(section, DynamicSection) and
                    section['sh_offset'] == header['p_offset']):
                stringtable = elffile.get_section(section['sh_link'])
                break
        Segment.__init__(self, header, stream)
        Dynamic.__init__(self, stream, elffile, stringtable, self['p_offset'],
             self['p_filesz'] == 0)
        self._symbol_size = self.elfstructs.Elf_Sym.sizeof()
        self._num_symbols = None
        self._symbol_name_map = None

    def num_symbols(self):
        """ Number of symbols in the table recovered from DT_SYMTAB
        """
        if self._num_symbols is not None:
            return self._num_symbols

        # Check if a DT_GNU_HASH tag exists and recover the number of symbols
        # from the corresponding hash table
        _, gnu_hash_offset = self.get_table_offset('DT_GNU_HASH')
        if gnu_hash_offset is not None:
            hash_section = GNUHashTable(self.elffile, gnu_hash_offset, self)
            self._num_symbols = hash_section.get_number_of_symbols()

        # If DT_GNU_HASH did not exist, maybe we can use DT_HASH
        if self._num_symbols is None:
            _, hash_offset = self.get_table_offset('DT_HASH')
            if hash_offset is not None:
                # Get the hash table from the DT_HASH offset
                hash_section = ELFHashTable(self.elffile, hash_offset, self)
                self._num_symbols = hash_section.get_number_of_symbols()

        if self._num_symbols is None:
            # Find closest higher pointer than tab_ptr. We'll use that to mark
            # the end of the symbol table.
            tab_ptr, tab_offset = self.get_table_offset('DT_SYMTAB')
            if tab_ptr is None or tab_offset is None:
                raise ELFError('Segment does not contain DT_SYMTAB.')
            nearest_ptr = None
            for tag in self.iter_tags():
                tag_ptr = tag['d_ptr']
                if tag['d_tag'] == 'DT_SYMENT':
                    if self._symbol_size != tag['d_val']:
                        # DT_SYMENT is the size of one symbol entry. It must be
                        # the same as returned by Elf_Sym.sizeof.
                        raise ELFError('DT_SYMENT (%d) != Elf_Sym (%d).' %
                                       (tag['d_val'], self._symbol_size))
                if (tag_ptr > tab_ptr and
                        (nearest_ptr is None or nearest_ptr > tag_ptr)):
                    nearest_ptr = tag_ptr

            if nearest_ptr is None:
                # Use the end of segment that contains DT_SYMTAB.
                for segment in self.elffile.iter_segments():
                    if (segment['p_vaddr'] <= tab_ptr and
                            tab_ptr <= (segment['p_vaddr'] + segment['p_filesz'])):
                        nearest_ptr = segment['p_vaddr'] + segment['p_filesz']

            end_ptr = nearest_ptr
            self._num_symbols = (end_ptr - tab_ptr) // self._symbol_size

        if self._num_symbols is None:
            raise ELFError('Cannot determine the end of DT_SYMTAB.')

        return self._num_symbols

    def get_symbol(self, index):
        """ Get the symbol at index #index from the table (Symbol object)
        """
        tab_ptr, tab_offset = self.get_table_offset('DT_SYMTAB')
        if tab_ptr is None or tab_offset is None:
            raise ELFError('Segment does not contain DT_SYMTAB.')

        symbol = struct_parse(
            self.elfstructs.Elf_Sym,
            self._stream,
            stream_pos=tab_offset + index * self._symbol_size)

        string_table = self._get_stringtable()
        symbol_name = string_table.get_string(symbol["st_name"])

        return Symbol(symbol, symbol_name)

    def get_symbol_by_name(self, name):
        """ Get a symbol(s) by name. Return None if no symbol by the given name
            exists.
        """
        # The first time this method is called, construct a name to number
        # mapping
        #
        if self._symbol_name_map is None:
            self._symbol_name_map = defaultdict(list)
            for i, sym in enumerate(self.iter_symbols()):
                self._symbol_name_map[sym.name].append(i)
        symnums = self._symbol_name_map.get(name)
        return [self.get_symbol(i) for i in symnums] if symnums else None

    def iter_symbols(self):
        """ Yield all symbols in this dynamic segment. The symbols are usually
            the same as returned by SymbolTableSection.iter_symbols. However,
            in stripped binaries, SymbolTableSection might have been removed.
            This method reads from the mandatory dynamic tag DT_SYMTAB.
        """
        for i in range(self.num_symbols()):
            yield(self.get_symbol(i))
