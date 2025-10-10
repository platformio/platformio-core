# -------------------------------------------------------------------------------
# elftools: ehabi/ehabiinfo.py
#
# Decoder for ARM exception handler bytecode.
#
# LeadroyaL (leadroyal@qq.com)
# This code is in the public domain
# -------------------------------------------------------------------------------

from ..common.utils import struct_parse

from .decoder import EHABIBytecodeDecoder
from .constants import EHABI_INDEX_ENTRY_SIZE
from .structs import EHABIStructs


class EHABIInfo(object):
    """ ARM exception handler abi information class.

        Parameters:

            arm_idx_section:
                elf.sections.Section object, section which type is SHT_ARM_EXIDX.

            little_endian:
                bool, endianness of elf file.
    """

    def __init__(self, arm_idx_section, little_endian):
        self._arm_idx_section = arm_idx_section
        self._struct = EHABIStructs(little_endian)
        self._num_entry = None

    def section_name(self):
        return self._arm_idx_section.name

    def section_offset(self):
        return self._arm_idx_section['sh_offset']

    def num_entry(self):
        """ Number of exception handler entry in the section.
        """
        if self._num_entry is None:
            self._num_entry = self._arm_idx_section['sh_size'] // EHABI_INDEX_ENTRY_SIZE
        return self._num_entry

    def get_entry(self, n):
        """ Get the exception handler entry at index #n. (EHABIEntry object or a subclass)
        """
        if n >= self.num_entry():
            raise IndexError('Invalid entry %d/%d' % (n, self._num_entry))
        eh_index_entry_offset = self.section_offset() + n * EHABI_INDEX_ENTRY_SIZE
        eh_index_data = struct_parse(self._struct.EH_index_struct, self._arm_idx_section.stream, eh_index_entry_offset)
        word0, word1 = eh_index_data['word0'], eh_index_data['word1']

        if word0 & 0x80000000 != 0:
            return CorruptEHABIEntry('Corrupt ARM exception handler table entry: %x' % n)

        function_offset = arm_expand_prel31(word0, self.section_offset() + n * EHABI_INDEX_ENTRY_SIZE)

        if word1 == 1:
            # 0x1 means cannot unwind
            return CannotUnwindEHABIEntry(function_offset)
        elif word1 & 0x80000000 == 0:
            # highest bit is zero, point to .ARM.extab data
            eh_table_offset = arm_expand_prel31(word1, self.section_offset() + n * EHABI_INDEX_ENTRY_SIZE + 4)
            eh_index_data = struct_parse(self._struct.EH_table_struct, self._arm_idx_section.stream, eh_table_offset)
            word0 = eh_index_data['word0']
            if word0 & 0x80000000 == 0:
                # highest bit is one, generic model
                return GenericEHABIEntry(function_offset, arm_expand_prel31(word0, eh_table_offset))
            else:
                # highest bit is one, arm compact model
                # highest half must be 0b1000 for compact model
                if word0 & 0x70000000 != 0:
                    return CorruptEHABIEntry('Corrupt ARM compact model table entry: %x' % n)
                per_index = (word0 >> 24) & 0x7f
                if per_index == 0:
                    # arm compact model 0
                    opcode = [(word0 & 0xFF0000) >> 16, (word0 & 0xFF00) >> 8, word0 & 0xFF]
                    return EHABIEntry(function_offset, per_index, opcode)
                elif per_index == 1 or per_index == 2:
                    # arm compact model 1/2
                    more_word = (word0 >> 16) & 0xff
                    opcode = [(word0 >> 8) & 0xff, (word0 >> 0) & 0xff]
                    self._arm_idx_section.stream.seek(eh_table_offset + 4)
                    for i in range(more_word):
                        r = struct_parse(self._struct.EH_table_struct, self._arm_idx_section.stream)['word0']
                        opcode.append((r >> 24) & 0xFF)
                        opcode.append((r >> 16) & 0xFF)
                        opcode.append((r >> 8) & 0xFF)
                        opcode.append((r >> 0) & 0xFF)
                    return EHABIEntry(function_offset, per_index, opcode, eh_table_offset=eh_table_offset)
                else:
                    return CorruptEHABIEntry('Unknown ARM compact model %d at table entry: %x' % (per_index, n))
        else:
            # highest bit is one, compact model must be 0
            if word1 & 0x7f000000 != 0:
                return CorruptEHABIEntry('Corrupt ARM compact model table entry: %x' % n)
            opcode = [(word1 & 0xFF0000) >> 16, (word1 & 0xFF00) >> 8, word1 & 0xFF]
            return EHABIEntry(function_offset, 0, opcode)


