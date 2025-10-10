#-------------------------------------------------------------------------------
# elftools: dwarf/lineprogram.py
#
# DWARF line number program
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os
import copy
from collections import namedtuple

from ..common.utils import struct_parse, dwarf_assert
from .constants import *


# LineProgramEntry - an entry in the line program.
# A line program is a sequence of encoded entries. Some of these entries add a
# new LineState (mapping between line and address), and some don't.
#
# command:
#   The command/opcode - always numeric. For standard commands - it's the opcode
#   that can be matched with one of the DW_LNS_* constants. For extended commands
#   it's the extended opcode that can be matched with one of the DW_LNE_*
#   constants. For special commands, it's the opcode itself.
#
# args:
#   A list of decoded arguments of the command.
#
# is_extended:
#   Since extended commands are encoded by a zero followed by an extended
#   opcode, and these extended opcodes overlap with other opcodes, this
#   flag is needed to mark that the command has an extended opcode.
#
# state:
#   For commands that add a new state, it's the relevant LineState object.
#   For commands that don't add a new state, it's None.
#
LineProgramEntry = namedtuple(
    'LineProgramEntry', 'command is_extended args state')


class LineState(object):
    """ Represents a line program state (or a "row" in the matrix
        describing debug location information for addresses).
        The instance variables of this class are the "state machine registers"
        described in section 6.2.2 of DWARFv3
    """
    def __init__(self, default_is_stmt):
        self.address = 0
        self.file = 1
        self.line = 1
        self.column = 0
        self.op_index = 0
        self.is_stmt = default_is_stmt
        self.basic_block = False
        self.end_sequence = False
        self.prologue_end = False
        self.epilogue_begin = False
        self.isa = 0
        self.discriminator = 0

    def __repr__(self):
        a = ['<LineState %x:' % id(self)]
        a.append('  address = 0x%x' % self.address)
        for attr in ('file', 'line', 'column', 'is_stmt', 'basic_block',
                     'end_sequence', 'prologue_end', 'epilogue_begin', 'isa',
                     'discriminator'):
            a.append('  %s = %s' % (attr, getattr(self, attr)))
        return '\n'.join(a) + '>\n'


