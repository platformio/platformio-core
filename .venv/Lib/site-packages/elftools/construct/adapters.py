from .core import Adapter, AdaptationError, Pass
from .lib import int_to_bin, bin_to_int, swap_bytes
from .lib import FlagsContainer, HexString
from .lib.py3compat import BytesIO, decodebytes


#===============================================================================
# exceptions
#===============================================================================
class BitIntegerError(AdaptationError):
    __slots__ = []
class MappingError(AdaptationError):
    __slots__ = []
class ConstError(AdaptationError):
    __slots__ = []
class ValidationError(AdaptationError):
    __slots__ = []
class PaddingError(AdaptationError):
    __slots__ = []

#===============================================================================
# adapters
#===============================================================================
class BitIntegerAdapter(Adapter):
    """
    Adapter for bit-integers (converts bitstrings to integers, and vice versa).
    See BitField.

    Parameters:
    * subcon - the subcon to adapt
    * width - the size of the subcon, in bits
    * swapped - whether to swap byte order (little endian/big endian).
      default is False (big endian)
    * signed - whether the value is signed (two's complement). the default
      is False (unsigned)
    * bytesize - number of bits per byte, used for byte-swapping (if swapped).
      default is 8.
    """
    __slots__ = ["width", "swapped", "signed", "bytesize"]
    def __init__(self, subcon, width, swapped = False, signed = False,
                 bytesize = 8):
        Adapter.__init__(self, subcon)
        self.width = width
        self.swapped = swapped
        self.signed = signed
        self.bytesize = bytesize
    def _encode(self, obj, context):
        if obj < 0 and not self.signed:
            raise BitIntegerError("object is negative, but field is not signed",
                obj)
        obj2 = int_to_bin(obj, width = self.width)
        if self.swapped:
            obj2 = swap_bytes(obj2, bytesize = self.bytesize)
        return obj2
    def _decode(self, obj, context):
        if self.swapped:
            obj = swap_bytes(obj, bytesize = self.bytesize)
        return bin_to_int(obj, signed = self.signed)

class MappingAdapter(Adapter):
    """
    Adapter that maps objects to other objects.
    See SymmetricMapping and Enum.

    Parameters:
    * subcon - the subcon to map
    * decoding - the decoding (parsing) mapping (a dict)
    * encoding - the encoding (building) mapping (a dict)
    * decdefault - the default return value when the object is not found
      in the decoding mapping. if no object is given, an exception is raised.
      if `Pass` is used, the unmapped object will be passed as-is
    * encdefault - the default return value when the object is not found
      in the encoding mapping. if no object is given, an exception is raised.
      if `Pass` is used, the unmapped object will be passed as-is
    """
    __slots__ = ["encoding", "decoding", "encdefault", "decdefault"]
    def __init__(self, subcon, decoding, encoding,
                 decdefault = NotImplemented, encdefault = NotImplemented):
        Adapter.__init__(self, subcon)
        self.decoding = decoding
        self.encoding = encoding
        self.decdefault = decdefault
        self.encdefault = encdefault
    def _encode(self, obj, context):
        try:
            return self.encoding[obj]
        except (KeyError, TypeError):
            if self.encdefault is NotImplemented:
                raise MappingError("no encoding mapping for %r [%s]" % (
                    obj, self.subcon.name))
            if self.encdefault is Pass:
                return obj
            return self.encdefault
    def _decode(self, obj, context):
        try:
            return self.decoding[obj]
        except (KeyError, TypeError):
            if self.decdefault is NotImplemented:
                raise MappingError("no decoding mapping for %r [%s]" % (
                    obj, self.subcon.name))
            if self.decdefault is Pass:
                return obj
            return self.decdefault

