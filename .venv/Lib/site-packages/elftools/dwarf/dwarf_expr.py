#-------------------------------------------------------------------------------
# elftools: dwarf/dwarf_expr.py
#
# Decoding DWARF expressions
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from collections import namedtuple
from io import BytesIO

from ..common.utils import struct_parse, bytelist2string, read_blob
from ..common.exceptions import DWARFError


# DWARF expression opcodes. name -> opcode mapping
DW_OP_name2opcode = dict(
    DW_OP_addr=0x03,
    DW_OP_deref=0x06,
    DW_OP_const1u=0x08,
    DW_OP_const1s=0x09,
    DW_OP_const2u=0x0a,
    DW_OP_const2s=0x0b,
    DW_OP_const4u=0x0c,
    DW_OP_const4s=0x0d,
    DW_OP_const8u=0x0e,
    DW_OP_const8s=0x0f,
    DW_OP_constu=0x10,
    DW_OP_consts=0x11,
    DW_OP_dup=0x12,
    DW_OP_drop=0x13,
    DW_OP_over=0x14,
    DW_OP_pick=0x15,
    DW_OP_swap=0x16,
    DW_OP_rot=0x17,
    DW_OP_xderef=0x18,
    DW_OP_abs=0x19,
    DW_OP_and=0x1a,
    DW_OP_div=0x1b,
    DW_OP_minus=0x1c,
    DW_OP_mod=0x1d,
    DW_OP_mul=0x1e,
    DW_OP_neg=0x1f,
    DW_OP_not=0x20,
    DW_OP_or=0x21,
    DW_OP_plus=0x22,
    DW_OP_plus_uconst=0x23,
    DW_OP_shl=0x24,
    DW_OP_shr=0x25,
    DW_OP_shra=0x26,
    DW_OP_xor=0x27,
    DW_OP_bra=0x28,
    DW_OP_eq=0x29,
    DW_OP_ge=0x2a,
    DW_OP_gt=0x2b,
    DW_OP_le=0x2c,
    DW_OP_lt=0x2d,
    DW_OP_ne=0x2e,
    DW_OP_skip=0x2f,
    DW_OP_regx=0x90,
    DW_OP_fbreg=0x91,
    DW_OP_bregx=0x92,
    DW_OP_piece=0x93,
    DW_OP_deref_size=0x94,
    DW_OP_xderef_size=0x95,
    DW_OP_nop=0x96,
    DW_OP_push_object_address=0x97,
    DW_OP_call2=0x98,
    DW_OP_call4=0x99,
    DW_OP_call_ref=0x9a,
    DW_OP_form_tls_address=0x9b,
    DW_OP_call_frame_cfa=0x9c,
    DW_OP_bit_piece=0x9d,
    DW_OP_implicit_value=0x9e,
    DW_OP_stack_value=0x9f,
    DW_OP_implicit_pointer=0xa0,
    DW_OP_addrx=0xa1,
    DW_OP_constx=0xa2,
    DW_OP_entry_value=0xa3,
    DW_OP_const_type=0xa4,
    DW_OP_regval_type=0xa5,
    DW_OP_deref_type=0xa6,
    DW_OP_xderef_type=0xa7,
    DW_OP_convert=0xa8,
    DW_OP_reinterpret=0xa9,
    DW_OP_lo_user=0xe0,
    DW_OP_GNU_push_tls_address=0xe0,
    DW_OP_WASM_location=0xed,
    DW_OP_GNU_uninit=0xf0,
    DW_OP_GNU_implicit_pointer=0xf2,
    DW_OP_GNU_entry_value=0xf3,
    DW_OP_GNU_const_type=0xf4,
    DW_OP_GNU_regval_type=0xf5,
    DW_OP_GNU_deref_type=0xf6,
    DW_OP_GNU_convert=0xf7,
    DW_OP_GNU_parameter_ref=0xfa,
    DW_OP_hi_user=0xff,
)

def _generate_dynamic_values(map, prefix, index_start, index_end, value_start):
    """ Generate values in a map (dict) dynamically. Each key starts with
        a (string) prefix, followed by an index in the inclusive range
        [index_start, index_end]. The values start at value_start.
    """
    for index in range(index_start, index_end + 1):
        name = '%s%s' % (prefix, index)
        value = value_start + index - index_start
        map[name] = value

_generate_dynamic_values(DW_OP_name2opcode, 'DW_OP_lit', 0, 31, 0x30)
_generate_dynamic_values(DW_OP_name2opcode, 'DW_OP_reg', 0, 31, 0x50)
_generate_dynamic_values(DW_OP_name2opcode, 'DW_OP_breg', 0, 31, 0x70)

