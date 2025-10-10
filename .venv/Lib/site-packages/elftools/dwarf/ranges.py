#-------------------------------------------------------------------------------
# elftools: dwarf/ranges.py
#
# DWARF ranges section decoding (.debug_ranges)
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os
from collections import namedtuple

from ..common.utils import struct_parse
from ..common.exceptions import DWARFError
from .dwarf_util import _iter_CUs_in_section


RangeEntry = namedtuple('RangeEntry', 'entry_offset entry_length begin_offset end_offset is_absolute')
BaseAddressEntry = namedtuple('BaseAddressEntry', 'entry_offset base_address')
# If we ever see a list with a base entry at the end, there will be an error that entry_length is not a field.

def _translate_startx_length(e, cu):
    start_offset = cu.dwarfinfo.get_addr(cu, e.start_index)
    return RangeEntry(e.entry_offset, e.entry_length, start_offset, start_offset + e.length, True)

# Maps parsed entry types to RangeEntry/BaseAddressEntry objects
entry_translate = {
    'DW_RLE_base_address' : lambda e, cu: BaseAddressEntry(e.entry_offset, e.address),
    'DW_RLE_offset_pair'  : lambda e, cu: RangeEntry(e.entry_offset, e.entry_length, e.start_offset, e.end_offset, False),
    'DW_RLE_start_end'    : lambda e, cu: RangeEntry(e.entry_offset, e.entry_length, e.start_address, e.end_address, True),
    'DW_RLE_start_length' : lambda e, cu: RangeEntry(e.entry_offset, e.entry_length, e.start_address, e.start_address + e.length, True),
    'DW_RLE_base_addressx': lambda e, cu: BaseAddressEntry(e.entry_offset, cu.dwarfinfo.get_addr(cu, e.index)),
    'DW_RLE_startx_endx'  : lambda e, cu: RangeEntry(e.entry_offset, e.entry_length, cu.dwarfinfo.get_addr(cu, e.start_index), cu.dwarfinfo.get_addr(cu, e.end_index), True),
    'DW_RLE_startx_length': _translate_startx_length
}

class RangeListsPair(object):
    """For those binaries that contain both a debug_ranges and a debug_rnglists section,
    it holds a RangeLists object for both and forwards API calls to the right one based
    on the CU version.
    """
    def __init__(self, streamv4, streamv5, structs, dwarfinfo=None):
        self._ranges = RangeLists(streamv4, structs, 4, dwarfinfo)
        self._rnglists = RangeLists(streamv5, structs, 5, dwarfinfo)

    def get_range_list_at_offset(self, offset, cu=None):
        """Forwards the call to either v4 section or v5 one,
        depending on DWARF version in the CU.
        """
        if cu is None:
            raise DWARFError("For this binary, \"cu\" needs to be provided")
        section = self._rnglists if cu.header.version >= 5 else self._ranges
        return section.get_range_list_at_offset(offset, cu)

    def get_range_list_at_offset_ex(self, offset):
        """Gets an untranslated v5 rangelist from the v5 section.
        """
        return self._rnglists.get_range_list_at_offset_ex(offset)

    def iter_range_lists(self):
        """Tricky proposition, since the structure of ranges and rnglists
        is not identical. A realistic readelf implementation needs to be aware of both.
        """
        raise DWARFError("Iterating through two sections is not supported")

    def iter_CUs(self):
        """See RangeLists.iter_CUs()
        
        CU structure is only present in DWARFv5 rnglists sections. A well written
        section dumper should check if one is present.
        """
        return self._rnglists.iter_CUs()

    def iter_CU_range_lists_ex(self, cu):
        """See RangeLists.iter_CU_range_lists_ex()

        CU structure is only present in DWARFv5 rnglists sections. A well written
        section dumper should check if one is present.
        """
        return self._rnglists.iter_CU_range_lists_ex(cu)
    
    def translate_v5_entry(self, entry, cu):
        """Forwards a V5 entry translation request to the V5 section
        """
        return self._rnglists.translate_v5_entry(entry, cu)

