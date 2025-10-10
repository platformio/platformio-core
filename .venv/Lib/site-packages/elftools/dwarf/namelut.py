#-------------------------------------------------------------------------------
# elftools: dwarf/namelut.py
#
# DWARF pubtypes/pubnames section decoding (.debug_pubtypes, .debug_pubnames)
#
# Vijay Ramasami (rvijayc@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os
import collections
from collections import OrderedDict
from collections.abc import Mapping
from ..common.utils import struct_parse
from bisect import bisect_right
import math
from ..construct import CString, Struct, If

NameLUTEntry = collections.namedtuple('NameLUTEntry', 'cu_ofs die_ofs')

class NameLUT(Mapping):
    """
    A "Name LUT" holds any of the tables specified by .debug_pubtypes or
    .debug_pubnames sections. This is basically a dictionary where the key is
    the symbol name (either a public variable, function or a type), and the
    value is the tuple (cu_offset, die_offset) corresponding to the variable.
    The die_offset is an absolute offset (meaning, it can be used to search the
    CU by iterating until a match is obtained).

    An ordered dictionary is used to preserve the CU order (i.e, items are
    stored on a per-CU basis (as it was originally in the .debug_* section).

    Usage:

    The NameLUT walks and talks like a dictionary and hence it can be used as
    such. Some examples below:

    # get the pubnames (a NameLUT from DWARF info).
    pubnames = dwarf_info.get_pubnames()

    # lookup a variable.
    entry1 = pubnames["var_name1"]
    entry2 = pubnames.get("var_name2", default=<default_var>)
    print(entry2.cu_ofs)
    ...

    # iterate over items.
    for (name, entry) in pubnames.items():
      # do stuff with name, entry.cu_ofs, entry.die_ofs

    # iterate over items on a per-CU basis.
    import itertools
    for cu_ofs, item_list in itertools.groupby(pubnames.items(),
        key = lambda x: x[1].cu_ofs):
      # items are now grouped by cu_ofs.
      # item_list is an iterator yeilding NameLUTEntry'ies belonging
      # to cu_ofs.
      # We can parse the CU at cu_offset and use the parsed CU results
      # to parse the pubname DIEs in the CU listed by item_list.
      for item in item_list:
        # work with item which is part of the CU with cu_ofs.

    """

    def __init__(self, stream, size, structs):

        self._stream = stream
        self._size = size
        self._structs = structs
        # entries are lazily loaded on demand.
        self._entries = None
        # CU headers (for readelf).
        self._cu_headers = None

    def get_entries(self):
        """
        Returns the parsed NameLUT entries. The returned object is a dictionary
        with the symbol name as the key and NameLUTEntry(cu_ofs, die_ofs) as
        the value.

        This is useful when dealing with very large ELF files with millions of
        entries. The returned entries can be pickled to a file and restored by
        calling set_entries on subsequent loads.
        """
        if self._entries is None:
            self._entries, self._cu_headers = self._get_entries()
        return self._entries

    def set_entries(self, entries, cu_headers):
        """
        Set the NameLUT entries from an external source. The input is a
        dictionary with the symbol name as the key and NameLUTEntry(cu_ofs,
        die_ofs) as the value.

        This option is useful when dealing with very large ELF files with
        millions of entries. The entries can be parsed once and pickled to a
        file and can be restored via this function on subsequent loads.
        """
        self._entries = entries
        self._cu_headers = cu_headers

    def __len__(self):
        """
        Returns the number of entries in the NameLUT.
        """
        if self._entries is None:
            self._entries, self._cu_headers = self._get_entries()
        return len(self._entries)

    def __getitem__(self, name):
        """
        Returns a namedtuple - NameLUTEntry(cu_ofs, die_ofs) - that corresponds
        to the given symbol name.
        """
        if self._entries is None:
            self._entries, self._cu_headers = self._get_entries()
        return self._entries.get(name)

    def __iter__(self):
        """
        Returns an iterator to the NameLUT dictionary.
        """
        if self._entries is None:
            self._entries, self._cu_headers = self._get_entries()
        return iter(self._entries)

    def items(self):
        """
        Returns the NameLUT dictionary items.
        """
        if self._entries is None:
            self._entries, self._cu_headers = self._get_entries()
        return self._entries.items()

    def get(self, name, default=None):
        """
        Returns NameLUTEntry(cu_ofs, die_ofs) for the provided symbol name or
        None if the symbol does not exist in the corresponding section.
        """
        if self._entries is None:
            self._entries, self._cu_headers = self._get_entries()
        return self._entries.get(name, default)

    def get_cu_headers(self):
        """
        Returns all CU headers. Mainly required for readelf.
        """
        if self._cu_headers is None:
            self._entries, self._cu_headers = self._get_entries()

        return self._cu_headers

    def _get_entries(self):
        """
        Parse the (name, cu_ofs, die_ofs) information from this section and
        store as a dictionary.
        """

        self._stream.seek(0)
        entries = OrderedDict()
        cu_headers = []
        offset = 0
        # According to 6.1.1. of DWARFv4, each set of names is terminated by
        # an offset field containing zero (and no following string). Because
        # of sequential parsing, every next entry may be that terminator.
        # So, field "name" is conditional.
        entry_struct = Struct("Dwarf_offset_name_pair",
                self._structs.Dwarf_offset('die_ofs'),
                If(lambda ctx: ctx['die_ofs'], CString('name')))

        # each run of this loop will fetch one CU worth of entries.
        while offset < self._size:

            # read the header for this CU.
            namelut_hdr = struct_parse(self._structs.Dwarf_nameLUT_header,
                    self._stream, offset)
            cu_headers.append(namelut_hdr)
            # compute the next offset.
            offset = (offset + namelut_hdr.unit_length +
                     self._structs.initial_length_field_size())

            # before inner loop, latch data that will be used in the inner
            # loop to avoid attribute access and other computation.
            hdr_cu_ofs = namelut_hdr.debug_info_offset

            # while die_ofs of the entry is non-zero (which indicates the end) ...
            while True:
                entry = struct_parse(entry_struct, self._stream)

                # if it is zero, this is the terminating record.
                if entry.die_ofs == 0:
                    break
                # add this entry to the look-up dictionary.
                entries[entry.name.decode('utf-8')] = NameLUTEntry(
                        cu_ofs = hdr_cu_ofs,
                        die_ofs = hdr_cu_ofs + entry.die_ofs)

        # return the entries parsed so far.
        return (entries, cu_headers)
