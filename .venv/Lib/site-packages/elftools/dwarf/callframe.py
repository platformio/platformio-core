#-------------------------------------------------------------------------------
# elftools: dwarf/callframe.py
#
# DWARF call frame information
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import copy, os
from collections import namedtuple
from ..common.utils import (
    struct_parse, dwarf_assert, preserve_stream_pos, iterbytes)
from ..construct import Struct, Switch
from .enums import DW_EH_encoding_flags
from .structs import DWARFStructs
from .constants import *


class CallFrameInfo(object):
    """ DWARF CFI (Call Frame Info)

    Note that this also supports unwinding information as found in .eh_frame
    sections: its format differs slightly from the one in .debug_frame. See
    <http://www.airs.com/blog/archives/460>.

        stream, size:
            A stream holding the .debug_frame section, and the size of the
            section in it.

        address:
            Virtual address for this section. This is used to decode relative
            addresses.

        base_structs:
            The structs to be used as the base for parsing this section.
            Eventually, each entry gets its own structs based on the initial
            length field it starts with. The address_size, however, is taken
            from base_structs. This appears to be a limitation of the DWARFv3
            standard, fixed in v4.
            A discussion I had on dwarf-discuss confirms this.
            So for DWARFv4 we'll take the address size from the CIE header,
            but for earlier versions will use the elfclass of the containing
            file; more sophisticated methods are used by libdwarf and others,
            such as guessing which CU contains which FDEs (based on their
            address ranges) and taking the address_size from those CUs.
    """
    def __init__(self, stream, size, address, base_structs,
                 for_eh_frame=False):
        self.stream = stream
        self.size = size
        self.address = address
        self.base_structs = base_structs
        self.entries = None

        # Map between an offset in the stream and the entry object found at this
        # offset. Useful for assigning CIE to FDEs according to the CIE_pointer
        # header field which contains a stream offset.
        self._entry_cache = {}

        # The .eh_frame and .debug_frame section use almost the same CFI
        # encoding, but there are tiny variations we need to handle during
        # parsing.
        self.for_eh_frame = for_eh_frame

    def get_entries(self):
        """ Get a list of entries that constitute this CFI. The list consists
            of CIE or FDE objects, in the order of their appearance in the
            section.
        """
        if self.entries is None:
            self.entries = self._parse_entries()
        return self.entries

    #-------------------------

    def _parse_entries(self):
        entries = []
        offset = 0
        while offset < self.size:
            entries.append(self._parse_entry_at(offset))
            offset = self.stream.tell()
        return entries

    def _parse_entry_at(self, offset):
        """ Parse an entry from self.stream starting with the given offset.
            Return the entry object. self.stream will point right after the
            entry (even if pulled from the cache).
        """
        if offset in self._entry_cache:
            entry = self._entry_cache[offset]
            self.stream.seek(entry.header.length +
                entry.structs.initial_length_field_size(), os.SEEK_CUR)
            return entry

        entry_length = struct_parse(
            self.base_structs.the_Dwarf_uint32, self.stream, offset)

        if self.for_eh_frame and entry_length == 0:
            return ZERO(offset)

        dwarf_format = 64 if entry_length == 0xFFFFFFFF else 32

        # Theoretically possible to have a DWARF bitness transition here.
        # DWARF version doesn't matter (CIEs are versioned separately), endianness can't change.
        # The structs are cached though, so no extraneous creation.
        entry_structs = DWARFStructs(
            little_endian=self.base_structs.little_endian,
            dwarf_format=dwarf_format,
            address_size=self.base_structs.address_size)

        # Read the next field to see whether this is a CIE or FDE
        CIE_id = struct_parse(
            entry_structs.the_Dwarf_offset, self.stream)

        if self.for_eh_frame:
            is_CIE = CIE_id == 0
        else:
            is_CIE = (
                (dwarf_format == 32 and CIE_id == 0xFFFFFFFF) or
                CIE_id == 0xFFFFFFFFFFFFFFFF)

        # Parse the header, which goes up to and excluding the sequence of
        # instructions.
        if is_CIE:
            header_struct = (entry_structs.EH_CIE_header
                             if self.for_eh_frame else
                             entry_structs.Dwarf_CIE_header)
            header = struct_parse(
                header_struct, self.stream, offset)
        else:
            header = self._parse_fde_header(entry_structs, offset)

        # If the augmentation string is not empty, hope to find a length field
        # in order to skip the data specified augmentation.
        if is_CIE:
            aug_bytes, aug_dict = self._parse_cie_augmentation(
                    header, entry_structs)
        else:
            cie = self._parse_cie_for_fde(offset, header, entry_structs)
            aug_bytes = self._read_augmentation_data(entry_structs)
            lsda_encoding = cie.augmentation_dict.get('LSDA_encoding', DW_EH_encoding_flags['DW_EH_PE_omit'])
            if lsda_encoding != DW_EH_encoding_flags['DW_EH_PE_omit']:
                # parse LSDA pointer
                lsda_pointer = self._parse_lsda_pointer(entry_structs,
                                                        self.stream.tell() - len(aug_bytes),
                                                        lsda_encoding)
            else:
                lsda_pointer = None

        # For convenience, compute the end offset for this entry
        end_offset = (
            offset + header.length +
            entry_structs.initial_length_field_size())

        # At this point self.stream is at the start of the instruction list
        # for this entry
        instructions = self._parse_instructions(
            entry_structs, self.stream.tell(), end_offset)

        if is_CIE:
            entry = CIE(
                header=header, instructions=instructions, offset=offset,
                augmentation_dict=aug_dict,
                augmentation_bytes=aug_bytes,
                structs=entry_structs)

        else: # FDE
            cie = self._parse_cie_for_fde(offset, header, entry_structs)
            entry = FDE(
                header=header, instructions=instructions, offset=offset,
                structs=entry_structs, cie=cie,
                augmentation_bytes=aug_bytes,
                lsda_pointer=lsda_pointer,
            )
        self._entry_cache[offset] = entry
        return entry

    def _parse_instructions(self, structs, offset, end_offset):
        """ Parse a list of CFI instructions from self.stream, starting with
            the offset and until (not including) end_offset.
            Return a list of CallFrameInstruction objects.
        """
        instructions = []
        while offset < end_offset:
            opcode = struct_parse(structs.the_Dwarf_uint8, self.stream, offset)
            args = []

            primary = opcode & _PRIMARY_MASK
            primary_arg = opcode & _PRIMARY_ARG_MASK
            if primary == DW_CFA_advance_loc:
                args = [primary_arg]
            elif primary == DW_CFA_offset:
                args = [
                    primary_arg,
                    struct_parse(structs.the_Dwarf_uleb128, self.stream)]
            elif primary == DW_CFA_restore:
                args = [primary_arg]
            # primary == 0 and real opcode is extended
            elif opcode in (DW_CFA_nop, DW_CFA_remember_state,
                            DW_CFA_restore_state, DW_CFA_AARCH64_negate_ra_state):
                args = []
            elif opcode == DW_CFA_set_loc:
                args = [
                    struct_parse(structs.the_Dwarf_target_addr, self.stream)]
            elif opcode == DW_CFA_advance_loc1:
                args = [struct_parse(structs.the_Dwarf_uint8, self.stream)]
            elif opcode == DW_CFA_advance_loc2:
                args = [struct_parse(structs.the_Dwarf_uint16, self.stream)]
            elif opcode == DW_CFA_advance_loc4:
                args = [struct_parse(structs.the_Dwarf_uint32, self.stream)]
            elif opcode in (DW_CFA_offset_extended, DW_CFA_register,
                            DW_CFA_def_cfa, DW_CFA_val_offset):
                args = [
                    struct_parse(structs.the_Dwarf_uleb128, self.stream),
                    struct_parse(structs.the_Dwarf_uleb128, self.stream)]
            elif opcode in (DW_CFA_restore_extended, DW_CFA_undefined,
                            DW_CFA_same_value, DW_CFA_def_cfa_register,
                            DW_CFA_def_cfa_offset):
                args = [struct_parse(structs.the_Dwarf_uleb128, self.stream)]
            elif opcode == DW_CFA_def_cfa_offset_sf:
                args = [struct_parse(structs.the_Dwarf_sleb128, self.stream)]
            elif opcode == DW_CFA_def_cfa_expression:
                args = [struct_parse(
                    structs.Dwarf_dw_form['DW_FORM_block'], self.stream)]
            elif opcode in (DW_CFA_expression, DW_CFA_val_expression):
                args = [
                    struct_parse(structs.the_Dwarf_uleb128, self.stream),
                    struct_parse(
                        structs.Dwarf_dw_form['DW_FORM_block'], self.stream)]
            elif opcode in (DW_CFA_offset_extended_sf,
                            DW_CFA_def_cfa_sf, DW_CFA_val_offset_sf):
                args = [
                    struct_parse(structs.the_Dwarf_uleb128, self.stream),
                    struct_parse(structs.the_Dwarf_sleb128, self.stream)]
            elif opcode == DW_CFA_GNU_args_size:
                args = [struct_parse(structs.the_Dwarf_uleb128, self.stream)]
            
            else:
                dwarf_assert(False, 'Unknown CFI opcode: 0x%x' % opcode)

            instructions.append(CallFrameInstruction(opcode=opcode, args=args))
            offset = self.stream.tell()
        return instructions

    def _parse_cie_for_fde(self, fde_offset, fde_header, entry_structs):
        """ Parse the CIE that corresponds to an FDE.
        """
        # Determine the offset of the CIE that corresponds to this FDE
        if self.for_eh_frame:
            # CIE_pointer contains the offset for a reverse displacement from
            # the section offset of the CIE_pointer field itself (not from the
            # FDE header offset).
            cie_displacement = fde_header['CIE_pointer']
            cie_offset = (fde_offset + entry_structs.dwarf_format // 8
                          - cie_displacement)
        else:
            cie_offset = fde_header['CIE_pointer']

        # Then read it
        with preserve_stream_pos(self.stream):
            return self._parse_entry_at(cie_offset)

    def _parse_cie_augmentation(self, header, entry_structs):
        """ Parse CIE augmentation data from the annotation string in `header`.

        Return a tuple that contains 1) the augmentation data as a string
        (without the length field) and 2) the augmentation data as a dict.
        """
        augmentation = header.get('augmentation')
        if not augmentation:
            return ('', {})

        # Augmentation parsing works in minimal mode here: we need the length
        # field to be able to skip unhandled augmentation fields.
        assert augmentation.startswith(b'z'), (
            'Unhandled augmentation string: {}'.format(repr(augmentation)))

        available_fields = {
            b'z': entry_structs.Dwarf_uleb128('length'),
            b'L': entry_structs.Dwarf_uint8('LSDA_encoding'),
            b'R': entry_structs.Dwarf_uint8('FDE_encoding'),
            b'S': True,
            b'P': Struct(
                'personality',
                entry_structs.Dwarf_uint8('encoding'),
                Switch('function', lambda ctx: ctx.encoding & 0x0f, {
                    enc: fld_cons('function')
                    for enc, fld_cons
                    in self._eh_encoding_to_field(entry_structs).items()})),
        }

        # Build the Struct we will be using to parse the augmentation data.
        # Stop as soon as we are not able to match the augmentation string.
        fields = []
        aug_dict = {}

        for b in iterbytes(augmentation):
            try:
                fld = available_fields[b]
            except KeyError:
                break

            if fld is True:
                aug_dict[fld] = True
            else:
                fields.append(fld)

        # Read the augmentation twice: once with the Struct, once for the raw
        # bytes. Read the raw bytes last so we are sure we leave the stream
        # pointing right after the augmentation: the Struct may be incomplete
        # (missing trailing fields) due to an unknown char: see the KeyError
        # above.
        offset = self.stream.tell()
        struct = Struct('Augmentation_Data', *fields)
        aug_dict.update(struct_parse(struct, self.stream, offset))
        self.stream.seek(offset)
        aug_bytes = self._read_augmentation_data(entry_structs)
        return (aug_bytes, aug_dict)

    def _read_augmentation_data(self, entry_structs):
        """ Read augmentation data.

        This assumes that the augmentation string starts with 'z', i.e. that
        augmentation data is prefixed by a length field, which is not returned.
        """
        if not self.for_eh_frame:
            return b''

        augmentation_data_length = struct_parse(
            Struct('Dummy_Augmentation_Data',
                   entry_structs.Dwarf_uleb128('length')),
            self.stream)['length']
        return self.stream.read(augmentation_data_length)

    def _parse_lsda_pointer(self, structs, stream_offset, encoding):
        """ Parse bytes to get an LSDA pointer.

        The basic encoding (lower four bits of the encoding) describes how the values are encoded in a CIE or an FDE.
        The modifier (upper four bits of the encoding) describes how the raw values, after decoded using a basic
        encoding, should be modified before using.

        Ref: https://www.airs.com/blog/archives/460
        """
        assert encoding != DW_EH_encoding_flags['DW_EH_PE_omit']
        basic_encoding = encoding & 0x0f
        modifier = encoding & 0xf0

        formats = self._eh_encoding_to_field(structs)

        ptr = struct_parse(
            Struct('Augmentation_Data',
                   formats[basic_encoding]('LSDA_pointer')),
            self.stream, stream_pos=stream_offset)['LSDA_pointer']

        if modifier == DW_EH_encoding_flags['DW_EH_PE_absptr']:
            pass

        elif modifier == DW_EH_encoding_flags['DW_EH_PE_pcrel']:
            ptr += self.address + stream_offset

        else:
            assert False, 'Unsupported encoding modifier for LSDA pointer: {:#x}'.format(modifier)

        return ptr

    def _parse_fde_header(self, entry_structs, offset):
        """ Compute a struct to parse the header of the current FDE.
        """
        if not self.for_eh_frame:
            return struct_parse(entry_structs.Dwarf_FDE_header, self.stream,
                                offset)

        fields = [entry_structs.Dwarf_initial_length('length'),
                  entry_structs.Dwarf_offset('CIE_pointer')]

        # Parse the couple of header fields that are always here so we can
        # fetch the corresponding CIE.
        minimal_header = struct_parse(Struct('eh_frame_minimal_header',
                                             *fields), self.stream, offset)
        cie = self._parse_cie_for_fde(offset, minimal_header, entry_structs)
        initial_location_offset = self.stream.tell()

        # Try to parse the initial location. We need the initial location in
        # order to create a meaningful FDE, so assume it's there. Omission does
        # not seem to happen in practice.
        encoding = cie.augmentation_dict['FDE_encoding']
        assert encoding != DW_EH_encoding_flags['DW_EH_PE_omit']
        basic_encoding = encoding & 0x0f
        encoding_modifier = encoding & 0xf0

        # Depending on the specified encoding, complete the header Struct
        formats = self._eh_encoding_to_field(entry_structs)
        fields.append(formats[basic_encoding]('initial_location'))
        fields.append(formats[basic_encoding]('address_range'))

        result = struct_parse(Struct('Dwarf_FDE_header', *fields),
                              self.stream, offset)

        if encoding_modifier == 0:
            pass

        elif encoding_modifier == DW_EH_encoding_flags['DW_EH_PE_pcrel']:
            # Start address is relative to the address of the
            # "initial_location" field.
            result['initial_location'] += (
                self.address + initial_location_offset)
        else:
            assert False, 'Unsupported encoding: {:#x}'.format(encoding)

        return result

    @staticmethod
    def _eh_encoding_to_field(entry_structs):
        """
        Return a mapping from basic encodings (DW_EH_encoding_flags) the
        corresponding field constructors (for instance
        entry_structs.Dwarf_uint32).
        """
        return {
            DW_EH_encoding_flags['DW_EH_PE_absptr']:
                entry_structs.Dwarf_target_addr,
            DW_EH_encoding_flags['DW_EH_PE_uleb128']:
                entry_structs.Dwarf_uleb128,
            DW_EH_encoding_flags['DW_EH_PE_udata2']:
                entry_structs.Dwarf_uint16,
            DW_EH_encoding_flags['DW_EH_PE_udata4']:
                entry_structs.Dwarf_uint32,
            DW_EH_encoding_flags['DW_EH_PE_udata8']:
                entry_structs.Dwarf_uint64,

            DW_EH_encoding_flags['DW_EH_PE_sleb128']:
                entry_structs.Dwarf_sleb128,
            DW_EH_encoding_flags['DW_EH_PE_sdata2']:
                entry_structs.Dwarf_int16,
            DW_EH_encoding_flags['DW_EH_PE_sdata4']:
                entry_structs.Dwarf_int32,
            DW_EH_encoding_flags['DW_EH_PE_sdata8']:
                entry_structs.Dwarf_int64,
        }


