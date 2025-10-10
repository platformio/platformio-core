"""
    ####                                                               ####
   ##     ####  ##  ##  #### ###### #####  ##  ##  #### ######        ##  ##
   ##    ##  ## ### ## ##      ##   ##  ## ##  ## ##      ##    ####      ##
   ##    ##  ## ######  ###    ##   #####  ##  ## ##      ##            ##
   ##    ##  ## ## ###    ##   ##   ##  ## ##  ## ##      ##          ##
    ####  ####  ##  ## ####    ##   ##  ##  #####  ####   ##          ######

                 Parsing made even more fun (and faster too)

Homepage:
    http://construct.wikispaces.com (including online tutorial)

Typical usage:
    >>> from construct import *

Hands-on example:
    >>> from construct import *
    >>> s = Struct("foo",
    ...     UBInt8("a"),
    ...     UBInt16("b"),
    ... )
    >>> s.parse("\\x01\\x02\\x03")
    Container(a = 1, b = 515)
    >>> print s.parse("\\x01\\x02\\x03")
    Container:
        a = 1
        b = 515
    >>> s.build(Container(a = 1, b = 0x0203))
    "\\x01\\x02\\x03"
"""

from .core import *
from .adapters import *
from .macros import *
from .debug import Probe, Debugger


#===============================================================================
# Metadata
#===============================================================================
__author__ = "tomer filiba (tomerfiliba [at] gmail.com)"
__maintainer__ = "Corbin Simpson <MostAwesomeDude@gmail.com>"
__version__ = "2.06"

#===============================================================================
# Shorthand expressions
#===============================================================================
Bits = BitField
Byte = UBInt8
Bytes = Field
Const = ConstAdapter
Tunnel = TunnelAdapter
Embed = Embedded

#===============================================================================
# Deprecated names
# Next scheduled name cleanout: 2.1
#===============================================================================
import functools, warnings

def deprecated(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        warnings.warn(
            "This name is deprecated, use %s instead" % f.__name__,
            DeprecationWarning, stacklevel=2)
        return f(*args, **kwargs)
    return wrapper

MetaBytes = deprecated(MetaField)
GreedyRepeater = deprecated(GreedyRange)
OptionalGreedyRepeater = deprecated(OptionalGreedyRange)
Repeater = deprecated(Range)
StrictRepeater = deprecated(Array)
MetaRepeater = deprecated(Array)
OneOfValidator = deprecated(OneOf)
NoneOfValidator = deprecated(NoneOf)

#===============================================================================
# exposed names
#===============================================================================
__all__ = [
    'AdaptationError', 'Adapter', 'Alias', 'Aligned', 'AlignedStruct',
    'Anchor', 'Array', 'ArrayError', 'BFloat32', 'BFloat64', 'Bit', 'BitField',
    'BitIntegerAdapter', 'BitIntegerError', 'BitStruct', 'Bits', 'Bitwise',
    'Buffered', 'Byte', 'Bytes', 'CString', 'CStringAdapter', 'Const',
    'ConstAdapter', 'ConstError', 'Construct', 'ConstructError', 'Container',
    'Debugger', 'Embed', 'Embedded', 'EmbeddedBitStruct', 'Enum', 'ExprAdapter',
    'Field', 'FieldError', 'Flag', 'FlagsAdapter', 'FlagsContainer',
    'FlagsEnum', 'FormatField', 'GreedyRange', 'GreedyRepeater',
    'HexDumpAdapter', 'If', 'IfThenElse', 'IndexingAdapter', 'LFloat32',
    'LFloat64', 'LazyBound', 'LengthValueAdapter', 'ListContainer',
    'MappingAdapter', 'MappingError', 'MetaArray', 'MetaBytes', 'MetaField',
    'MetaRepeater', 'NFloat32', 'NFloat64', 'Nibble', 'NoneOf',
    'NoneOfValidator', 'Octet', 'OnDemand', 'OnDemandPointer', 'OneOf',
    'OneOfValidator', 'OpenRange', 'Optional', 'OptionalGreedyRange',
    'OptionalGreedyRepeater', 'PaddedStringAdapter', 'Padding',
    'PaddingAdapter', 'PaddingError', 'PascalString', 'Pass', 'Peek',
    'Pointer', 'PrefixedArray', 'Probe', 'Range', 'RangeError', 'Reconfig',
    'Rename', 'RepeatUntil', 'Repeater', 'Restream', 'SBInt16', 'SBInt32',
    'SBInt64', 'SBInt8', 'SLInt16', 'SLInt32', 'SLInt64', 'SLInt8', 'SNInt16',
    'SNInt32', 'SNInt64', 'SNInt8', 'Select', 'SelectError', 'Sequence',
    'SizeofError', 'SlicingAdapter', 'StaticField', 'StrictRepeater', 'String',
    'StringAdapter', 'Struct', 'Subconstruct', 'Switch', 'SwitchError',
    'SymmetricMapping', 'Terminator', 'TerminatorError', 'Tunnel',
    'TunnelAdapter', 'UBInt16', 'UBInt32', 'UBInt64', 'UBInt8', 'ULInt16',
    'ULInt32', 'ULInt64', 'ULInt8', 'UNInt16', 'UNInt32', 'UNInt64', 'UNInt8',
    'Union', 'ValidationError', 'Validator', 'Value', "Magic",
]
