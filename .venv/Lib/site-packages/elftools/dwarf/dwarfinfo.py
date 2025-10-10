#-------------------------------------------------------------------------------
# elftools: dwarf/dwarfinfo.py
#
# DWARFInfo - Main class for accessing DWARF debug information
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os
from collections import namedtuple, OrderedDict
from bisect import bisect_right

from ..construct.lib.container import Container
from ..common.exceptions import DWARFError
from ..common.utils import (struct_parse, dwarf_assert,
                            parse_cstring_from_stream)
from .structs import DWARFStructs
from .compileunit import CompileUnit
from .typeunit import TypeUnit
from .abbrevtable import AbbrevTable
from .lineprogram import LineProgram
from .callframe import CallFrameInfo
from .locationlists import LocationLists, LocationListsPair
from .ranges import RangeLists, RangeListsPair
from .aranges import ARanges
from .namelut import NameLUT
from .dwarf_util import _get_base_offset


# Describes a debug section
#
# stream: a stream object containing the data of this section
# name: section name in the container file
# global_offset: the global offset of the section in its container file
# size: the size of the section's data, in bytes
# address: the virtual address for the section's data
#
# 'name' and 'global_offset' are for descriptional purposes only and
# aren't strictly required for the DWARF parsing to work. 'address' is required
# to properly decode the special '.eh_frame' format.
#
DebugSectionDescriptor = namedtuple('DebugSectionDescriptor',
    'stream name global_offset size address')


# Some configuration parameters for the DWARF reader. This exists to allow
# DWARFInfo to be independent from any specific file format/container.
#
# little_endian:
#   boolean flag specifying whether the data in the file is little endian
#
# machine_arch:
#   Machine architecture as a string. For example 'x86' or 'x64'
#
# default_address_size:
#   The default address size for the container file (sizeof pointer, in bytes)
#
DwarfConfig = namedtuple('DwarfConfig',
    'little_endian machine_arch default_address_size')