class LineProgram(object):
    """ Builds a "line table", which is essentially the matrix described
        in section 6.2 of DWARFv3. It's a list of LineState objects,
        sorted by increasing address, so it can be used to obtain the
        state information for each address.
    """
    def __init__(self, header, stream, structs,
                 program_start_offset, program_end_offset):
        """
            header:
                The header of this line program. Note: LineProgram may modify
                its header by appending file entries if DW_LNE_define_file
                instructions are encountered.

            stream:
                The stream this program can be read from.

            structs:
                A DWARFStructs instance suitable for this line program

            program_{start|end}_offset:
                Offset in the debug_line section stream where this program
                starts (the actual program, after the header), and where it
                ends.
                The actual range includes start but not end: [start, end - 1]
        """
        self.stream = stream
        self.header = header
        self.structs = structs
        self.program_start_offset = program_start_offset
        self.program_end_offset = program_end_offset
        self._decoded_entries = None

    def get_entries(self):
        """ Get the decoded entries for this line program. Return a list of
            LineProgramEntry objects.
            Note that this contains more information than absolutely required
            for the line table. The line table can be easily extracted from
            the list of entries by looking only at entries with non-None
            state. The extra information is mainly for the purposes of display
            with readelf and debugging.
        """
        if self._decoded_entries is None:
            self._decoded_entries = self._decode_line_program()
        return self._decoded_entries

    #------ PRIVATE ------#

    def __getitem__(self, name):
        """ Implement dict-like access to header entries
        """
        return self.header[name]

    def _decode_line_program(self):
        entries = []
        state = LineState(self.header['default_is_stmt'])

        def add_entry_new_state(cmd, args, is_extended=False):
            # Add an entry that sets a new state.
            # After adding, clear some state registers.
            entries.append(LineProgramEntry(
                cmd, is_extended, args, copy.copy(state)))
            state.discriminator = 0
            state.basic_block = False
            state.prologue_end = False
            state.epilogue_begin = False

        def add_entry_old_state(cmd, args, is_extended=False):
            # Add an entry that doesn't visibly set a new state
            entries.append(LineProgramEntry(cmd, is_extended, args, None))

        offset = self.program_start_offset
        while offset < self.program_end_offset:
            opcode = struct_parse(
                self.structs.the_Dwarf_uint8,
                self.stream,
                offset)

            # As an exercise in avoiding premature optimization, if...elif
            # chains are used here for standard and extended opcodes instead
            # of dispatch tables. This keeps the code much cleaner. Besides,
            # the majority of instructions in a typical program are special
            # opcodes anyway.
            if opcode >= self.header['opcode_base']:
                # Special opcode (follow the recipe in 6.2.5.1)
                maximum_operations_per_instruction = self['maximum_operations_per_instruction']
                adjusted_opcode = opcode - self['opcode_base']
                operation_advance = adjusted_opcode // self['line_range']
                address_addend = (
                    self['minimum_instruction_length'] *
                        ((state.op_index + operation_advance) //
                          maximum_operations_per_instruction))
                state.address += address_addend
                state.op_index = (state.op_index + operation_advance) % maximum_operations_per_instruction
                line_addend = self['line_base'] + (adjusted_opcode % self['line_range'])
                state.line += line_addend
                add_entry_new_state(
                    opcode, [line_addend, address_addend, state.op_index])
            elif opcode == 0:
                # Extended opcode: start with a zero byte, followed by
                # instruction size and the instruction itself.
                inst_len = struct_parse(self.structs.the_Dwarf_uleb128,
                                        self.stream)
                ex_opcode = struct_parse(self.structs.the_Dwarf_uint8,
                                         self.stream)

                if ex_opcode == DW_LNE_end_sequence:
                    state.end_sequence = True
                    state.is_stmt = 0
                    add_entry_new_state(ex_opcode, [], is_extended=True)
                    # reset state
                    state = LineState(self.header['default_is_stmt'])
                elif ex_opcode == DW_LNE_set_address:
                    operand = struct_parse(self.structs.the_Dwarf_target_addr,
                                           self.stream)
                    state.address = operand
                    add_entry_old_state(ex_opcode, [operand], is_extended=True)
                elif ex_opcode == DW_LNE_define_file:
                    operand = struct_parse(
                        self.structs.Dwarf_lineprog_file_entry, self.stream)
                    self['file_entry'].append(operand)
                    add_entry_old_state(ex_opcode, [operand], is_extended=True)
                elif ex_opcode == DW_LNE_set_discriminator:
                    operand = struct_parse(self.structs.the_Dwarf_uleb128,
                                           self.stream)
                    state.discriminator = operand
                else:
                    # Unknown, but need to roll forward the stream because the
                    # length is specified. Seek forward inst_len - 1 because
                    # we've already read the extended opcode, which takes part
                    # in the length.
                    self.stream.seek(inst_len - 1, os.SEEK_CUR)
            else: # 0 < opcode < opcode_base
                # Standard opcode
                if opcode == DW_LNS_copy:
                    add_entry_new_state(opcode, [])
                elif opcode == DW_LNS_advance_pc:
                    operand = struct_parse(self.structs.the_Dwarf_uleb128,
                                           self.stream)
                    address_addend = (
                        operand * self.header['minimum_instruction_length'])
                    state.address += address_addend
                    add_entry_old_state(opcode, [address_addend])
                elif opcode == DW_LNS_advance_line:
                    operand = struct_parse(self.structs.the_Dwarf_sleb128,
                                           self.stream)
                    state.line += operand
                elif opcode == DW_LNS_set_file:
                    operand = struct_parse(self.structs.the_Dwarf_uleb128,
                                           self.stream)
                    state.file = operand
                    add_entry_old_state(opcode, [operand])
                elif opcode == DW_LNS_set_column:
                    operand = struct_parse(self.structs.the_Dwarf_uleb128,
                                           self.stream)
                    state.column = operand
                    add_entry_old_state(opcode, [operand])
                elif opcode == DW_LNS_negate_stmt:
                    state.is_stmt = not state.is_stmt
                    add_entry_old_state(opcode, [])
                elif opcode == DW_LNS_set_basic_block:
                    state.basic_block = True
                    add_entry_old_state(opcode, [])
                elif opcode == DW_LNS_const_add_pc:
                    adjusted_opcode = 255 - self['opcode_base']
                    address_addend = ((adjusted_opcode // self['line_range']) *
                                      self['minimum_instruction_length'])
                    state.address += address_addend
                    add_entry_old_state(opcode, [address_addend])
                elif opcode == DW_LNS_fixed_advance_pc:
                    operand = struct_parse(self.structs.the_Dwarf_uint16,
                                           self.stream)
                    state.address += operand
                    add_entry_old_state(opcode, [operand])
                elif opcode == DW_LNS_set_prologue_end:
                    state.prologue_end = True
                    add_entry_old_state(opcode, [])
                elif opcode == DW_LNS_set_epilogue_begin:
                    state.epilogue_begin = True
                    add_entry_old_state(opcode, [])
                elif opcode == DW_LNS_set_isa:
                    operand = struct_parse(self.structs.the_Dwarf_uleb128,
                                           self.stream)
                    state.isa = operand
                    add_entry_old_state(opcode, [operand])
                else:
                    dwarf_assert(False, 'Invalid standard line program opcode: %s' % (
                        opcode,))
            offset = self.stream.tell()
        return entries