class EHABIEntry(object):
    """ Exception handler abi entry.

        Accessible attributes:

            function_offset:
                Integer.
                None if corrupt. (Reference: CorruptEHABIEntry)

            personality:
                Integer.
                None if corrupt or unwindable. (Reference: CorruptEHABIEntry, CannotUnwindEHABIEntry)
                0/1/2 for ARM personality compact format.
                Others for generic personality.

            bytecode_array:
                Integer array.
                None if corrupt or unwindable or generic personality.
                (Reference: CorruptEHABIEntry, CannotUnwindEHABIEntry, GenericEHABIEntry)

            eh_table_offset:
                Integer.
                Only entries who point to .ARM.extab contains this field, otherwise return None.

            unwindable:
                bool. Whether this function is unwindable.

            corrupt:
                bool. Whether this entry is corrupt.

    """

    def __init__(self,
                 function_offset,
                 personality,
                 bytecode_array,
                 eh_table_offset=None,
                 unwindable=True,
                 corrupt=False):
        self.function_offset = function_offset
        self.personality = personality
        self.bytecode_array = bytecode_array
        self.eh_table_offset = eh_table_offset
        self.unwindable = unwindable
        self.corrupt = corrupt

    def mnmemonic_array(self):
        if self.bytecode_array:
            return EHABIBytecodeDecoder(self.bytecode_array).mnemonic_array
        else:
            return None

    def __repr__(self):
        return "<EHABIEntry function_offset=0x%x, personality=%d, %sbytecode=%s>" % (
            self.function_offset,
            self.personality,
            "eh_table_offset=0x%x, " % self.eh_table_offset if self.eh_table_offset else "",
            self.bytecode_array)


class CorruptEHABIEntry(EHABIEntry):
    """ This entry is corrupt. Attribute #corrupt will be True.
    """

    def __init__(self, reason):
        super(CorruptEHABIEntry, self).__init__(function_offset=None, personality=None, bytecode_array=None,
                                                corrupt=True)
        self.reason = reason

    def __repr__(self):
        return "<CorruptEHABIEntry reason=%s>" % self.reason


class CannotUnwindEHABIEntry(EHABIEntry):
    """ This function cannot be unwind. Attribute #unwindable will be False.
    """

    def __init__(self, function_offset):
        super(CannotUnwindEHABIEntry, self).__init__(function_offset, personality=None, bytecode_array=None,
                                                     unwindable=False)

    def __repr__(self):
        return "<CannotUnwindEHABIEntry function_offset=0x%x>" % self.function_offset


class GenericEHABIEntry(EHABIEntry):
    """ This entry is generic model rather than ARM compact model.Attribute #bytecode_array will be None.
    """

    def __init__(self, function_offset, personality):
        super(GenericEHABIEntry, self).__init__(function_offset, personality, bytecode_array=None)

    def __repr__(self):
        return "<GenericEHABIEntry function_offset=0x%x, personality=0x%x>" % (self.function_offset, self.personality)


def arm_expand_prel31(address, place):
    """
       address: uint32
       place: uint32
       return: uint64
    """
    location = address & 0x7fffffff
    if location & 0x04000000:
        location |= 0xffffffff80000000
    return location + place & 0xffffffffffffffff