class DWARFInfo(object):
    """ Acts also as a "context" to other major objects, bridging between
        various parts of the debug information.
    """
    def __init__(self,
            config,
            debug_info_sec,
            debug_aranges_sec,
            debug_abbrev_sec,
            debug_frame_sec,
            eh_frame_sec,
            debug_str_sec,
            debug_loc_sec,
            debug_ranges_sec,
            debug_line_sec,
            debug_pubtypes_sec,
            debug_pubnames_sec,
            debug_addr_sec,
            debug_str_offsets_sec,
            debug_line_str_sec,
            debug_loclists_sec,
            debug_rnglists_sec,
            debug_sup_sec,
            gnu_debugaltlink_sec,
            debug_types_sec
            ):
        """ config:
                A DwarfConfig object

            debug_*_sec:
                DebugSectionDescriptor for a section. Pass None for sections
                that don't exist. These arguments are best given with
                keyword syntax.
        """
        self.config = config
        self.debug_info_sec = debug_info_sec
        self.debug_aranges_sec = debug_aranges_sec
        self.debug_abbrev_sec = debug_abbrev_sec
        self.debug_frame_sec = debug_frame_sec
        self.eh_frame_sec = eh_frame_sec
        self.debug_str_sec = debug_str_sec
        self.debug_loc_sec = debug_loc_sec
        self.debug_ranges_sec = debug_ranges_sec
        self.debug_line_sec = debug_line_sec
        self.debug_addr_sec = debug_addr_sec
        self.debug_str_offsets_sec = debug_str_offsets_sec
        self.debug_line_str_sec = debug_line_str_sec
        self.debug_pubtypes_sec = debug_pubtypes_sec
        self.debug_pubnames_sec = debug_pubnames_sec
        self.debug_loclists_sec = debug_loclists_sec
        self.debug_rnglists_sec = debug_rnglists_sec
        self.debug_sup_sec = debug_sup_sec
        self.gnu_debugaltlink_sec = gnu_debugaltlink_sec
        self.debug_types_sec = debug_types_sec

        # Sets the supplementary_dwarfinfo to None. Client code can set this
        # to something else, typically a DWARFInfo file read from an ELFFile
        # which path is stored in the debug_sup_sec or gnu_debugaltlink_sec.
        self.supplementary_dwarfinfo = None

        # This is the DWARFStructs the context uses, so it doesn't depend on
        # DWARF format and address_size (these are determined per CU) - set them
        # to default values.
        self.structs = DWARFStructs(
            little_endian=self.config.little_endian,
            dwarf_format=32,
            address_size=self.config.default_address_size)

        # Cache for abbrev tables: a dict keyed by offset
        self._abbrevtable_cache = {}
        # Cache for program lines tables: a dict keyed by offset
        self._linetable_cache = {}
 
        # Cache of compile units and map of their offsets for bisect lookup.
        # Access with .iter_CUs(), .get_CU_containing(), and/or .get_CU_at().
        self._cu_cache = []
        self._cu_offsets_map = []

        # DWARF v4 type units by sig8 - OrderedDict created when needed
        self._type_units_by_sig = None

    @property
    def has_debug_info(self):
        """ Return whether this contains debug information.

        It can be not the case when the ELF only contains .eh_frame, which is
        encoded DWARF but not actually for debugging.
        """
        return bool(self.debug_info_sec)

    def has_debug_types(self):
        """ Return whether this contains debug types information.
        """
        return bool(self.debug_types_sec)

    def get_DIE_from_lut_entry(self, lut_entry):
        """ Get the DIE from the pubnames or putbtypes lookup table entry.

            lut_entry:
                A NameLUTEntry object from a NameLUT instance (see
                .get_pubmames and .get_pubtypes methods).
        """
        cu = self.get_CU_at(lut_entry.cu_ofs)
        return self.get_DIE_from_refaddr(lut_entry.die_ofs, cu)

    def get_DIE_from_refaddr(self, refaddr, cu=None):
        """ Given a .debug_info section offset of a DIE, return the DIE.

            refaddr:
                The refaddr may come from a DW_FORM_ref_addr attribute.

            cu:
                The compile unit object, if known.  If None a search
                from the closest offset less than refaddr will be performed.
        """
        if cu is None:
            cu = self.get_CU_containing(refaddr)
        return cu.get_DIE_from_refaddr(refaddr)
    
    def get_DIE_by_sig8(self, sig8):
        """ Find and return a DIE referenced by its type signature.
            sig8:
                The 8 byte signature (as a 64-bit unsigned integer)
            Returns the DIE with the given type signature by searching
            for the Type Unit with the matching signature then finding
            the DIE at the offset given by the type_die field in the
            Type Unit header.
                Signatures are an 64-bit unsigned integers computed by the
                DWARF producer as specified in the DWARF standard. Each
                Type Unit contains one signature and the offset to the
                corresponding DW_AT_type DIE in its unit header.
                Describing a type can generate several DIEs. By moving
                a DIE and its related DIEs to a Type Unit and generating
                a hash of the DIEs and attributes in a flattened form
                multiple Compile Units in a linked object can reference
                the same DIE in the overall DWARF structure.
            In DWARF v4 type units are identified by their appearance in the
            .debug_types section.
        """
        self._parse_debug_types()
        tu = self._type_units_by_sig.get(sig8)
        if tu is None:
            raise KeyError("Signature %016x not found in .debug_types" % sig8)
        return tu._get_cached_DIE(tu.tu_offset + tu['type_offset'])    

    def get_CU_containing(self, refaddr):
        """ Find the CU that includes the given reference address in the
            .debug_info section.

            refaddr:
                Either a refaddr of a DIE (possibly from a DW_FORM_ref_addr
                attribute) or the section offset of a CU (possibly from an
                aranges table).

           This function will parse and cache CUs until the search criteria
           is met, starting from the closest known offset lessthan or equal
           to the given address.
        """
        dwarf_assert(
            self.has_debug_info,
            'CU lookup but no debug info section')
        dwarf_assert(
            0 <= refaddr < self.debug_info_sec.size,
            "refaddr %s beyond .debug_info size" % refaddr)

        # The CU containing the DIE we desire will be to the right of the
        # DIE insert point.  If we have a CU address, then it will be a
        # match but the right insert minus one will still be the item.
        # The first CU starts at offset 0, so start there if cache is empty.
        i = bisect_right(self._cu_offsets_map, refaddr)
        start = self._cu_offsets_map[i - 1] if i > 0 else 0

        # parse CUs until we find one containing the desired address
        for cu in self._parse_CUs_iter(start):
            if cu.cu_offset <= refaddr < cu.cu_offset + cu.size:
                return cu

        raise ValueError("CU for reference address %s not found" % refaddr)

    def get_CU_at(self, offset):
        """ Given a CU header offset, return the parsed CU.

            offset:
                The offset may be from an accelerated access table such as
                the public names, public types, address range table, or
                prior use.

            This function will directly parse the CU doing no validation of
            the offset beyond checking the size of the .debug_info section.
        """
        dwarf_assert(
            self.has_debug_info,
            'CU lookup but no debug info section')
        dwarf_assert(
            0 <= offset < self.debug_info_sec.size,
            "offset %s beyond .debug_info size" % offset)

        return self._cached_CU_at_offset(offset)

    def get_TU_by_sig8(self, sig8):
        """ Find and return a Type Unit referenced by its signature

            sig8:
                The 8 byte unique signature (as a 64-bit unsigned integer)

            Returns the TU with the given type signature by parsing the
            .debug_types section.

        """
        self._parse_debug_types()
        tu = self._type_units_by_sig.get(sig8)
        if tu is None:
            raise KeyError("Signature %016x not found in .debug_types" % sig8)
        return tu

    def iter_CUs(self):
        """ Yield all the compile units (CompileUnit objects) in the debug info
        """
        return self._parse_CUs_iter()

    def iter_TUs(self):
        """Yield all the type units (TypeUnit objects) in the debug_types
        """
        return self._parse_TUs_iter()

    def get_abbrev_table(self, offset):
        """ Get an AbbrevTable from the given offset in the debug_abbrev
            section.

            The only verification done on the offset is that it's within the
            bounds of the section (if not, an exception is raised).
            It is the caller's responsibility to make sure the offset actually
            points to a valid abbreviation table.

            AbbrevTable objects are cached internally (two calls for the same
            offset will return the same object).
        """
        dwarf_assert(
            offset < self.debug_abbrev_sec.size,
            "Offset '0x%x' to abbrev table out of section bounds" % offset)
        if offset not in self._abbrevtable_cache:
            self._abbrevtable_cache[offset] = AbbrevTable(
                structs=self.structs,
                stream=self.debug_abbrev_sec.stream,
                offset=offset)
        return self._abbrevtable_cache[offset]

    def get_string_from_table(self, offset):
        """ Obtain a string from the string table section, given an offset
            relative to the section.
        """
        return parse_cstring_from_stream(self.debug_str_sec.stream, offset)

    def get_string_from_linetable(self, offset):
        """ Obtain a string from the string table section, given an offset
            relative to the section.
        """
        return parse_cstring_from_stream(self.debug_line_str_sec.stream, offset)

    def line_program_for_CU(self, CU):
        """ Given a CU object, fetch the line program it points to from the
            .debug_line section.
            If the CU doesn't point to a line program, return None.

            Note about directory and file names. They are returned as two collections
            in the lineprogram object's header - include_directory and file_entry.

            In DWARFv5, they have introduced a different, extensible format for those
            collections. So in a lineprogram v5+, there are two more collections in
            the header - directories and file_names. Those might contain extra DWARFv5
            information that is not exposed in include_directory and file_entry.
        """
        # The line program is pointed to by the DW_AT_stmt_list attribute of
        # the top DIE of a CU.
        top_DIE = CU.get_top_DIE()
        if 'DW_AT_stmt_list' in top_DIE.attributes:
            return self._parse_line_program_at_offset(
                    top_DIE.attributes['DW_AT_stmt_list'].value, CU.structs)
        else:
            return None

    def has_CFI(self):
        """ Does this dwarf info have a dwarf_frame CFI section?
        """
        return self.debug_frame_sec is not None

    def CFI_entries(self):
        """ Get a list of dwarf_frame CFI entries from the .debug_frame section.
        """
        cfi = CallFrameInfo(
            stream=self.debug_frame_sec.stream,
            size=self.debug_frame_sec.size,
            address=self.debug_frame_sec.address,
            base_structs=self.structs)
        return cfi.get_entries()

    def has_EH_CFI(self):
        """ Does this dwarf info have a eh_frame CFI section?
        """
        return self.eh_frame_sec is not None

    def EH_CFI_entries(self):
        """ Get a list of eh_frame CFI entries from the .eh_frame section.
        """
        cfi = CallFrameInfo(
            stream=self.eh_frame_sec.stream,
            size=self.eh_frame_sec.size,
            address=self.eh_frame_sec.address,
            base_structs=self.structs,
            for_eh_frame=True)
        return cfi.get_entries()

    def get_pubtypes(self):
        """
        Returns a NameLUT object that contains information read from the
        .debug_pubtypes section in the ELF file.

        NameLUT is essentially a dictionary containing the CU/DIE offsets of
        each symbol. See the NameLUT doc string for more details.
        """

        if self.debug_pubtypes_sec:
            return NameLUT(self.debug_pubtypes_sec.stream,
                    self.debug_pubtypes_sec.size,
                    self.structs)
        else:
            return None

    def get_pubnames(self):
        """
        Returns a NameLUT object that contains information read from the
        .debug_pubnames section in the ELF file.

        NameLUT is essentially a dictionary containing the CU/DIE offsets of
        each symbol. See the NameLUT doc string for more details.
        """

        if self.debug_pubnames_sec:
            return NameLUT(self.debug_pubnames_sec.stream,
                    self.debug_pubnames_sec.size,
                    self.structs)
        else:
            return None

    def get_aranges(self):
        """ Get an ARanges object representing the .debug_aranges section of
            the DWARF data, or None if the section doesn't exist
        """
        if self.debug_aranges_sec:
            return ARanges(self.debug_aranges_sec.stream,
                self.debug_aranges_sec.size,
                self.structs)
        else:
            return None

    def location_lists(self):
        """ Get a LocationLists object representing the .debug_loc/debug_loclists section of
            the DWARF data, or None if this section doesn't exist.

            If both sections exist, it returns a LocationListsPair.
        """
        if self.debug_loclists_sec and self.debug_loc_sec is None:
            return LocationLists(self.debug_loclists_sec.stream, self.structs, 5, self)
        elif self.debug_loc_sec and self.debug_loclists_sec is None:
            return LocationLists(self.debug_loc_sec.stream, self.structs, 4, self)
        elif self.debug_loc_sec and self.debug_loclists_sec:
            return LocationListsPair(self.debug_loc_sec.stream, self.debug_loclists_sec.stream, self.structs, self)
        else:
            return None

    def range_lists(self):
        """ Get a RangeLists object representing the .debug_ranges/.debug_rnglists section of
            the DWARF data, or None if this section doesn't exist.

            If both sections exist, it returns a RangeListsPair.
        """
        if self.debug_rnglists_sec and self.debug_ranges_sec is None:
            return RangeLists(self.debug_rnglists_sec.stream, self.structs, 5, self)
        elif self.debug_ranges_sec and self.debug_rnglists_sec is None:
            return RangeLists(self.debug_ranges_sec.stream, self.structs, 4, self)
        elif self.debug_ranges_sec and self.debug_rnglists_sec:
            return RangeListsPair(self.debug_ranges_sec.stream, self.debug_rnglists_sec.stream, self.structs, self)
        else:
            return None

    def get_addr(self, cu, addr_index):
        """Provided a CU and an index, retrieves an address from the debug_addr section
        """
        if not self.debug_addr_sec:
            raise DWARFError('The file does not contain a debug_addr section for indirect address access')
        # Selectors are not supported, but no assert on that. TODO?
        cu_addr_base = _get_base_offset(cu, 'DW_AT_addr_base')
        return struct_parse(cu.structs.the_Dwarf_target_addr, self.debug_addr_sec.stream, cu_addr_base + addr_index*cu.header.address_size)            

    #------ PRIVATE ------#

    def _parse_CUs_iter(self, offset=0):
        """ Iterate CU objects in order of appearance in the debug_info section.

            offset:
                The offset of the first CU to yield.  Additional iterations
                will return the sequential unit objects.

            See .iter_CUs(), .get_CU_containing(), and .get_CU_at().
        """
        if self.debug_info_sec is None:
            return

        while offset < self.debug_info_sec.size:
            cu = self._cached_CU_at_offset(offset)
            # Compute the offset of the next CU in the section. The unit_length
            # field of the CU header contains its size not including the length
            # field itself.
            offset = (offset +
                      cu['unit_length'] +
                      cu.structs.initial_length_field_size())
            yield cu

    def _parse_TUs_iter(self, offset=0):
        """ Iterate Type Unit objects in order of appearance in the debug_types section.

            offset:
                The offset of the first TU to yield.  Additional iterations
                will return the sequential unit objects.

                See .iter_TUs().
        """
        if self.debug_types_sec is None:
            return

        while offset < self.debug_types_sec.size:
            tu = self._parse_TU_at_offset(offset)
            # Compute the offset of the next TU in the section. The unit_length
            # field of the TU header contains its size not including the length
            # field itself.
            offset = (offset +
                      tu['unit_length'] +
                      tu.structs.initial_length_field_size())

            yield tu

    def _parse_debug_types(self):
        """ Check if the .debug_types section is previously parsed. If not,
            parse all TUs and store them in an OrderedDict using their unique
            64-bit signature as the key.

            See .get_TU_by_sig8().
        """
        if self._type_units_by_sig is not None:
            return
        self._type_units_by_sig = OrderedDict()

        if self.debug_types_sec is None:
            return

        # Parse all the Type Units in the types section for access by sig8
        offset = 0
        while offset < self.debug_types_sec.size:
            tu = self._parse_TU_at_offset(offset)
            # Compute the offset of the next TU in the section. The unit_length
            # field of the TU header contains its size not including the length
            # field itself.
            offset = (offset +
                      tu['unit_length'] +
                      tu.structs.initial_length_field_size())
            self._type_units_by_sig[tu['signature']] = tu

    def _cached_CU_at_offset(self, offset):
        """ Return the CU with unit header at the given offset into the
            debug_info section from the cache.  If not present, the unit is
            header is parsed and the object is installed in the cache.

            offset:
                The offset of the unit header in the .debug_info section
                to of the unit to fetch from the cache.

            See get_CU_at().
        """
        # Find the insert point for the requested offset.  With bisect_right,
        # if this entry is present in the cache it will be the prior entry.
        i = bisect_right(self._cu_offsets_map, offset)
        if i >= 1 and offset == self._cu_offsets_map[i - 1]:
            return self._cu_cache[i - 1]

        # Parse the CU and insert the offset and object into the cache.
        # The ._cu_offsets_map[] contains just the numeric offsets for the
        # bisect_right search while the parallel indexed ._cu_cache[] holds
        # the object references.
        cu = self._parse_CU_at_offset(offset)
        self._cu_offsets_map.insert(i, offset)
        self._cu_cache.insert(i, cu)
        return cu

    def _parse_CU_at_offset(self, offset):
        """ Parse and return a CU at the given offset in the debug_info stream.
        """
        # Section 7.4 (32-bit and 64-bit DWARF Formats) of the DWARF spec v3
        # states that the first 32-bit word of the CU header determines
        # whether the CU is represented with 32-bit or 64-bit DWARF format.
        #
        # So we peek at the first word in the CU header to determine its
        # dwarf format. Based on it, we then create a new DWARFStructs
        # instance suitable for this CU and use it to parse the rest.
        #
        initial_length = struct_parse(
            self.structs.the_Dwarf_uint32, self.debug_info_sec.stream, offset)
        dwarf_format = 64 if initial_length == 0xFFFFFFFF else 32


        # Temporary structs for parsing the header
        # The structs for the rest of the CU depend on the header data.
        #
        cu_structs = DWARFStructs(
            little_endian=self.config.little_endian,
            dwarf_format=dwarf_format,
            address_size=4,
            dwarf_version=2)

        cu_header = struct_parse(
            cu_structs.Dwarf_CU_header, self.debug_info_sec.stream, offset)

        # structs for the rest of the CU, taking into account bitness and DWARF version
        cu_structs = DWARFStructs(
            little_endian=self.config.little_endian,
            dwarf_format=dwarf_format,
            address_size=cu_header['address_size'],
            dwarf_version=cu_header['version'])

        cu_die_offset = self.debug_info_sec.stream.tell()
        dwarf_assert(
            self._is_supported_version(cu_header['version']),
            "Expected supported DWARF version. Got '%s'" % cu_header['version'])
        return CompileUnit(
                header=cu_header,
                dwarfinfo=self,
                structs=cu_structs,
                cu_offset=offset,
                cu_die_offset=cu_die_offset)

    def _parse_TU_at_offset(self, offset):
        """ Parse and return a Type Unit (TU) at the given offset in the debug_types stream.
        """
        # Section 7.4 (32-bit and 64-bit DWARF Formats) of the DWARF spec v4
        # states that the first 32-bit word of the TU header determines
        # whether the TU is represented with 32-bit or 64-bit DWARF format.
        #
        # So we peek at the first word in the TU header to determine its
        # dwarf format. Based on it, we then create a new DWARFStructs
        # instance suitable for this TU and use it to parse the rest.
        #
        initial_length = struct_parse(
            self.structs.the_Dwarf_uint32, self.debug_types_sec.stream, offset)
        dwarf_format = 64 if initial_length == 0xFFFFFFFF else 32

        # Temporary structs for parsing the header
        # The structs for the rest of the TU depend on the header data.
        #
        tu_structs = DWARFStructs(
            little_endian=self.config.little_endian,
            dwarf_format=dwarf_format,
            address_size=4,
            dwarf_version=2)

        tu_header = struct_parse(
            tu_structs.Dwarf_TU_header, self.debug_types_sec.stream, offset)

        # structs for the rest of the TU, taking into account bit-width and DWARF version
        tu_structs = DWARFStructs(
            little_endian=self.config.little_endian,
            dwarf_format=dwarf_format,
            address_size=tu_header['address_size'],
            dwarf_version=tu_header['version'])

        tu_die_offset = self.debug_types_sec.stream.tell()
        dwarf_assert(
            self._is_supported_version(tu_header['version']),
            "Expected supported DWARF version. Got '%s'" % tu_header['version'])
        return TypeUnit(
            header=tu_header,
            dwarfinfo=self,
            structs=tu_structs,
            tu_offset=offset,
            tu_die_offset=tu_die_offset)

    def _is_supported_version(self, version):
        """ DWARF version supported by this parser
        """
        return 2 <= version <= 5

    def _parse_line_program_at_offset(self, offset, structs):
        """ Given an offset to the .debug_line section, parse the line program
            starting at this offset in the section and return it.
            structs is the DWARFStructs object used to do this parsing.
        """

        if offset in self._linetable_cache:
            return self._linetable_cache[offset]

        lineprog_header = struct_parse(
            structs.Dwarf_lineprog_header,
            self.debug_line_sec.stream,
            offset)

        # DWARF5: resolve names
        def resolve_strings(self, lineprog_header, format_field, data_field):
            if lineprog_header.get(format_field, False):
                data = lineprog_header[data_field]
                for field in lineprog_header[format_field]:
                    def replace_value(data, content_type, replacer):
                        for entry in data:
                            entry[content_type] = replacer(entry[content_type])

                    if field.form == 'DW_FORM_line_strp':
                        replace_value(data, field.content_type, self.get_string_from_linetable)
                    elif field.form == 'DW_FORM_strp':
                        replace_value(data, field.content_type, self.get_string_from_table)
                    elif field.form in ('DW_FORM_strp_sup', 'DW_FORM_GNU_strp_alt'):
                        if self.supplementary_dwarfinfo:
                            replace_value(data, field.content_type, self.supplementary_dwarfinfo.get_string_fromtable)
                        else:
                            replace_value(data, field.content_type, lambda x: str(x))
                    elif field.form in ('DW_FORM_strp_sup', 'DW_FORM_strx', 'DW_FORM_strx1', 'DW_FORM_strx2', 'DW_FORM_strx3', 'DW_FORM_strx4'):
                        raise NotImplementedError()

        resolve_strings(self, lineprog_header, 'directory_entry_format', 'directories')
        resolve_strings(self, lineprog_header, 'file_name_entry_format', 'file_names')

        # DWARF5: provide compatible file/directory name arrays for legacy lineprogram consumers
        if lineprog_header.get('directories', False):
            lineprog_header.include_directory = tuple(d.DW_LNCT_path for d in lineprog_header.directories)
        if lineprog_header.get('file_names', False):
            lineprog_header.file_entry = tuple(
                Container(**{
                    'name':e.get('DW_LNCT_path'),
                    'dir_index': e.get('DW_LNCT_directory_index'),
                    'mtime': e.get('DW_LNCT_timestamp'),
                    'length': e.get('DW_LNCT_size')})
                for e in lineprog_header.file_names)

        # Calculate the offset to the next line program (see DWARF 6.2.4)
        end_offset = (  offset + lineprog_header['unit_length'] +
                        structs.initial_length_field_size())

        lineprogram = LineProgram(
            header=lineprog_header,
            stream=self.debug_line_sec.stream,
            structs=structs,
            program_start_offset=self.debug_line_sec.stream.tell(),
            program_end_offset=end_offset)

        self._linetable_cache[offset] = lineprogram
        return lineprogram

    def parse_debugsupinfo(self):
        """
        Extract a filename from .debug_sup, .gnu_debualtlink sections.
        """
        if self.debug_sup_sec is not None:
            self.debug_sup_sec.stream.seek(0)
            suplink = self.structs.Dwarf_debugsup.parse_stream(self.debug_sup_sec.stream)
            if suplink.is_supplementary == 0:
                return suplink.sup_filename
        if self.gnu_debugaltlink_sec is not None:
            self.gnu_debugaltlink_sec.stream.seek(0)
            suplink = self.structs.Dwarf_debugaltlink.parse_stream(self.gnu_debugaltlink_sec.stream)
            return suplink.sup_filename
        # The section .gnu_debuglink with similarly looking contents
        # has a different meaning - it doesn't point at supplementary DWARF,
        # which is meant to be referenced from primary DWARF,
        # it points at DWARF proper.
        return None

