#-------------------------------------------------------------------------------
# elftools: dwarf/dwarf_utils.py
#
# Minor, shared DWARF helpers
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------

import os, binascii
from ..construct.macros import UBInt32, UBInt64, ULInt32, ULInt64, Array
from ..common.exceptions import DWARFError
from ..common.utils import preserve_stream_pos, struct_parse

def _get_base_offset(cu, base_attribute_name):
    """Retrieves a required, base offset-type atribute
    from the top DIE in the CU. Applies to several indirectly
    encoded objects - range lists, location lists, strings, addresses.
    """
    cu_top_die = cu.get_top_DIE()
    if not base_attribute_name in cu_top_die.attributes:
        raise DWARFError("The CU at offset 0x%x needs %s" % (cu.cu_offset, base_attribute_name))
    return cu_top_die.attributes[base_attribute_name].value

def _resolve_via_offset_table(stream, cu, index, base_attribute_name):
    """Given an index in the offset table and directions where to find it,
    retrieves an offset. Works for loclists, rnglists.

    The DWARF offset bitness of the CU block in the section matches that
    of the CU record in dwarf_info. See DWARFv5 standard, section 7.4.

    This is used for translating DW_FORM_loclistx, DW_FORM_rnglistx
    via the offset table in the respective section.
    """
    base_offset = _get_base_offset(cu, base_attribute_name)
    # That's offset (within the rnglists/loclists/str_offsets section) of
    # the offset table for this CU's block in that section, which in turn is indexed by the index.

    offset_size = 4 if cu.structs.dwarf_format == 32 else 8
    with preserve_stream_pos(stream):
        return base_offset + struct_parse(cu.structs.the_Dwarf_offset, stream, base_offset + index*offset_size)

def _iter_CUs_in_section(stream, structs, parser):
    """Iterates through the list of CU sections in loclists or rangelists. Almost identical structures there.

    get_parser is a lambda that takes structs, returns the parser
    """
    stream.seek(0, os.SEEK_END)
    endpos = stream.tell()
    stream.seek(0, os.SEEK_SET)

    offset = 0
    while offset < endpos:
        header = struct_parse(parser, stream, offset)
        if header.offset_count > 0:
            offset_parser = structs.Dwarf_uint64 if header.is64 else structs.Dwarf_uint32
            header['offsets'] = struct_parse(Array(header.offset_count, offset_parser('')), stream)
        else:
            header['offsets'] = False
        yield header
        offset = header.offset_after_length + header.unit_length   

def _file_crc32(file):
    """ Provided a readable binary stream, reads the stream to the end
        and computes the CRC32 checksum of its contents,
        with the initial value of 0.
    """
    d = file.read(4096)
    checksum = 0
    while len(d):
        checksum = binascii.crc32(d, checksum)
        d = file.read(4096)
    return checksum
