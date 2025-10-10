#------------------------------------------------------------------------------
# elftools: elf/gnuversions.py
#
# ELF sections
#
# Yann Rouillard (yann@pleiades.fr.eu.org)
# This code is in the public domain
#------------------------------------------------------------------------------
from ..construct import CString
from ..common.utils import struct_parse, elf_assert
from .sections import Section, Symbol


class Version(object):
    """ Version object - representing a version definition or dependency
        entry from a "Version Needed" or a "Version Dependency" table section.

        This kind of entry contains a pointer to an array of auxiliary entries
        that store the information about version names or dependencies.
        These entries are not stored in this object and should be accessed
        through the appropriate method of a section object which will return
        an iterator of VersionAuxiliary objects.

        Similarly to Section objects, allows dictionary-like access to
        verdef/verneed entry
    """
    def __init__(self, entry, name=None):
        self.entry = entry
        self.name = name

    def __getitem__(self, name):
        """ Implement dict-like access to entry
        """
        return self.entry[name]


class VersionAuxiliary(object):
    """ Version Auxiliary object - representing an auxiliary entry of a version
        definition or dependency entry

        Similarly to Section objects, allows dictionary-like access to the
        verdaux/vernaux entry
    """
    def __init__(self, entry, name):
        self.entry = entry
        self.name = name

    def __getitem__(self, name):
        """ Implement dict-like access to entries
        """
        return self.entry[name]


class GNUVersionSection(Section):
    """ Common ancestor class for ELF SUNW|GNU Version Needed/Dependency
        sections class which contains shareable code
    """

    def __init__(self, header, name, elffile, stringtable,
                 field_prefix, version_struct, version_auxiliaries_struct):
        super(GNUVersionSection, self).__init__(header, name, elffile)
        self.stringtable = stringtable
        self.field_prefix = field_prefix
        self.version_struct = version_struct
        self.version_auxiliaries_struct = version_auxiliaries_struct

    def num_versions(self):
        """ Number of version entries in the section
        """
        return self['sh_info']

    def _field_name(self, name, auxiliary=False):
        """ Return the real field's name of version or a version auxiliary
            entry
        """
        middle = 'a_' if auxiliary else '_'
        return self.field_prefix + middle + name

    def _iter_version_auxiliaries(self, entry_offset, count):
        """ Yield all auxiliary entries of a version entry
        """
        name_field = self._field_name('name', auxiliary=True)
        next_field = self._field_name('next', auxiliary=True)

        for _ in range(count):
            entry = struct_parse(
                        self.version_auxiliaries_struct,
                        self.stream,
                        stream_pos=entry_offset)

            name = self.stringtable.get_string(entry[name_field])
            version_aux = VersionAuxiliary(entry, name)
            yield version_aux

            entry_offset += entry[next_field]

    def iter_versions(self):
        """ Yield all the version entries in the section
            Each time it returns the main version structure
            and an iterator to walk through its auxiliaries entries
        """
        aux_field = self._field_name('aux')
        count_field = self._field_name('cnt')
        next_field = self._field_name('next')

        entry_offset = self['sh_offset']
        for _ in range(self.num_versions()):
            entry = struct_parse(
                self.version_struct,
                self.stream,
                stream_pos=entry_offset)

            elf_assert(entry[count_field] > 0,
                'Expected number of version auxiliary entries (%s) to be > 0'
                'for the following version entry: %s' % (
                    count_field, str(entry)))

            version = Version(entry)
            aux_entries_offset = entry_offset + entry[aux_field]
            version_auxiliaries_iter = self._iter_version_auxiliaries(
                    aux_entries_offset, entry[count_field])

            yield version, version_auxiliaries_iter

            entry_offset += entry[next_field]


class GNUVerNeedSection(GNUVersionSection):
    """ ELF SUNW or GNU Version Needed table section.
        Has an associated StringTableSection that's passed in the constructor.
    """
    def __init__(self, header, name, elffile, stringtable):
        super(GNUVerNeedSection, self).__init__(
                header, name, elffile, stringtable, 'vn',
                elffile.structs.Elf_Verneed, elffile.structs.Elf_Vernaux)
        self._has_indexes = None

    def has_indexes(self):
        """ Return True if at least one version definition entry has an index
            that is stored in the vna_other field.
            This information is used for symbol versioning
        """
        if self._has_indexes is None:
            self._has_indexes = False
            for _, vernaux_iter in self.iter_versions():
                for vernaux in vernaux_iter:
                    if vernaux['vna_other']:
                        self._has_indexes = True
                        break

        return self._has_indexes

    def iter_versions(self):
        for verneed, vernaux in super(GNUVerNeedSection, self).iter_versions():
            verneed.name = self.stringtable.get_string(verneed['vn_file'])
            yield verneed, vernaux

    def get_version(self, index):
        """ Get the version information located at index #n in the table
            Return boths the verneed structure and the vernaux structure
            that contains the name of the version
        """
        for verneed, vernaux_iter in self.iter_versions():
            for vernaux in vernaux_iter:
                if vernaux['vna_other'] == index:
                    return verneed, vernaux

        return None


class GNUVerDefSection(GNUVersionSection):
    """ ELF SUNW or GNU Version Definition table section.
        Has an associated StringTableSection that's passed in the constructor.
    """
    def __init__(self, header, name, elffile, stringtable):
        super(GNUVerDefSection, self).__init__(
                header, name, elffile, stringtable, 'vd',
                elffile.structs.Elf_Verdef, elffile.structs.Elf_Verdaux)

    def get_version(self, index):
        """ Get the version information located at index #n in the table
            Return boths the verdef structure and an iterator to retrieve
            both the version names and dependencies in the form of
            verdaux entries
        """
        for verdef, verdaux_iter in self.iter_versions():
            if verdef['vd_ndx'] == index:
                return verdef, verdaux_iter

        return None


class GNUVerSymSection(Section):
    """ ELF SUNW or GNU Versym table section.
        Has an associated SymbolTableSection that's passed in the constructor.
    """
    def __init__(self, header, name, elffile, symboltable):
        super(GNUVerSymSection, self).__init__(header, name, elffile)
        self.symboltable = symboltable

    def num_symbols(self):
        """ Number of symbols in the table
        """
        return self['sh_size'] // self['sh_entsize']

    def get_symbol(self, n):
        """ Get the symbol at index #n from the table (Symbol object)
            It begins at 1 and not 0 since the first entry is used to
            store the current version of the syminfo table
        """
        # Grab the symbol's entry from the stream
        entry_offset = self['sh_offset'] + n * self['sh_entsize']
        entry = struct_parse(
            self.structs.Elf_Versym,
            self.stream,
            stream_pos=entry_offset)
        # Find the symbol name in the associated symbol table
        name = self.symboltable.get_symbol(n).name
        return Symbol(entry, name)

    def iter_symbols(self):
        """ Yield all the symbols in the table
        """
        for i in range(self.num_symbols()):
            yield self.get_symbol(i)