class FlagsAdapter(Adapter):
    """
    Adapter for flag fields. Each flag is extracted from the number, resulting
    in a FlagsContainer object. Not intended for direct usage.
    See FlagsEnum.

    Parameters
    * subcon - the subcon to extract
    * flags - a dictionary mapping flag-names to their value
    """
    __slots__ = ["flags"]
    def __init__(self, subcon, flags):
        Adapter.__init__(self, subcon)
        self.flags = flags
    def _encode(self, obj, context):
        flags = 0
        for name, value in self.flags.items():
            if getattr(obj, name, False):
                flags |= value
        return flags
    def _decode(self, obj, context):
        obj2 = FlagsContainer()
        for name, value in self.flags.items():
            setattr(obj2, name, bool(obj & value))
        return obj2

class StringAdapter(Adapter):
    """
    Adapter for strings. Converts a sequence of characters into a python
    string, and optionally handles character encoding.
    See String.

    Parameters:
    * subcon - the subcon to convert
    * encoding - the character encoding name (e.g., "utf8"), or None to
      return raw bytes (usually 8-bit ASCII).
    """
    __slots__ = ["encoding"]
    def __init__(self, subcon, encoding = None):
        Adapter.__init__(self, subcon)
        self.encoding = encoding
    def _encode(self, obj, context):
        if self.encoding:
            obj = obj.encode(self.encoding)
        return obj
    def _decode(self, obj, context):
        if self.encoding:
            obj = obj.decode(self.encoding)
        return obj

class PaddedStringAdapter(Adapter):
    r"""
    Adapter for padded strings.
    See String.

    Parameters:
    * subcon - the subcon to adapt
    * padchar - the padding character. default is b"\x00".
    * paddir - the direction where padding is placed ("right", "left", or
      "center"). the default is "right".
    * trimdir - the direction where trimming will take place ("right" or
      "left"). the default is "right". trimming is only meaningful for
      building, when the given string is too long.
    """
    __slots__ = ["padchar", "paddir", "trimdir"]
    def __init__(self, subcon, padchar = b"\x00", paddir = "right",
                 trimdir = "right"):
        if paddir not in ("right", "left", "center"):
            raise ValueError("paddir must be 'right', 'left' or 'center'",
                paddir)
        if trimdir not in ("right", "left"):
            raise ValueError("trimdir must be 'right' or 'left'", trimdir)
        Adapter.__init__(self, subcon)
        self.padchar = padchar
        self.paddir = paddir
        self.trimdir = trimdir
    def _decode(self, obj, context):
        if self.paddir == "right":
            obj = obj.rstrip(self.padchar)
        elif self.paddir == "left":
            obj = obj.lstrip(self.padchar)
        else:
            obj = obj.strip(self.padchar)
        return obj
    def _encode(self, obj, context):
        size = self._sizeof(context)
        if self.paddir == "right":
            obj = obj.ljust(size, self.padchar)
        elif self.paddir == "left":
            obj = obj.rjust(size, self.padchar)
        else:
            obj = obj.center(size, self.padchar)
        if len(obj) > size:
            if self.trimdir == "right":
                obj = obj[:size]
            else:
                obj = obj[-size:]
        return obj

class LengthValueAdapter(Adapter):
    """
    Adapter for length-value pairs. It extracts only the value from the
    pair, and calculates the length based on the value.
    See PrefixedArray and PascalString.

    Parameters:
    * subcon - the subcon returning a length-value pair
    """
    __slots__ = []
    def _encode(self, obj, context):
        return (len(obj), obj)
    def _decode(self, obj, context):
        return obj[1]

class CStringAdapter(StringAdapter):
    r"""
    Adapter for C-style strings (strings terminated by a terminator char).

    Parameters:
    * subcon - the subcon to convert
    * terminators - a sequence of terminator chars. default is b"\x00".
    * encoding - the character encoding to use (e.g., "utf8"), or None to
      return raw-bytes. the terminator characters are not affected by the
      encoding.
    """
    __slots__ = ["terminators"]
    def __init__(self, subcon, terminators = b"\x00", encoding = None):
        StringAdapter.__init__(self, subcon, encoding = encoding)
        self.terminators = terminators
    def _encode(self, obj, context):
        return StringAdapter._encode(self, obj, context) + self.terminators[0:1]
    def _decode(self, obj, context):
        return StringAdapter._decode(self, b''.join(obj[:-1]), context)