# opcode -> name mapping
DW_OP_opcode2name = dict((v, k) for k, v in DW_OP_name2opcode.items())


# Each parsed DWARF expression is returned as this type with its numeric opcode,
# op name (as a string) and a list of arguments.
DWARFExprOp = namedtuple('DWARFExprOp', 'op op_name args offset')


class DWARFExprParser(object):
    """DWARF expression parser.

    When initialized, requires structs to cache a dispatch table. After that,
    parse_expr can be called repeatedly - it's stateless.
    """

    def __init__(self, structs):
        self._dispatch_table = _init_dispatch_table(structs)

    def parse_expr(self, expr):
        """ Parses expr (a list of integers) into a list of DWARFExprOp.

        The list can potentially be nested.
        """
        stream = BytesIO(bytelist2string(expr))
        parsed = []

        while True:
            # Get the next opcode from the stream. If nothing is left in the
            # stream, we're done.
            offset = stream.tell()
            byte = stream.read(1)
            if len(byte) == 0:
                break

            # Decode the opcode and its name.
            op = ord(byte)
            op_name = DW_OP_opcode2name.get(op, 'OP:0x%x' % op)

            # Use dispatch table to parse args.
            arg_parser = self._dispatch_table[op]
            args = arg_parser(stream)

            parsed.append(DWARFExprOp(op=op, op_name=op_name, args=args, offset=offset))

        return parsed