def instruction_name(opcode):
    """ Given an opcode, return the instruction name.
    """
    primary = opcode & _PRIMARY_MASK
    if primary == 0:
        return _OPCODE_NAME_MAP[opcode]
    else:
        return _OPCODE_NAME_MAP[primary]


class CallFrameInstruction(object):
    """ An instruction in the CFI section. opcode is the instruction
        opcode, numeric - as it appears in the section. args is a list of
        arguments (including arguments embedded in the low bits of some
        instructions, when applicable), decoded from the stream.
    """
    def __init__(self, opcode, args):
        self.opcode = opcode
        self.args = args

    def __repr__(self):
        return '%s (0x%x): %s' % (
            instruction_name(self.opcode), self.opcode, self.args)


class CFIEntry(object):
    """ A common base class for CFI entries.
        Contains a header and a list of instructions (CallFrameInstruction).
        offset: the offset of this entry from the beginning of the section
        cie: for FDEs, a CIE pointer is required
        augmentation_dict: Augmentation data as a parsed struct (dict): see
            CallFrameInfo._parse_cie_augmentation and
            http://www.airs.com/blog/archives/460.
        augmentation_bytes: Augmentation data as a chain of bytes: see
            CallFrameInfo._parse_cie_augmentation and
            http://www.airs.com/blog/archives/460.
    """
    def __init__(self, header, structs, instructions, offset,
            augmentation_dict=None, augmentation_bytes=b'', cie=None):
        self.header = header
        self.structs = structs
        self.instructions = instructions
        self.offset = offset
        self.cie = cie
        self._decoded_table = None
        self.augmentation_dict = augmentation_dict if augmentation_dict else {}
        self.augmentation_bytes = augmentation_bytes

    def get_decoded(self):
        """ Decode the CFI contained in this entry and return a
            DecodedCallFrameTable object representing it. See the documentation
            of that class to understand how to interpret the decoded table.
        """
        if self._decoded_table is None:
            self._decoded_table = self._decode_CFI_table()
        return self._decoded_table

    def __getitem__(self, name):
        """ Implement dict-like access to header entries
        """
        return self.header[name]

    def _decode_CFI_table(self):
        """ Decode the instructions contained in the given CFI entry and return
            a DecodedCallFrameTable.
        """
        if isinstance(self, CIE):
            # For a CIE, initialize cur_line to an "empty" line
            cie = self
            cur_line = dict(pc=0, cfa=CFARule(reg=None, offset=0))
            reg_order = []
        else: # FDE
            # For a FDE, we need to decode the attached CIE first, because its
            # decoded table is needed. Its "initial instructions" describe a
            # line that serves as the base (first) line in the FDE's table.
            cie = self.cie
            cie_decoded_table = cie.get_decoded()
            if len(cie_decoded_table.table) > 0:
                last_line_in_CIE = copy.copy(cie_decoded_table.table[-1])
                cur_line = copy.copy(last_line_in_CIE)
            else:
                cur_line = dict(cfa=CFARule(reg=None, offset=0))
            cur_line['pc'] = self['initial_location']
            reg_order = copy.copy(cie_decoded_table.reg_order)

        table = []

        # Keeps a stack for the use of DW_CFA_{remember|restore}_state
        # instructions.
        line_stack = []

        def _add_to_order(regnum):
            # DW_CFA_restore and others remove registers from cur_line,
            #  but they stay in reg_order. Avoid duplicates.
            if regnum not in reg_order:
                reg_order.append(regnum)

        for instr in self.instructions:
            # Throughout this loop, cur_line is the current line. Some
            # instructions add it to the table, but most instructions just
            # update it without adding it to the table.

            name = instruction_name(instr.opcode)

            if name == 'DW_CFA_set_loc':
                table.append(copy.copy(cur_line))
                cur_line['pc'] = instr.args[0]
            elif name in (  'DW_CFA_advance_loc1', 'DW_CFA_advance_loc2',
                            'DW_CFA_advance_loc4', 'DW_CFA_advance_loc'):
                table.append(copy.copy(cur_line))
                cur_line['pc'] += instr.args[0] * cie['code_alignment_factor']
            elif name == 'DW_CFA_def_cfa':
                cur_line['cfa'] = CFARule(
                    reg=instr.args[0],
                    offset=instr.args[1])
            elif name == 'DW_CFA_def_cfa_sf':
                cur_line['cfa'] = CFARule(
                    reg=instr.args[0],
                    offset=instr.args[1] * cie['code_alignment_factor'])
            elif name == 'DW_CFA_def_cfa_register':
                cur_line['cfa'] = CFARule(
                    reg=instr.args[0],
                    offset=cur_line['cfa'].offset)
            elif name == 'DW_CFA_def_cfa_offset':
                cur_line['cfa'] = CFARule(
                    reg=cur_line['cfa'].reg,
                    offset=instr.args[0])
            elif name == 'DW_CFA_def_cfa_offset_sf':
                cur_line['cfa'] = CFARule(
                    reg=cur_line['cfa'].reg,
                    offset=instr.args[0] * cie['data_alignment_factor'])
            elif name == 'DW_CFA_def_cfa_expression':
                cur_line['cfa'] = CFARule(expr=instr.args[0])
            elif name == 'DW_CFA_undefined':
                _add_to_order(instr.args[0])
                cur_line[instr.args[0]] = RegisterRule(RegisterRule.UNDEFINED)
            elif name == 'DW_CFA_same_value':
                _add_to_order(instr.args[0])
                cur_line[instr.args[0]] = RegisterRule(RegisterRule.SAME_VALUE)
            elif name in (  'DW_CFA_offset', 'DW_CFA_offset_extended',
                            'DW_CFA_offset_extended_sf'):
                _add_to_order(instr.args[0])
                cur_line[instr.args[0]] = RegisterRule(
                    RegisterRule.OFFSET,
                    instr.args[1] * cie['data_alignment_factor'])
            elif name in ('DW_CFA_val_offset', 'DW_CFA_val_offset_sf'):
                _add_to_order(instr.args[0])
                cur_line[instr.args[0]] = RegisterRule(
                    RegisterRule.VAL_OFFSET,
                    instr.args[1] * cie['data_alignment_factor'])
            elif name == 'DW_CFA_register':
                _add_to_order(instr.args[0])
                cur_line[instr.args[0]] = RegisterRule(
                    RegisterRule.REGISTER,
                    instr.args[1])
            elif name == 'DW_CFA_expression':
                _add_to_order(instr.args[0])
                cur_line[instr.args[0]] = RegisterRule(
                    RegisterRule.EXPRESSION,
                    instr.args[1])
            elif name == 'DW_CFA_val_expression':
                _add_to_order(instr.args[0])
                cur_line[instr.args[0]] = RegisterRule(
                    RegisterRule.VAL_EXPRESSION,
                    instr.args[1])
            elif name in ('DW_CFA_restore', 'DW_CFA_restore_extended'):
                _add_to_order(instr.args[0])
                dwarf_assert(
                    isinstance(self, FDE),
                    '%s instruction must be in a FDE' % name)
                if instr.args[0] in last_line_in_CIE:
                    cur_line[instr.args[0]] = last_line_in_CIE[instr.args[0]]
                else:
                    cur_line.pop(instr.args[0], None)
            elif name == 'DW_CFA_remember_state':
                line_stack.append(copy.deepcopy(cur_line))
            elif name == 'DW_CFA_restore_state':
                pc = cur_line['pc']
                cur_line = line_stack.pop()
                cur_line['pc'] = pc

        # The current line is appended to the table after all instructions
        # have ended, if there were instructions.
        if cur_line['cfa'].reg is not None or len(cur_line) > 2:
            table.append(cur_line)

        return DecodedCallFrameTable(table=table, reg_order=reg_order)