class TunnelAdapter(Adapter):
    """
    Adapter for tunneling (as in protocol tunneling). A tunnel is construct
    nested upon another (layering). For parsing, the lower layer first parses
    the data (note: it must return a string!), then the upper layer is called
    to parse that data (bottom-up). For building it works in a top-down manner;
    first the upper layer builds the data, then the lower layer takes it and
    writes it to the stream.

    Parameters:
    * subcon - the lower layer subcon
    * inner_subcon - the upper layer (tunneled/nested) subcon

    Example:
    # a pascal string containing compressed data (zlib encoding), so first
    # the string is read, decompressed, and finally re-parsed as an array
    # of UBInt16
    TunnelAdapter(
        PascalString("data", encoding = "zlib"),
        GreedyRange(UBInt16("elements"))
    )
    """
    __slots__ = ["inner_subcon"]
    def __init__(self, subcon, inner_subcon):
        Adapter.__init__(self, subcon)
        self.inner_subcon = inner_subcon
    def _decode(self, obj, context):
        return self.inner_subcon._parse(BytesIO(obj), context)
    def _encode(self, obj, context):
        stream = BytesIO()
        self.inner_subcon._build(obj, stream, context)
        return stream.getvalue()

class ExprAdapter(Adapter):
    """
    A generic adapter that accepts 'encoder' and 'decoder' as parameters. You
    can use ExprAdapter instead of writing a full-blown class when only a
    simple expression is needed.

    Parameters:
    * subcon - the subcon to adapt
    * encoder - a function that takes (obj, context) and returns an encoded
      version of obj
    * decoder - a function that takes (obj, context) and returns a decoded
      version of obj

    Example:
    ExprAdapter(UBInt8("foo"),
        encoder = lambda obj, ctx: obj / 4,
        decoder = lambda obj, ctx: obj * 4,
    )
    """
    __slots__ = ["_encode", "_decode"]
    def __init__(self, subcon, encoder, decoder):
        Adapter.__init__(self, subcon)
        self._encode = encoder
        self._decode = decoder

class HexDumpAdapter(Adapter):
    """
    Adapter for hex-dumping strings. It returns a HexString, which is a string
    """
    __slots__ = ["linesize"]
    def __init__(self, subcon, linesize = 16):
        Adapter.__init__(self, subcon)
        self.linesize = linesize
    def _encode(self, obj, context):
        return obj
    def _decode(self, obj, context):
        return HexString(obj, linesize = self.linesize)

class ConstAdapter(Adapter):
    """
    Adapter for enforcing a constant value ("magic numbers"). When decoding,
    the return value is checked; when building, the value is substituted in.

    Parameters:
    * subcon - the subcon to validate
    * value - the expected value

    Example:
    Const(Field("signature", 2), "MZ")
    """
    __slots__ = ["value"]
    def __init__(self, subcon, value):
        Adapter.__init__(self, subcon)
        self.value = value
    def _encode(self, obj, context):
        if obj is None or obj == self.value:
            return self.value
        else:
            raise ConstError("expected %r, found %r" % (self.value, obj))
    def _decode(self, obj, context):
        if obj != self.value:
            raise ConstError("expected %r, found %r" % (self.value, obj))
        return obj

class SlicingAdapter(Adapter):
    """
    Adapter for slicing a list (getting a slice from that list)

    Parameters:
    * subcon - the subcon to slice
    * start - start index
    * stop - stop index (or None for up-to-end)
    * step - step (or None for every element)
    """
    __slots__ = ["start", "stop", "step"]
    def __init__(self, subcon, start, stop = None):
        Adapter.__init__(self, subcon)
        self.start = start
        self.stop = stop
    def _encode(self, obj, context):
        if self.start is None:
            return obj
        return [None] * self.start + obj
    def _decode(self, obj, context):
        return obj[self.start:self.stop]