class RangeLists(object):
    """ A single range list is a Python list consisting of RangeEntry or
        BaseAddressEntry objects.

        Since v0.29, two new parameters - version and dwarfinfo

        version is used to distinguish DWARFv5 rnglists section from
        the DWARF<=4 ranges section. Only the 4/5 distinction matters.

        The dwarfinfo is needed for enumeration, because enumeration
        requires scanning the DIEs, because ranges may overlap, even on DWARF<=4
    """
    def __init__(self, stream, structs, version, dwarfinfo):
        self.stream = stream
        self.structs = structs
        self._max_addr = 2 ** (self.structs.address_size * 8) - 1
        self.version = version
        self._dwarfinfo = dwarfinfo

    def get_range_list_at_offset(self, offset, cu=None):
        """ Get a range list at the given offset in the section.

            The cu argument is necessary if the ranges section is a
            DWARFv5 debug_rnglists one, and the target rangelist
            contains indirect encodings
        """
        self.stream.seek(offset, os.SEEK_SET)
        return self._parse_range_list_from_stream(cu)

    def get_range_list_at_offset_ex(self, offset):
        """Get a DWARF v5 range list, addresses and offsets unresolved,
        at the given offset in the section
        """
        return struct_parse(self.structs.Dwarf_rnglists_entries, self.stream, offset)

    def iter_range_lists(self):
        """ Yields all range lists found in the section according to readelf rules.
        Scans the DIEs for rangelist offsets, then pulls those.
        Returned rangelists are always translated into lists of BaseAddressEntry/RangeEntry objects.
        """
        # Rangelists can overlap. That is, one DIE points at the rangelist beginning, and another
        # points at the middle of the same. Therefore, enumerating them is not a well defined
        # operation - do you count those as two different (but overlapping) ones, or as a single one?
        # For debugging utility, you want two. That's what readelf does. For faithfully
        # representing the section contents, you want one.
        # That was the behaviour of pyelftools 0.28 and below - calling
        # parse until the stream end. Leaving aside the question of correctless,
        # that's uncompatible with readelf.

        ver5 = self.version >= 5
        # This maps list offset to CU
        cu_map = {die.attributes['DW_AT_ranges'].value : cu
            for cu in self._dwarfinfo.iter_CUs()
            for die in cu.iter_DIEs()
            if 'DW_AT_ranges' in die.attributes and (cu['version'] >= 5) == ver5}
        all_offsets = list(cu_map.keys())
        all_offsets.sort()

        for offset in all_offsets:
            yield self.get_range_list_at_offset(offset, cu_map[offset])

    def iter_CUs(self):
        """For DWARF5 returns an array of objects, where each one has an array of offsets
        """
        if self.version < 5:
            raise DWARFError("CU iteration in rnglists is not supported with DWARF<5")

        structs = next(self._dwarfinfo.iter_CUs()).structs # Just pick one
        return _iter_CUs_in_section(self.stream, structs, structs.Dwarf_rnglists_CU_header)

    def iter_CU_range_lists_ex(self, cu):
        """For DWARF5, returns untranslated rangelists in the CU, where CU comes from iter_CUs above
        """
        stream = self.stream
        stream.seek(cu.offset_table_offset + (64 if cu.is64 else 32) * cu.offset_count)
        while stream.tell() < cu.offset_after_length + cu.unit_length:
            yield struct_parse(self.structs.Dwarf_rnglists_entries, stream)

    def translate_v5_entry(self, entry, cu):
        """Translates entries in a DWARFv5 rangelist from raw parsed format to 
        a list of BaseAddressEntry/RangeEntry, using the CU
        """
        return entry_translate[entry.entry_type](entry, cu)

    #------ PRIVATE ------#

    def _parse_range_list_from_stream(self, cu):
        if self.version >= 5:
            return list(entry_translate[entry.entry_type](entry, cu)
                for entry
                in struct_parse(self.structs.Dwarf_rnglists_entries, self.stream))
        else:
            lst = []
            while True:
                entry_offset = self.stream.tell()
                begin_offset = struct_parse(
                    self.structs.the_Dwarf_target_addr, self.stream)
                end_offset = struct_parse(
                    self.structs.the_Dwarf_target_addr, self.stream)
                if begin_offset == 0 and end_offset == 0:
                    # End of list - we're done.
                    break
                elif begin_offset == self._max_addr:
                    # Base address selection entry
                    lst.append(BaseAddressEntry(entry_offset=entry_offset, base_address=end_offset))
                else:
                    # Range entry
                    lst.append(RangeEntry(
                        entry_offset=entry_offset,
                        entry_length=self.stream.tell() - entry_offset,
                        begin_offset=begin_offset,
                        end_offset=end_offset,
                        is_absolute=False))
            return lst