def _init_dispatch_table(structs):
    """Creates a dispatch table for parsing args of an op.

    Returns a dict mapping opcode to a function. The function accepts a stream
    and return a list of parsed arguments for the opcode from the stream;
    the stream is advanced by the function as needed.
    """
    table = {}
    def add(opcode_name, func):
        table[DW_OP_name2opcode[opcode_name]] = func

    def parse_noargs():
        return lambda stream: []

    def parse_op_addr():
        return lambda stream: [struct_parse(structs.the_Dwarf_target_addr,
                                            stream)]

    def parse_arg_struct(arg_struct):
        return lambda stream: [struct_parse(arg_struct, stream)]

    def parse_arg_struct2(arg1_struct, arg2_struct):
        return lambda stream: [struct_parse(arg1_struct, stream),
                               struct_parse(arg2_struct, stream)]

    # ULEB128, then an expression of that length
    def parse_nestedexpr():
        def parse(stream):
            size = struct_parse(structs.the_Dwarf_uleb128, stream)
            nested_expr_blob = read_blob(stream, size)
            return [DWARFExprParser(structs).parse_expr(nested_expr_blob)]
        return parse

    # ULEB128, then a blob of that size
    def parse_blob():
        return lambda stream: [read_blob(stream, struct_parse(structs.the_Dwarf_uleb128, stream))]

    # ULEB128 with datatype DIE offset, then byte, then a blob of that size
    def parse_typedblob():
        return lambda stream: [struct_parse(structs.the_Dwarf_uleb128, stream), read_blob(stream, struct_parse(structs.the_Dwarf_uint8, stream))]
    
    # https://yurydelendik.github.io/webassembly-dwarf/
    # Byte, then variant: 0, 1, 2 => uleb128, 3 => uint32
    def parse_wasmloc():
        def parse(stream):
            op = struct_parse(structs.the_Dwarf_uint8, stream)
            if 0 <= op <= 2:
                return [op, struct_parse(structs.the_Dwarf_uleb128, stream)]
            elif op == 3:
                return [op, struct_parse(structs.the_Dwarf_uint32, stream)]
            else:
                raise DWARFError("Unknown operation code in DW_OP_WASM_location: %d" % (op,))
        return parse

    add('DW_OP_addr', parse_op_addr())
    add('DW_OP_addrx', parse_arg_struct(structs.the_Dwarf_uleb128))
    add('DW_OP_const1u', parse_arg_struct(structs.the_Dwarf_uint8))
    add('DW_OP_const1s', parse_arg_struct(structs.Dwarf_int8('')))
    add('DW_OP_const2u', parse_arg_struct(structs.the_Dwarf_uint16))
    add('DW_OP_const2s', parse_arg_struct(structs.Dwarf_int16('')))
    add('DW_OP_const4u', parse_arg_struct(structs.the_Dwarf_uint32))
    add('DW_OP_const4s', parse_arg_struct(structs.Dwarf_int32('')))
    add('DW_OP_const8u', parse_arg_struct(structs.Dwarf_uint64('')))
    add('DW_OP_const8s', parse_arg_struct(structs.Dwarf_int64('')))
    add('DW_OP_constu', parse_arg_struct(structs.the_Dwarf_uleb128))
    add('DW_OP_consts', parse_arg_struct(structs.the_Dwarf_sleb128))
    add('DW_OP_pick', parse_arg_struct(structs.the_Dwarf_uint8))
    add('DW_OP_plus_uconst', parse_arg_struct(structs.the_Dwarf_uleb128))
    add('DW_OP_bra', parse_arg_struct(structs.Dwarf_int16('')))
    add('DW_OP_skip', parse_arg_struct(structs.Dwarf_int16('')))

    for opname in [ 'DW_OP_deref', 'DW_OP_dup', 'DW_OP_drop', 'DW_OP_over',
                    'DW_OP_swap', 'DW_OP_swap', 'DW_OP_rot', 'DW_OP_xderef',
                    'DW_OP_abs', 'DW_OP_and', 'DW_OP_div', 'DW_OP_minus',
                    'DW_OP_mod', 'DW_OP_mul', 'DW_OP_neg', 'DW_OP_not',
                    'DW_OP_or', 'DW_OP_plus', 'DW_OP_shl', 'DW_OP_shr',
                    'DW_OP_shra', 'DW_OP_xor', 'DW_OP_eq', 'DW_OP_ge',
                    'DW_OP_gt', 'DW_OP_le', 'DW_OP_lt', 'DW_OP_ne', 'DW_OP_nop',
                    'DW_OP_push_object_address', 'DW_OP_form_tls_address',
                    'DW_OP_call_frame_cfa', 'DW_OP_stack_value',
                    'DW_OP_GNU_push_tls_address', 'DW_OP_GNU_uninit']:
        add(opname, parse_noargs())

    for n in range(0, 32):
        add('DW_OP_lit%s' % n, parse_noargs())
        add('DW_OP_reg%s' % n, parse_noargs())
        add('DW_OP_breg%s' % n, parse_arg_struct(structs.the_Dwarf_sleb128))

    add('DW_OP_fbreg', parse_arg_struct(structs.the_Dwarf_sleb128))
    add('DW_OP_regx', parse_arg_struct(structs.the_Dwarf_uleb128))
    add('DW_OP_bregx', parse_arg_struct2(structs.the_Dwarf_uleb128,
                                         structs.the_Dwarf_sleb128))
    add('DW_OP_piece', parse_arg_struct(structs.the_Dwarf_uleb128))
    add('DW_OP_bit_piece', parse_arg_struct2(structs.the_Dwarf_uleb128,
                                             structs.the_Dwarf_uleb128))
    add('DW_OP_deref_size', parse_arg_struct(structs.Dwarf_int8('')))
    add('DW_OP_xderef_size', parse_arg_struct(structs.Dwarf_int8('')))
    add('DW_OP_call2', parse_arg_struct(structs.the_Dwarf_uint16))
    add('DW_OP_call4', parse_arg_struct(structs.the_Dwarf_uint32))
    add('DW_OP_call_ref', parse_arg_struct(structs.the_Dwarf_offset))
    add('DW_OP_implicit_value', parse_blob())
    add('DW_OP_entry_value', parse_nestedexpr())
    add('DW_OP_const_type', parse_typedblob())
    add('DW_OP_regval_type', parse_arg_struct2(structs.the_Dwarf_uleb128,
                                                   structs.the_Dwarf_uleb128))
    add('DW_OP_deref_type', parse_arg_struct2(structs.the_Dwarf_uint8,
                                              structs.the_Dwarf_uleb128))
    add('DW_OP_implicit_pointer', parse_arg_struct2(structs.the_Dwarf_offset,
                                                        structs.the_Dwarf_sleb128))
    add('DW_OP_convert', parse_arg_struct(structs.the_Dwarf_uleb128))
    add('DW_OP_GNU_entry_value', parse_nestedexpr())
    add('DW_OP_GNU_const_type', parse_typedblob())
    add('DW_OP_GNU_regval_type', parse_arg_struct2(structs.the_Dwarf_uleb128,
                                                   structs.the_Dwarf_uleb128))
    add('DW_OP_GNU_deref_type', parse_arg_struct2(structs.the_Dwarf_uint8,
                                                   structs.the_Dwarf_uleb128))
    add('DW_OP_GNU_implicit_pointer', parse_arg_struct2(structs.the_Dwarf_offset,
                                                        structs.the_Dwarf_sleb128))
    add('DW_OP_GNU_parameter_ref', parse_arg_struct(structs.the_Dwarf_offset))
    add('DW_OP_GNU_convert', parse_arg_struct(structs.the_Dwarf_uleb128))
    add('DW_OP_WASM_location', parse_wasmloc())

    return table