# A CIE and FDE have exactly the same functionality, except that a FDE has
# a pointer to its CIE. The functionality was wholly encapsulated in CFIEntry,
# so the CIE and FDE classes exists separately for identification (instead
# of having an explicit "entry_type" field in CFIEntry).
#
class CIE(CFIEntry):
    pass


class FDE(CFIEntry):
    def __init__(self, header, structs, instructions, offset, augmentation_bytes=None, cie=None, lsda_pointer=None):
        super(FDE, self).__init__(header, structs, instructions, offset, augmentation_bytes=augmentation_bytes, cie=cie)
        self.lsda_pointer = lsda_pointer


class ZERO(object):
    """ End marker for the sequence of CIE/FDE.

    This is specific to `.eh_frame` sections: this kind of entry does not exist
    in pure DWARF. `readelf` displays these as "ZERO terminator", hence the
    class name.
    """
    def __init__(self, offset):
        self.offset = offset


class RegisterRule(object):
    """ Register rules are used to find registers in call frames. Each rule
        consists of a type (enumeration following DWARFv3 section 6.4.1)
        and an optional argument to augment the type.
    """
    UNDEFINED = 'UNDEFINED'
    SAME_VALUE = 'SAME_VALUE'
    OFFSET = 'OFFSET'
    VAL_OFFSET = 'VAL_OFFSET'
    REGISTER = 'REGISTER'
    EXPRESSION = 'EXPRESSION'
    VAL_EXPRESSION = 'VAL_EXPRESSION'
    ARCHITECTURAL = 'ARCHITECTURAL'

    def __init__(self, type, arg=None):
        self.type = type
        self.arg = arg

    def __repr__(self):
        return 'RegisterRule(%s, %s)' % (self.type, self.arg)


