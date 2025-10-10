# -------------------------------------------------------------------------------
# elftools: ehabi/decoder.py
#
# Decode ARM exception handler bytecode.
#
# LeadroyaL (leadroyal@qq.com)
# This code is in the public domain
# -------------------------------------------------------------------------------
from collections import namedtuple


class EHABIBytecodeDecoder(object):
    """ Decoder of a sequence of ARM exception handler abi bytecode.

        Reference:
        https://github.com/llvm/llvm-project/blob/master/llvm/tools/llvm-readobj/ARMEHABIPrinter.h
        https://developer.arm.com/documentation/ihi0038/b/

        Accessible attributes:

            mnemonic_array:
                MnemonicItem array.

        Parameters:

            bytecode_array:
                Integer array, raw data of bytecode.

    """

    def __init__(self, bytecode_array):
        self._bytecode_array = bytecode_array
        self._index = None
        self.mnemonic_array = None
        self._decode()

    def _decode(self):
        """ Decode bytecode array, put result into mnemonic_array.
        """
        self._index = 0
        self.mnemonic_array = []
        while self._index < len(self._bytecode_array):
            for mask, value, handler in self.ring:
                if (self._bytecode_array[self._index] & mask) == value:
                    start_idx = self._index
                    mnemonic = handler(self)
                    end_idx = self._index
                    self.mnemonic_array.append(
                        MnemonicItem(self._bytecode_array[start_idx: end_idx], mnemonic))
                    break

    def _decode_00xxxxxx(self):
        #   SW.startLine() << format("0x%02X      ; vsp = vsp + %u\n", Opcode,
        #                            ((Opcode & 0x3f) << 2) + 4);
        opcode = self._bytecode_array[self._index]
        self._index += 1
        return 'vsp = vsp + %u' % (((opcode & 0x3f) << 2) + 4)

    def _decode_01xxxxxx(self):
        # SW.startLine() << format("0x%02X      ; vsp = vsp - %u\n", Opcode,
        #                          ((Opcode & 0x3f) << 2) + 4);
        opcode = self._bytecode_array[self._index]
        self._index += 1
        return 'vsp = vsp - %u' % (((opcode & 0x3f) << 2) + 4)

    gpr_register_names = ("r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7",
                          "r8", "r9", "r10", "fp", "ip", "sp", "lr", "pc")

    def _calculate_range(self, start, count):
        return ((1 << (count + 1)) - 1) << start

    def _printGPR(self, gpr_mask):
        hits = [self.gpr_register_names[i] for i in range(32) if gpr_mask & (1 << i) != 0]
        return '{%s}' % ', '.join(hits)

    def _print_registers(self, vfp_mask, prefix):
        hits = [prefix + str(i) for i in range(32) if vfp_mask & (1 << i) != 0]
        return '{%s}' % ', '.join(hits)

    def _decode_1000iiii_iiiiiiii(self):
        op0 = self._bytecode_array[self._index]
        self._index += 1
        op1 = self._bytecode_array[self._index]
        self._index += 1
        #   uint16_t GPRMask = (Opcode1 << 4) | ((Opcode0 & 0x0f) << 12);
        #   SW.startLine()
        #     << format("0x%02X 0x%02X ; %s",
        #               Opcode0, Opcode1, GPRMask ? "pop " : "refuse to unwind");
        #   if (GPRMask)
        #     PrintGPR(GPRMask);
        gpr_mask = (op1 << 4) | ((op0 & 0x0f) << 12)
        if gpr_mask == 0:
            return 'refuse to unwind'
        else:
            return 'pop %s' % self._printGPR(gpr_mask)

    def _decode_10011101(self):
        self._index += 1
        return 'reserved (ARM MOVrr)'

    def _decode_10011111(self):
        self._index += 1
        return 'reserved (WiMMX MOVrr)'

    def _decode_1001nnnn(self):
        # SW.startLine() << format("0x%02X      ; vsp = r%u\n", Opcode, (Opcode & 0x0f));
        opcode = self._bytecode_array[self._index]
        self._index += 1
        return 'vsp = r%u' % (opcode & 0x0f)

    def _decode_10100nnn(self):
        # SW.startLine() << format("0x%02X      ; pop ", Opcode);
        # PrintGPR((((1 << ((Opcode & 0x7) + 1)) - 1) << 4));
        opcode = self._bytecode_array[self._index]
        self._index += 1
        return 'pop %s' % self._printGPR(self._calculate_range(4, opcode & 0x07))

    def _decode_10101nnn(self):
        # SW.startLine() << format("0x%02X      ; pop ", Opcode);
        # PrintGPR((((1 << ((Opcode & 0x7) + 1)) - 1) << 4) | (1 << 14));
        opcode = self._bytecode_array[self._index]
        self._index += 1
        return 'pop %s' % self._printGPR(self._calculate_range(4, opcode & 0x07) | (1 << 14))

    def _decode_10110000(self):
        # SW.startLine() << format("0x%02X      ; finish\n", Opcode);
        self._index += 1
        return 'finish'

    def _decode_10110001_0000iiii(self):
        # SW.startLine()
        #   << format("0x%02X 0x%02X ; %s", Opcode0, Opcode1,
        #             ((Opcode1 & 0xf0) || Opcode1 == 0x00) ? "spare" : "pop ");
        # if (((Opcode1 & 0xf0) == 0x00) && Opcode1)
        #   PrintGPR((Opcode1 & 0x0f));
        self._index += 1  # skip constant byte
        op1 = self._bytecode_array[self._index]
        self._index += 1
        if (op1 & 0xf0) != 0 or op1 == 0x00:
            return 'spare'
        else:
            return 'pop %s' % self._printGPR((op1 & 0x0f))

    def _decode_10110010_uleb128(self):
        #  SmallVector<uint8_t, 4> ULEB;
        #  do { ULEB.push_back(Opcodes[OI ^ 3]); } while (Opcodes[OI++ ^ 3] & 0x80);
        #  uint64_t Value = 0;
        #  for (unsigned BI = 0, BE = ULEB.size(); BI != BE; ++BI)
        #    Value = Value | ((ULEB[BI] & 0x7f) << (7 * BI));
        #  OS << format("; vsp = vsp + %" PRIu64 "\n", 0x204 + (Value << 2));
        self._index += 1   # skip constant byte
        uleb_buffer = [self._bytecode_array[self._index]]
        self._index += 1
        while self._bytecode_array[self._index] & 0x80 == 0:
            uleb_buffer.append(self._bytecode_array[self._index])
            self._index += 1
        value = 0
        for b in reversed(uleb_buffer):
            value = (value << 7) + (b & 0x7F)
        return 'vsp = vsp + %u' % (0x204 + (value << 2))

    def _decode_10110011_sssscccc(self):
        # these two decoders are equal
        return self._decode_11001001_sssscccc()

    def _decode_101101nn(self):
        return self._spare()

    def _decode_10111nnn(self):
        #  SW.startLine() << format("0x%02X      ; pop ", Opcode);
        #  PrintRegisters((((1 << ((Opcode & 0x07) + 1)) - 1) << 8), "d");
        opcode = self._bytecode_array[self._index]
        self._index += 1
        return 'pop %s' % self._print_registers(self._calculate_range(8, opcode & 0x07), "d")

    def _decode_11000110_sssscccc(self):
        #  SW.startLine() << format("0x%02X 0x%02X ; pop ", Opcode0, Opcode1);
        #  uint8_t Start = ((Opcode1 & 0xf0) >> 4);
        #  uint8_t Count = ((Opcode1 & 0x0f) >> 0);
        #  PrintRegisters((((1 << (Count + 1)) - 1) << Start), "wR");
        self._index += 1  # skip constant byte
        op1 = self._bytecode_array[self._index]
        self._index += 1
        start = ((op1 & 0xf0) >> 4)
        count = ((op1 & 0x0f) >> 0)
        return 'pop %s' % self._print_registers(self._calculate_range(start, count), "wR")

    def _decode_11000111_0000iiii(self):
        #   SW.startLine()
        #     << format("0x%02X 0x%02X ; %s", Opcode0, Opcode1,
        #               ((Opcode1 & 0xf0) || Opcode1 == 0x00) ? "spare" : "pop ");
        #   if ((Opcode1 & 0xf0) == 0x00 && Opcode1)
        #       PrintRegisters(Opcode1 & 0x0f, "wCGR");
        self._index += 1  # skip constant byte
        op1 = self._bytecode_array[self._index]
        self._index += 1
        if (op1 & 0xf0) != 0 or op1 == 0x00:
            return 'spare'
        else:
            return 'pop %s' % self._print_registers(op1 & 0x0f, "wCGR")

    def _decode_11001000_sssscccc(self):
        #   SW.startLine() << format("0x%02X 0x%02X ; pop ", Opcode0, Opcode1);
        #   uint8_t Start = 16 + ((Opcode1 & 0xf0) >> 4);
        #   uint8_t Count = ((Opcode1 & 0x0f) >> 0);
        #   PrintRegisters((((1 << (Count + 1)) - 1) << Start), "d");
        self._index += 1  # skip constant byte
        op1 = self._bytecode_array[self._index]
        self._index += 1
        start = 16 + ((op1 & 0xf0) >> 4)
        count = ((op1 & 0x0f) >> 0)
        return 'pop %s' % self._print_registers(self._calculate_range(start, count), "d")

    def _decode_11001001_sssscccc(self):
        #   SW.startLine() << format("0x%02X 0x%02X ; pop ", Opcode0, Opcode1);
        #   uint8_t Start = ((Opcode1 & 0xf0) >> 4);
        #   uint8_t Count = ((Opcode1 & 0x0f) >> 0);
        #   PrintRegisters((((1 << (Count + 1)) - 1) << Start), "d");
        self._index += 1  # skip constant byte
        op1 = self._bytecode_array[self._index]
        self._index += 1
        start = ((op1 & 0xf0) >> 4)
        count = ((op1 & 0x0f) >> 0)
        return 'pop %s' % self._print_registers(self._calculate_range(start, count), "d")

    def _decode_11001yyy(self):
        return self._spare()

    def _decode_11000nnn(self):
        #   SW.startLine() << format("0x%02X      ; pop ", Opcode);
        #   PrintRegisters((((1 << ((Opcode & 0x07) + 1)) - 1) << 10), "wR");
        opcode = self._bytecode_array[self._index]
        self._index += 1
        return 'pop %s' % self._print_registers(self._calculate_range(10, opcode & 0x07), "wR")

    def _decode_11010nnn(self):
        # these two decoders are equal
        return self._decode_10111nnn()

    def _decode_11xxxyyy(self):
        return self._spare()

    def _spare(self):
        self._index += 1
        return 'spare'

    _DECODE_RECIPE_TYPE = namedtuple('_DECODE_RECIPE_TYPE', 'mask value handler')

    ring = (
        _DECODE_RECIPE_TYPE(mask=0xc0, value=0x00, handler=_decode_00xxxxxx),
        _DECODE_RECIPE_TYPE(mask=0xc0, value=0x40, handler=_decode_01xxxxxx),
        _DECODE_RECIPE_TYPE(mask=0xf0, value=0x80, handler=_decode_1000iiii_iiiiiiii),
        _DECODE_RECIPE_TYPE(mask=0xff, value=0x9d, handler=_decode_10011101),
        _DECODE_RECIPE_TYPE(mask=0xff, value=0x9f, handler=_decode_10011111),
        _DECODE_RECIPE_TYPE(mask=0xf0, value=0x90, handler=_decode_1001nnnn),
        _DECODE_RECIPE_TYPE(mask=0xf8, value=0xa0, handler=_decode_10100nnn),
        _DECODE_RECIPE_TYPE(mask=0xf8, value=0xa8, handler=_decode_10101nnn),
        _DECODE_RECIPE_TYPE(mask=0xff, value=0xb0, handler=_decode_10110000),
        _DECODE_RECIPE_TYPE(mask=0xff, value=0xb1, handler=_decode_10110001_0000iiii),
        _DECODE_RECIPE_TYPE(mask=0xff, value=0xb2, handler=_decode_10110010_uleb128),
        _DECODE_RECIPE_TYPE(mask=0xff, value=0xb3, handler=_decode_10110011_sssscccc),
        _DECODE_RECIPE_TYPE(mask=0xfc, value=0xb4, handler=_decode_101101nn),
        _DECODE_RECIPE_TYPE(mask=0xf8, value=0xb8, handler=_decode_10111nnn),
        _DECODE_RECIPE_TYPE(mask=0xff, value=0xc6, handler=_decode_11000110_sssscccc),
        _DECODE_RECIPE_TYPE(mask=0xff, value=0xc7, handler=_decode_11000111_0000iiii),
        _DECODE_RECIPE_TYPE(mask=0xff, value=0xc8, handler=_decode_11001000_sssscccc),
        _DECODE_RECIPE_TYPE(mask=0xff, value=0xc9, handler=_decode_11001001_sssscccc),
        _DECODE_RECIPE_TYPE(mask=0xc8, value=0xc8, handler=_decode_11001yyy),
        _DECODE_RECIPE_TYPE(mask=0xf8, value=0xc0, handler=_decode_11000nnn),
        _DECODE_RECIPE_TYPE(mask=0xf8, value=0xd0, handler=_decode_11010nnn),
        _DECODE_RECIPE_TYPE(mask=0xc0, value=0xc0, handler=_decode_11xxxyyy),
    )


class MnemonicItem(object):
    """ Single mnemonic item.
    """

    def __init__(self, bytecode, mnemonic):
        self.bytecode = bytecode
        self.mnemonic = mnemonic

    def __repr__(self):
        return '%s ; %s' % (' '.join(['0x%02x' % x for x in self.bytecode]), self.mnemonic)
