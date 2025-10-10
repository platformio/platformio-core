#-------------------------------------------------------------------------------
# elftools: dwarf/structs.py
#
# Encapsulation of Construct structs for parsing DWARF, adjusted for correct
# endianness and word-size.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from logging.config import valid_ident
from ..construct import (
    UBInt8, UBInt16, UBInt32, UBInt64, ULInt8, ULInt16, ULInt32, ULInt64,
    SBInt8, SBInt16, SBInt32, SBInt64, SLInt8, SLInt16, SLInt32, SLInt64,
    Adapter, Struct, ConstructError, If, Enum, Array, PrefixedArray,
    CString, Embed, StaticField, IfThenElse, Construct, Rename, Sequence,
    String, Switch, Value
    )
from ..common.construct_utils import (RepeatUntilExcluding, ULEB128, SLEB128,
    StreamOffset, ULInt24, UBInt24)
from .enums import *


class DWARFStructs(object):
    """ Exposes Construct structs suitable for parsing information from DWARF
        sections. Each compile unit in DWARF info can have its own structs
        object. Keep in mind that these structs have to be given a name (by
        calling them with a name) before being used for parsing (like other
        Construct structs). Those that should be used without a name are marked
        by (+).

        Accessible attributes (mostly as described in chapter 7 of the DWARF
        spec v3):

            Dwarf_[u]int{8,16,32,64):
                Data chunks of the common sizes

            Dwarf_offset:
                32-bit or 64-bit word, depending on dwarf_format

            Dwarf_length:
                32-bit or 64-bit word, depending on dwarf_format

            Dwarf_target_addr:
                32-bit or 64-bit word, depending on address size

            Dwarf_initial_length:
                "Initial length field" encoding
                section 7.4

            Dwarf_{u,s}leb128:
                ULEB128 and SLEB128 variable-length encoding

            Dwarf_CU_header (+):
                Compilation unit header

            Dwarf_TU_header (+):
                Type unit header

            Dwarf_abbrev_declaration (+):
                Abbreviation table declaration - doesn't include the initial
                code, only the contents.

            Dwarf_dw_form (+):
                A dictionary mapping 'DW_FORM_*' keys into construct Structs
                that parse such forms. These Structs have already been given
                dummy names.

            Dwarf_lineprog_header (+):
                Line program header

            Dwarf_lineprog_file_entry (+):
                A single file entry in a line program header or instruction

            Dwarf_CIE_header (+):
                A call-frame CIE

            Dwarf_FDE_header (+):
                A call-frame FDE

        See also the documentation of public methods.
    """

    # Cache for structs instances based on creation parameters. Structs
    # initialization is expensive and we don't won't to repeat it
    # unnecessarily.
    _structs_cache = {}

    def __new__(cls, little_endian, dwarf_format, address_size, dwarf_version=2):
        """ dwarf_version:
                Numeric DWARF version

            little_endian:
                True if the file is little endian, False if big

            dwarf_format:
                DWARF Format: 32 or 64-bit (see spec section 7.4)

            address_size:
                Target machine address size, in bytes (4 or 8). (See spec
                section 7.5.1)
        """
        key = (little_endian, dwarf_format, address_size, dwarf_version)

        if key in cls._structs_cache:
            return cls._structs_cache[key]

        self = super().__new__(cls)
        assert dwarf_format == 32 or dwarf_format == 64
        assert address_size == 8 or address_size == 4, str(address_size)
        self.little_endian = little_endian
        self.dwarf_format = dwarf_format
        self.address_size = address_size
        self.dwarf_version = dwarf_version
        self._create_structs()
        cls._structs_cache[key] = self
        return self

    def initial_length_field_size(self):
        """ Size of an initial length field.
        """
        return 4 if self.dwarf_format == 32 else 12

    def _create_structs(self):
        if self.little_endian:
            self.Dwarf_uint8 = ULInt8
            self.Dwarf_uint16 = ULInt16
            self.Dwarf_uint24 = ULInt24
            self.Dwarf_uint32 = ULInt32
            self.Dwarf_uint64 = ULInt64
            self.Dwarf_offset = ULInt32 if self.dwarf_format == 32 else ULInt64
            self.Dwarf_length = ULInt32 if self.dwarf_format == 32 else ULInt64
            self.Dwarf_target_addr = (
                ULInt32 if self.address_size == 4 else ULInt64)
            self.Dwarf_int8 = SLInt8
            self.Dwarf_int16 = SLInt16
            self.Dwarf_int32 = SLInt32
            self.Dwarf_int64 = SLInt64
        else:
            self.Dwarf_uint8 = UBInt8
            self.Dwarf_uint16 = UBInt16
            self.Dwarf_uint24 = UBInt24
            self.Dwarf_uint32 = UBInt32
            self.Dwarf_uint64 = UBInt64
            self.Dwarf_offset = UBInt32 if self.dwarf_format == 32 else UBInt64
            self.Dwarf_length = UBInt32 if self.dwarf_format == 32 else UBInt64
            self.Dwarf_target_addr = (
                UBInt32 if self.address_size == 4 else UBInt64)
            self.Dwarf_int8 = SBInt8
            self.Dwarf_int16 = SBInt16
            self.Dwarf_int32 = SBInt32
            self.Dwarf_int64 = SBInt64

        # Only instantiate those parsers that are used standalone,
        # as opposed to dispatch tables (e. g. forms, opcodes).
        # In dispatch tables, they are instantiated already.
        # LEB128 parsers are instantiated too, elsewhere.
        self.the_Dwarf_offset = self.Dwarf_offset('')
        self.the_Dwarf_target_addr = self.Dwarf_target_addr('')
        self.the_Dwarf_uint32 = self.Dwarf_uint32('')
        self.the_Dwarf_uint16 = self.Dwarf_uint16('')
        self.the_Dwarf_uint8 = self.Dwarf_uint8('')

        self._create_initial_length()
        self._create_leb128()
        self._create_cu_header()
        self._create_tu_header()
        self._create_abbrev_declaration()
        self._create_dw_form()
        self._create_lineprog_header()
        self._create_callframe_entry_headers()
        self._create_aranges_header()
        self._create_nameLUT_header()
        self._create_string_offsets_table_header()
        self._create_address_table_header()
        self._create_loclists_parsers()
        self._create_rnglists_parsers()

        self._create_debugsup()
        self._create_gnu_debugaltlink()

    def _create_initial_length(self):
        def _InitialLength(name):
            # Adapts a Struct that parses forward a full initial length field.
            # Only if the first word is the continuation value, the second
            # word is parsed from the stream.
            return _InitialLengthAdapter(
                Struct(name,
                    self.Dwarf_uint32('first'),
                    If(lambda ctx: ctx.first == 0xFFFFFFFF,
                        self.Dwarf_uint64('second'),
                        elsevalue=None)))
        self.Dwarf_initial_length = _InitialLength

    def _create_leb128(self):
        self.Dwarf_uleb128 = ULEB128
        self.Dwarf_sleb128 = SLEB128
        self.the_Dwarf_uleb128 = self.Dwarf_uleb128('')
        self.the_Dwarf_sleb128 = self.Dwarf_sleb128('')

    def _create_cu_header(self):
        dwarfv4_CU_header = Struct('',
            self.Dwarf_offset('debug_abbrev_offset'),
            self.Dwarf_uint8('address_size')
        )
        # DWARFv5 reverses the order of address_size and debug_abbrev_offset.
        # DWARFv5 7.5.1.1
        dwarfv5_CP_CU_header = Struct('',                  
            self.Dwarf_uint8('address_size'),
            self.Dwarf_offset('debug_abbrev_offset')
        )
        # DWARFv5 7.5.1.2
        dwarfv5_SS_CU_header = Struct('',
            self.Dwarf_uint8('address_size'),
            self.Dwarf_offset('debug_abbrev_offset'),
            self.Dwarf_uint64('dwo_id')
        )
        # DWARFv5 7.5.1.3
        dwarfv5_TS_CU_header = Struct('',
            self.Dwarf_uint8('address_size'),
            self.Dwarf_offset('debug_abbrev_offset'),
            self.Dwarf_uint64('type_signature'),
            self.Dwarf_offset('type_offset')
        )
        dwarfv5_CU_header = Struct('',
            Enum(self.Dwarf_uint8('unit_type'), **ENUM_DW_UT),
            Embed(Switch('', lambda ctx: ctx.unit_type,
            {
                'DW_UT_compile'       : dwarfv5_CP_CU_header,
                'DW_UT_partial'       : dwarfv5_CP_CU_header,
                'DW_UT_skeleton'      : dwarfv5_SS_CU_header,
                'DW_UT_split_compile' : dwarfv5_SS_CU_header,
                'DW_UT_type'          : dwarfv5_TS_CU_header,
                'DW_UT_split_type'    : dwarfv5_TS_CU_header,
            })))
        self.Dwarf_CU_header = Struct('Dwarf_CU_header',
            self.Dwarf_initial_length('unit_length'),
            self.Dwarf_uint16('version'),
            IfThenElse('', lambda ctx: ctx['version'] >= 5,
                Embed(dwarfv5_CU_header),
                Embed(dwarfv4_CU_header),
            ))

    def _create_tu_header(self):
        self.Dwarf_TU_header = Struct('Dwarf_TU_header',
                                      self.Dwarf_initial_length('unit_length'),
                                      self.Dwarf_uint16('version'),
                                      self.Dwarf_offset('debug_abbrev_offset'),
                                      self.Dwarf_uint8('address_size'),
                                      self.Dwarf_uint64('signature'),
                                      self.Dwarf_offset('type_offset'))

    def _create_abbrev_declaration(self):
        self.Dwarf_abbrev_declaration = Struct('Dwarf_abbrev_entry',
            Enum(self.Dwarf_uleb128('tag'), **ENUM_DW_TAG),
            Enum(self.Dwarf_uint8('children_flag'), **ENUM_DW_CHILDREN),
            RepeatUntilExcluding(
                lambda obj, ctx:
                    obj.name == 'DW_AT_null' and obj.form == 'DW_FORM_null',
                Struct('attr_spec',
                    Enum(self.Dwarf_uleb128('name'), **ENUM_DW_AT),
                    Enum(self.Dwarf_uleb128('form'), **ENUM_DW_FORM),
                    If(lambda ctx: ctx['form'] == 'DW_FORM_implicit_const',
                        self.Dwarf_sleb128('value')))))

    def _create_debugsup(self):
        # We don't care about checksums, for now.
        self.Dwarf_debugsup = Struct('Elf_debugsup',
            self.Dwarf_int16('version'),
            self.Dwarf_uint8('is_supplementary'),
            CString('sup_filename'))

    def _create_gnu_debugaltlink(self):
        self.Dwarf_debugaltlink = Struct('Elf_debugaltlink',
            CString("sup_filename"),
            String("sup_checksum", length=20))

    def _create_dw_form(self):
        self.Dwarf_dw_form = dict(
            DW_FORM_addr=self.the_Dwarf_target_addr,
            DW_FORM_addrx=self.the_Dwarf_uleb128,
            DW_FORM_addrx1=self.the_Dwarf_uint8,
            DW_FORM_addrx2=self.the_Dwarf_uint16,
            DW_FORM_addrx3=self.Dwarf_uint24(''),
            DW_FORM_addrx4=self.the_Dwarf_uint32,

            DW_FORM_block1=self._make_block_struct(self.Dwarf_uint8),
            DW_FORM_block2=self._make_block_struct(self.Dwarf_uint16),
            DW_FORM_block4=self._make_block_struct(self.Dwarf_uint32),
            DW_FORM_block=self._make_block_struct(self.Dwarf_uleb128),

            # All DW_FORM_data<n> forms are assumed to be unsigned
            DW_FORM_data1=self.the_Dwarf_uint8,
            DW_FORM_data2=self.the_Dwarf_uint16,
            DW_FORM_data4=self.the_Dwarf_uint32,
            DW_FORM_data8=self.Dwarf_uint64(''),
            DW_FORM_data16=Array(16, self.the_Dwarf_uint8), # Used for hashes and such, not for integers
            DW_FORM_sdata=self.the_Dwarf_sleb128,
            DW_FORM_udata=self.the_Dwarf_uleb128,

            DW_FORM_string=CString(''),
            DW_FORM_strp=self.the_Dwarf_offset,
            DW_FORM_strp_sup=self.the_Dwarf_offset,
            DW_FORM_line_strp=self.the_Dwarf_offset,
            DW_FORM_strx1=self.the_Dwarf_uint8,
            DW_FORM_strx2=self.the_Dwarf_uint16,
            DW_FORM_strx3=self.Dwarf_uint24(''),
            DW_FORM_strx4=self.Dwarf_uint64(''),
            DW_FORM_flag=self.the_Dwarf_uint8,

            DW_FORM_ref=self.the_Dwarf_uint32,
            DW_FORM_ref1=self.the_Dwarf_uint8,
            DW_FORM_ref2=self.the_Dwarf_uint16,
            DW_FORM_ref4=self.the_Dwarf_uint32,
            DW_FORM_ref_sup4=self.the_Dwarf_uint32,
            DW_FORM_ref8=self.Dwarf_uint64(''),
            DW_FORM_ref_sup8=self.Dwarf_uint64(''),
            DW_FORM_ref_udata=self.the_Dwarf_uleb128,
            DW_FORM_ref_addr=self.the_Dwarf_target_addr if self.dwarf_version == 2 else self.the_Dwarf_offset,

            DW_FORM_indirect=self.the_Dwarf_uleb128,
            
            # Treated separatedly while parsing, but here so that all forms resovle
            DW_FORM_implicit_const=None,

            # New forms in DWARFv4
            DW_FORM_flag_present = StaticField('', 0),
            DW_FORM_sec_offset = self.the_Dwarf_offset,
            DW_FORM_exprloc = self._make_block_struct(self.Dwarf_uleb128),
            DW_FORM_ref_sig8 = self.Dwarf_uint64(''),

            DW_FORM_GNU_strp_alt=self.the_Dwarf_offset,
            DW_FORM_GNU_ref_alt=self.the_Dwarf_offset,
            DW_AT_GNU_all_call_sites=self.the_Dwarf_uleb128,

            # New forms in DWARFv5
            DW_FORM_loclistx=self.the_Dwarf_uleb128,
            DW_FORM_rnglistx=self.the_Dwarf_uleb128
        )

    def _create_aranges_header(self):
        self.Dwarf_aranges_header = Struct("Dwarf_aranges_header",
            self.Dwarf_initial_length('unit_length'),
            self.Dwarf_uint16('version'),
            self.Dwarf_offset('debug_info_offset'), # a little tbd
            self.Dwarf_uint8('address_size'),
            self.Dwarf_uint8('segment_size')
            )

    def _create_nameLUT_header(self):
        self.Dwarf_nameLUT_header = Struct("Dwarf_nameLUT_header",
            self.Dwarf_initial_length('unit_length'),
            self.Dwarf_uint16('version'),
            self.Dwarf_offset('debug_info_offset'),
            self.Dwarf_length('debug_info_length')
            )

    def _create_string_offsets_table_header(self):
        self.Dwarf_string_offsets_table_header = Struct(
            "Dwarf_string_offets_table_header",
            self.Dwarf_initial_length('unit_length'),
            self.Dwarf_uint16('version'),
            self.Dwarf_uint16('padding'),
            )

    def _create_address_table_header(self):
        self.Dwarf_address_table_header = Struct("Dwarf_address_table_header",
            self.Dwarf_initial_length('unit_length'),
            self.Dwarf_uint16('version'),
            self.Dwarf_uint8('address_size'),
            self.Dwarf_uint8('segment_selector_size'),
            )

    def _create_lineprog_header(self):
        # A file entry is terminated by a NULL byte, so we don't want to parse
        # past it. Therefore an If is used.
        self.Dwarf_lineprog_file_entry = Struct('file_entry',
            CString('name'),
            If(lambda ctx: len(ctx.name) != 0,
                Embed(Struct('',
                    self.Dwarf_uleb128('dir_index'),
                    self.Dwarf_uleb128('mtime'),
                    self.Dwarf_uleb128('length')))))

        class FormattedEntry(Construct):
            # Generates a parser based on a previously parsed piece,
            # similar to deprecared Dynamic.
            # Strings are resolved later, since it potentially requires
            # looking at another section.
            def __init__(self, name, structs, format_field):
                Construct.__init__(self, name)
                self.structs = structs
                self.format_field = format_field

            def _parse(self, stream, context):
                # Somewhat tricky technique here, explicitly writing back to the context
                if self.format_field + "_parser" in context:
                    parser = context[self.format_field + "_parser"]
                else:
                    fields = tuple(
                        Rename(f.content_type, self.structs.Dwarf_dw_form[f.form])
                        for f in context[self.format_field])
                    parser = Struct('formatted_entry', *fields)
                    context[self.format_field + "_parser"] = parser
                return parser._parse(stream, context)

        ver5 = lambda ctx: ctx.version >= 5

        self.Dwarf_lineprog_header = Struct('Dwarf_lineprog_header',
            self.Dwarf_initial_length('unit_length'),
            self.Dwarf_uint16('version'),
            If(ver5,
                self.Dwarf_uint8("address_size"),
                None),
            If(ver5,
                self.Dwarf_uint8("segment_selector_size"),
                None),
            self.Dwarf_offset('header_length'),
            self.Dwarf_uint8('minimum_instruction_length'),
            If(lambda ctx: ctx.version >= 4,
                self.Dwarf_uint8("maximum_operations_per_instruction"),
                1),
            self.Dwarf_uint8('default_is_stmt'),
            self.Dwarf_int8('line_base'),
            self.Dwarf_uint8('line_range'),
            self.Dwarf_uint8('opcode_base'),
            Array(lambda ctx: ctx.opcode_base - 1,
                  self.Dwarf_uint8('standard_opcode_lengths')),
            If(ver5,
                PrefixedArray(
                    Struct('directory_entry_format',
                        Enum(self.Dwarf_uleb128('content_type'), **ENUM_DW_LNCT),
                        Enum(self.Dwarf_uleb128('form'), **ENUM_DW_FORM)),
                    self.Dwarf_uint8("directory_entry_format_count"))),
            If(ver5, # Name deliberately doesn't match the legacy object, since the format can't be made compatible
                PrefixedArray(
                    FormattedEntry('directories', self, "directory_entry_format"),
                    self.Dwarf_uleb128('directories_count'))),
            If(ver5,
                PrefixedArray(
                    Struct('file_name_entry_format',
                        Enum(self.Dwarf_uleb128('content_type'), **ENUM_DW_LNCT),
                        Enum(self.Dwarf_uleb128('form'), **ENUM_DW_FORM)),
                    self.Dwarf_uint8("file_name_entry_format_count"))),
            If(ver5,
                PrefixedArray(
                    FormattedEntry('file_names', self, "file_name_entry_format"),
                    self.Dwarf_uleb128('file_names_count'))),
            # Legacy  directories/files - DWARF < 5 only
            If(lambda ctx: ctx.version < 5,
                RepeatUntilExcluding(
                    lambda obj, ctx: obj == b'',
                    CString('include_directory'))),
            If(lambda ctx: ctx.version < 5,
                RepeatUntilExcluding(
                    lambda obj, ctx: len(obj.name) == 0,
                    self.Dwarf_lineprog_file_entry)) # array name is file_entry
        )

    def _create_callframe_entry_headers(self):
        self.Dwarf_CIE_header = Struct('Dwarf_CIE_header',
            self.Dwarf_initial_length('length'),
            self.Dwarf_offset('CIE_id'),
            self.Dwarf_uint8('version'),
            CString('augmentation'),
            If(lambda ctx: ctx.version >= 4, self.Dwarf_uint8('address_size')),
            If(lambda ctx: ctx.version >= 4, self.Dwarf_uint8('segment_size')),
            self.Dwarf_uleb128('code_alignment_factor'),
            self.Dwarf_sleb128('data_alignment_factor'),
            IfThenElse('return_address_register', lambda ctx: ctx.version > 1,
                self.Dwarf_uleb128(''),
                self.Dwarf_uint8('')))
        self.EH_CIE_header = self.Dwarf_CIE_header

        # The CIE header was modified in DWARFv4, but the
        # CIE header version is driven by the version # in the header
        # itself, independent of the DWARF version
        # in the CUs.

        self.Dwarf_FDE_header = Struct('Dwarf_FDE_header',
            self.Dwarf_initial_length('length'),
            self.Dwarf_offset('CIE_pointer'),
            self.Dwarf_target_addr('initial_location'),
            self.Dwarf_target_addr('address_range'))

    def _make_block_struct(self, length_field):
        """ Create a struct for DW_FORM_block<size>
        """
        return PrefixedArray(
                    subcon=self.Dwarf_uint8('elem'),
                    length_field=length_field(''))

    def _create_loclists_parsers(self):
        """ Create a struct for debug_loclists CU header, DWARFv5, 7,29
        """
        self.Dwarf_loclists_CU_header = Struct('Dwarf_loclists_CU_header',
            StreamOffset('cu_offset'),
            self.Dwarf_initial_length('unit_length'),
            Value('is64', lambda ctx: ctx.is64),
            StreamOffset('offset_after_length'),
            self.Dwarf_uint16('version'),
            self.Dwarf_uint8('address_size'),
            self.Dwarf_uint8('segment_selector_size'),
            self.Dwarf_uint32('offset_count'),
            StreamOffset('offset_table_offset'))

        cld = self.Dwarf_loclists_counted_location_description = PrefixedArray(self.Dwarf_uint8('loc_expr'), self.the_Dwarf_uleb128)

        self.Dwarf_loclists_entries = RepeatUntilExcluding(
            lambda obj, ctx: obj.entry_type == 'DW_LLE_end_of_list',
            Struct('entry',
                StreamOffset('entry_offset'),
                Enum(self.Dwarf_uint8('entry_type'), **ENUM_DW_LLE),
                Embed(Switch('', lambda ctx: ctx.entry_type,
                {
                    'DW_LLE_end_of_list'      : Struct('end_of_list'),
                    'DW_LLE_base_addressx'    : Struct('base_addressx', self.Dwarf_uleb128('index')),
                    'DW_LLE_startx_endx'      : Struct('startx_endx', self.Dwarf_uleb128('start_index'), self.Dwarf_uleb128('end_index'), cld),
                    'DW_LLE_startx_length'    : Struct('startx_endx', self.Dwarf_uleb128('start_index'), self.Dwarf_uleb128('length'), cld),
                    'DW_LLE_offset_pair'      : Struct('startx_endx', self.Dwarf_uleb128('start_offset'), self.Dwarf_uleb128('end_offset'), cld),
                    'DW_LLE_default_location' : Struct('default_location', cld),
                    'DW_LLE_base_address'     : Struct('base_address', self.Dwarf_target_addr('address')),
                    'DW_LLE_start_end'        : Struct('start_end', self.Dwarf_target_addr('start_address'), self.Dwarf_target_addr('end_address'), cld),
                    'DW_LLE_start_length'     : Struct('start_length', self.Dwarf_target_addr('start_address'), self.Dwarf_uleb128('length'), cld),
                })),
                StreamOffset('entry_end_offset'),
                Value('entry_length', lambda ctx: ctx.entry_end_offset - ctx.entry_offset)))

        self.Dwarf_locview_pair = Struct('locview_pair',
            StreamOffset('entry_offset'), self.Dwarf_uleb128('begin'), self.Dwarf_uleb128('end'))

    def _create_rnglists_parsers(self):
        self.Dwarf_rnglists_CU_header = Struct('Dwarf_rnglists_CU_header',
            StreamOffset('cu_offset'),
            self.Dwarf_initial_length('unit_length'),
            Value('is64', lambda ctx: ctx.is64),
            StreamOffset('offset_after_length'),
            self.Dwarf_uint16('version'),
            self.Dwarf_uint8('address_size'),
            self.Dwarf_uint8('segment_selector_size'),
            self.Dwarf_uint32('offset_count'),
            StreamOffset('offset_table_offset'))

        self.Dwarf_rnglists_entries = RepeatUntilExcluding(
            lambda obj, ctx: obj.entry_type == 'DW_RLE_end_of_list',
            Struct('entry',
                StreamOffset('entry_offset'),
                Enum(self.Dwarf_uint8('entry_type'), **ENUM_DW_RLE),
                Embed(Switch('', lambda ctx: ctx.entry_type,
                {
                    'DW_RLE_end_of_list'      : Struct('end_of_list'),
                    'DW_RLE_base_addressx'    : Struct('base_addressx', self.Dwarf_uleb128('index')),
                    'DW_RLE_startx_endx'      : Struct('startx_endx', self.Dwarf_uleb128('start_index'), self.Dwarf_uleb128('end_index')),
                    'DW_RLE_startx_length'    : Struct('startx_endx', self.Dwarf_uleb128('start_index'), self.Dwarf_uleb128('length')),
                    'DW_RLE_offset_pair'      : Struct('startx_endx', self.Dwarf_uleb128('start_offset'), self.Dwarf_uleb128('end_offset')),
                    'DW_RLE_base_address'     : Struct('base_address', self.Dwarf_target_addr('address')),
                    'DW_RLE_start_end'        : Struct('start_end', self.Dwarf_target_addr('start_address'), self.Dwarf_target_addr('end_address')),
                    'DW_RLE_start_length'     : Struct('start_length', self.Dwarf_target_addr('start_address'), self.Dwarf_uleb128('length'))
                })),
                StreamOffset('entry_end_offset'),
                Value('entry_length', lambda ctx: ctx.entry_end_offset - ctx.entry_offset)))


class _InitialLengthAdapter(Adapter):
    """ A standard Construct adapter that expects a sub-construct
        as a struct with one or two values (first, second).
    """
    def _decode(self, obj, context):
        if obj.first < 0xFFFFFF00:
            context['is64'] = False
            return obj.first
        else:
            if obj.first == 0xFFFFFFFF:
                context['is64'] = True
                return obj.second
            else:
                raise ConstructError("Failed decoding initial length for %X" % (
                    obj.first))