class CFARule(object):
    """ A CFA rule is used to compute the CFA for each location. It either
        consists of a register+offset, or a DWARF expression.
    """
    def __init__(self, reg=None, offset=None, expr=None):
        self.reg = reg
        self.offset = offset
        self.expr = expr

    def __repr__(self):
        return 'CFARule(reg=%s, offset=%s, expr=%s)' % (
            self.reg, self.offset, self.expr)


# Represents the decoded CFI for an entry, which is just a large table,
# according to DWARFv3 section 6.4.1
#
# DecodedCallFrameTable is a simple named tuple to group together the table
# and the register appearance order.
#
# table:
#
# A list of dicts that represent "lines" in the decoded table. Each line has
# some special dict entries: 'pc' for the location/program counter (LOC),
# and 'cfa' for the CFARule to locate the CFA on that line.
# The other entries are keyed by register numbers with RegisterRule values,
# and describe the rules for these registers.
#
# reg_order:
#
# A list of register numbers that are described in the table by the order of
# their appearance.
#
DecodedCallFrameTable = namedtuple(
    'DecodedCallFrameTable', 'table reg_order')


#---------------- PRIVATE ----------------#

_PRIMARY_MASK = 0b11000000
_PRIMARY_ARG_MASK = 0b00111111

# This dictionary is filled by automatically scanning the constants module
# for DW_CFA_* instructions, and mapping their values to names. Since all
# names were imported from constants with `import *`, we look in globals()
_OPCODE_NAME_MAP = {}
for name in list(globals().keys()):
    if name.startswith('DW_CFA'):
        _OPCODE_NAME_MAP[globals()[name]] = name
