#-------------------------------------------------------------------------------
# elftools: dwarf/aranges.py
#
# DWARF aranges section decoding (.debug_aranges)
#
# Dorothy Chen (dorothchen@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os
from collections import namedtuple
from ..common.utils import struct_parse
from bisect import bisect_right
import math

# An entry in the aranges table;
# begin_addr: The beginning address in the CU
# length: The length of the address range in this entry
# info_offset: The CU's offset into .debug_info
# see 6.1.2 in DWARF4 docs for explanation of the remaining fields
ARangeEntry = namedtuple('ARangeEntry',
    'begin_addr length info_offset unit_length version address_size segment_size')

class ARanges(object):
    """ ARanges table in DWARF

        stream, size:
            A stream holding the .debug_aranges section, and its size

        structs:
            A DWARFStructs instance for parsing the data
    """
    def __init__(self, stream, size, structs):
        self.stream = stream
        self.size = size
        self.structs = structs

        # Get entries of aranges table in the form of ARangeEntry tuples
        self.entries = self._get_entries()

        # Sort entries by the beginning address
        self.entries.sort(key=lambda entry: entry.begin_addr)

        # Create list of keys (first addresses) for better searching
        self.keys = [entry.begin_addr for entry in self.entries]


    def cu_offset_at_addr(self, addr):
        """ Given an address, get the offset of the CU it belongs to, where
            'offset' refers to the offset in the .debug_info section.
        """
        tup = self.entries[bisect_right(self.keys, addr) - 1]
        if tup.begin_addr <= addr < tup.begin_addr + tup.length:
            return tup.info_offset
        else:
            return None


    #------ PRIVATE ------#
    def _get_entries(self, need_empty=False):
        """ Populate self.entries with ARangeEntry tuples for each range of addresses

            Terminating null entries of CU blocks are not returned, unless
            need_empty is set to True and the CU block contains nothing but
            a null entry. The null entry will have both address and length
            set to 0. 
        """
        self.stream.seek(0)
        entries = []
        offset = 0

        # one loop == one "set" == one CU
        while offset < self.size :
            aranges_header = struct_parse(self.structs.Dwarf_aranges_header,
                self.stream, offset)
            addr_size = self._get_addr_size_struct(aranges_header["address_size"])

            # No segmentation
            if aranges_header["segment_size"] == 0:
                # pad to nearest multiple of tuple size
                tuple_size = aranges_header["address_size"] * 2
                fp = self.stream.tell()
                seek_to = int(math.ceil(fp/float(tuple_size)) * tuple_size)
                self.stream.seek(seek_to)

                # We now have a binary with empty arange sections - nothing but a NULL entry.
                # To keep compatibility with readelf, we need to return those.
                # A two level list would be a prettier solution, but this will be compatible.
                got_entries = False

                # entries in this set/CU
                addr = struct_parse(addr_size('addr'), self.stream)
                length = struct_parse(addr_size('length'), self.stream)
                while addr != 0 or length != 0 or (not got_entries and need_empty):
                    # 'begin_addr length info_offset version address_size segment_size'
                    entries.append(
                        ARangeEntry(begin_addr=addr,
                            length=length,
                            info_offset=aranges_header["debug_info_offset"],
                            unit_length=aranges_header["unit_length"],
                            version=aranges_header["version"],
                            address_size=aranges_header["address_size"],
                            segment_size=aranges_header["segment_size"]))
                    got_entries = True
                    if addr != 0 or length != 0:
                        addr = struct_parse(addr_size('addr'), self.stream)
                        length = struct_parse(addr_size('length'), self.stream)
                    
            # Segmentation exists in executable
            elif aranges_header["segment_size"] != 0:
                raise NotImplementedError("Segmentation not implemented")

            offset = (offset
                + aranges_header.unit_length
                + self.structs.initial_length_field_size())

        return entries

    def _get_addr_size_struct(self, addr_header_value):
        """ Given this set's header value (int) for the address size,
            get the Construct representation of that size
        """
        if addr_header_value == 4:
            return self.structs.Dwarf_uint32
        else:
            assert addr_header_value == 8
            return self.structs.Dwarf_uint64