class IndexingAdapter(Adapter):
    """
    Adapter for indexing a list (getting a single item from that list)

    Parameters:
    * subcon - the subcon to index
    * index - the index of the list to get
    """
    __slots__ = ["index"]
    def __init__(self, subcon, index):
        Adapter.__init__(self, subcon)
        if type(index) is not int:
            raise TypeError("index must be an integer", type(index))
        self.index = index
    def _encode(self, obj, context):
        return [None] * self.index + [obj]
    def _decode(self, obj, context):
        return obj[self.index]

class PaddingAdapter(Adapter):
    r"""
    Adapter for padding.

    Parameters:
    * subcon - the subcon to pad
    * pattern - the padding pattern (character as byte). default is b"\x00"
    * strict - whether or not to verify, during parsing, that the given
      padding matches the padding pattern. default is False (unstrict)
    """
    __slots__ = ["pattern", "strict"]
    def __init__(self, subcon, pattern = b"\x00", strict = False):
        Adapter.__init__(self, subcon)
        self.pattern = pattern
        self.strict = strict
    def _encode(self, obj, context):
        return self._sizeof(context) * self.pattern
    def _decode(self, obj, context):
        if self.strict:
            expected = self._sizeof(context) * self.pattern
            if obj != expected:
                raise PaddingError("expected %r, found %r" % (expected, obj))
        return obj


#===============================================================================
# validators
#===============================================================================
class Validator(Adapter):
    """
    Abstract class: validates a condition on the encoded/decoded object.
    Override _validate(obj, context) in deriving classes.

    Parameters:
    * subcon - the subcon to validate
    """
    __slots__ = []
    def _decode(self, obj, context):
        if not self._validate(obj, context):
            raise ValidationError("invalid object", obj)
        return obj
    def _encode(self, obj, context):
        return self._decode(obj, context)
    def _validate(self, obj, context):
        raise NotImplementedError()

class OneOf(Validator):
    """
    Validates that the object is one of the listed values.

    :param ``Construct`` subcon: object to validate
    :param iterable valids: a set of valid values

    >>> OneOf(UBInt8("foo"), [4,5,6,7]).parse("\\x05")
    5
    >>> OneOf(UBInt8("foo"), [4,5,6,7]).parse("\\x08")
    Traceback (most recent call last):
        ...
    construct.core.ValidationError: ('invalid object', 8)
    >>>
    >>> OneOf(UBInt8("foo"), [4,5,6,7]).build(5)
    '\\x05'
    >>> OneOf(UBInt8("foo"), [4,5,6,7]).build(9)
    Traceback (most recent call last):
        ...
    construct.core.ValidationError: ('invalid object', 9)
    """
    __slots__ = ["valids"]
    def __init__(self, subcon, valids):
        Validator.__init__(self, subcon)
        self.valids = valids
    def _validate(self, obj, context):
        return obj in self.valids

class NoneOf(Validator):
    """
    Validates that the object is none of the listed values.

    :param ``Construct`` subcon: object to validate
    :param iterable invalids: a set of invalid values

    >>> NoneOf(UBInt8("foo"), [4,5,6,7]).parse("\\x08")
    8
    >>> NoneOf(UBInt8("foo"), [4,5,6,7]).parse("\\x06")
    Traceback (most recent call last):
        ...
    construct.core.ValidationError: ('invalid object', 6)
    """
    __slots__ = ["invalids"]
    def __init__(self, subcon, invalids):
        Validator.__init__(self, subcon)
        self.invalids = invalids
    def _validate(self, obj, context):
        return obj not in self.invalids
