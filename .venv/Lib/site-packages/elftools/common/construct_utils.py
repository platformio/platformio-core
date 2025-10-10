#-------------------------------------------------------------------------------
# elftools: common/construct_utils.py
#
# Some complementary construct utilities
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
from struct import Struct
from ..construct import (
    Subconstruct, ConstructError, ArrayError, Adapter, Field, RepeatUntil,
    Rename, SizeofError, Construct, StaticField, FieldError
    )


class RepeatUntilExcluding(Subconstruct):
    """ A version of construct's RepeatUntil that doesn't include the last
        element (which casued the repeat to exit) in the return value.

        Only parsing is currently implemented.

        P.S. removed some code duplication
    """
    __slots__ = ["predicate"]
    def __init__(self, predicate, subcon):
        Subconstruct.__init__(self, subcon)
        self.predicate = predicate
        self._clear_flag(self.FLAG_COPY_CONTEXT)
        self._set_flag(self.FLAG_DYNAMIC)
    def _parse(self, stream, context):
        obj = []
        try:
            context_for_subcon = context
            if self.subcon.conflags & self.FLAG_COPY_CONTEXT:
                context_for_subcon = context.__copy__()

            while True:
                subobj = self.subcon._parse(stream, context_for_subcon)
                if self.predicate(subobj, context):
                    break
                obj.append(subobj)
        except ConstructError as ex:
            raise ArrayError("missing terminator", ex)
        return obj
    def _build(self, obj, stream, context):
        raise NotImplementedError('no building')
    def _sizeof(self, context):
        raise SizeofError("can't calculate size")

class ULEB128(Construct):
    """A construct based parser for ULEB128 encoding.

       Incompatible with Python 2 - assumes that the return of read()
       is an indexed collection of numbers.
    """
    def _parse(self, stream, context):
        value = 0
        shift = 0
        while True:
            data = stream.read(1)
            if len(data) != 1:
                raise FieldError("unexpected end of stream while parsing a ULEB128 encoded value")
            b = data[0]
            value |= (b & 0x7F) << shift
            shift += 7
            if b & 0x80 == 0:
                return value

class SLEB128(Construct):
    """A construct based parser for SLEB128 encoding.

       Incompatible with Python 2 - assumes that the return of read()
       is an indexed collection of numbers.
    """
    def _parse(self, stream, context):
        value = 0
        shift = 0
        while True:
            data = stream.read(1)
            if len(data) != 1:
                raise FieldError("unexpected end of stream while parsing a SLEB128 encoded value")
            b = data[0]
            value |= (b & 0x7F) << shift
            shift += 7
            if b & 0x80 == 0:
                return value | (~0 << shift) if b & 0x40 else value

class StreamOffset(Construct):
    """
    Captures the current stream offset

    Parameters:
    * name - the name of the value

    Example:
    StreamOffset("item_offset")
    """
    __slots__ = []
    def __init__(self, name):
        Construct.__init__(self, name)
        self._set_flag(self.FLAG_DYNAMIC)
    def _parse(self, stream, context):
        return stream.tell()
    def _build(self, obj, stream, context):
        context[self.name] = stream.tell()
    def _sizeof(self, context):
        return 0

_UBInt24_packer = Struct(">BH")
_ULInt24_packer = Struct("<HB")

class UBInt24(StaticField):
    """unsigned, big endian 24-bit integer"""
    def __init__(self, name):
        StaticField.__init__(self, name, 3)

    def _parse(self, stream, context):
        (h, l) = _UBInt24_packer.unpack(StaticField._parse(self, stream, context))
        return l | (h << 16)
    
    def _build(self, obj, stream, context):
        StaticField._build(self, _UBInt24_packer.pack(obj >> 16, obj & 0xFFFF), stream, context)

class ULInt24(StaticField):
    """unsigned, little endian 24-bit integer"""
    def __init__(self, name):
        StaticField.__init__(self, name, 3)

    def _parse(self, stream, context):
        (l, h) = _ULInt24_packer.unpack(StaticField._parse(self, stream, context))
        return l | (h << 16)
    
    def _build(self, obj, stream, context):
        StaticField._build(self, _ULInt24_packer.pack(obj & 0xFFFF, obj >> 16), stream, context)
