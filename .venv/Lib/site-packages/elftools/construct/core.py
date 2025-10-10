from struct import Struct as Packer

from .lib.py3compat import BytesIO, advance_iterator, bchr
from .lib import Container, ListContainer, LazyContainer


#===============================================================================
# exceptions
#===============================================================================
class ConstructError(Exception):
    __slots__ = []
class FieldError(ConstructError):
    __slots__ = []
class SizeofError(ConstructError):
    __slots__ = []
class AdaptationError(ConstructError):
    __slots__ = []
class ArrayError(ConstructError):
    __slots__ = []
class RangeError(ConstructError):
    __slots__ = []
class SwitchError(ConstructError):
    __slots__ = []
class SelectError(ConstructError):
    __slots__ = []
class TerminatorError(ConstructError):
    __slots__ = []

#===============================================================================
# abstract constructs
#===============================================================================
class Construct(object):
    """
    The mother of all constructs.

    This object is generally not directly instantiated, and it does not
    directly implement parsing and building, so it is largely only of interest
    to subclass implementors.

    The external user API:

     * parse()
     * parse_stream()
     * build()
     * build_stream()
     * sizeof()

    Subclass authors should not override the external methods. Instead,
    another API is available:

     * _parse()
     * _build()
     * _sizeof()

    There is also a flag API:

     * _set_flag()
     * _clear_flag()
     * _inherit_flags()
     * _is_flag()

    And stateful copying:

     * __getstate__()
     * __setstate__()

    Attributes and Inheritance
    ==========================

    All constructs have a name and flags. The name is used for naming struct
    members and context dictionaries. Note that the name can either be a
    string, or None if the name is not needed. A single underscore ("_") is a
    reserved name, and so are names starting with a less-than character ("<").
    The name should be descriptive, short, and valid as a Python identifier,
    although these rules are not enforced.

    The flags specify additional behavioral information about this construct.
    Flags are used by enclosing constructs to determine a proper course of
    action. Flags are inherited by default, from inner subconstructs to outer
    constructs. The enclosing construct may set new flags or clear existing
    ones, as necessary.

    For example, if FLAG_COPY_CONTEXT is set, repeaters will pass a copy of
    the context for each iteration, which is necessary for OnDemand parsing.
    """

    FLAG_COPY_CONTEXT          = 0x0001
    FLAG_DYNAMIC               = 0x0002
    FLAG_EMBED                 = 0x0004
    FLAG_NESTING               = 0x0008

    __slots__ = ["name", "conflags"]
    def __init__(self, name, flags = 0):
        if name is not None:
            if type(name) is not str:
                raise TypeError("name must be a string or None", name)
            if name == "_" or name.startswith("<"):
                raise ValueError("reserved name", name)
        self.name = name
        self.conflags = flags

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.name)

    def _set_flag(self, flag):
        """
        Set the given flag or flags.

        :param int flag: flag to set; may be OR'd combination of flags
        """

        self.conflags |= flag

    def _clear_flag(self, flag):
        """
        Clear the given flag or flags.

        :param int flag: flag to clear; may be OR'd combination of flags
        """

        self.conflags &= ~flag

    def _inherit_flags(self, *subcons):
        """
        Pull flags from subconstructs.
        """

        for sc in subcons:
            self._set_flag(sc.conflags)

    def _is_flag(self, flag):
        """
        Check whether a given flag is set.

        :param int flag: flag to check
        """

        return bool(self.conflags & flag)

    def __getstate__(self):
        """
        Obtain a dictionary representing this construct's state.
        """

        attrs = {}
        if hasattr(self, "__dict__"):
            attrs.update(self.__dict__)
        slots = []
        c = self.__class__
        while c is not None:
            if hasattr(c, "__slots__"):
                slots.extend(c.__slots__)
            c = c.__base__
        for name in slots:
            if hasattr(self, name):
                attrs[name] = getattr(self, name)
        return attrs

    def __setstate__(self, attrs):
        """
        Set this construct's state to a given state.
        """
        for name, value in attrs.items():
            setattr(self, name, value)

    def __copy__(self):
        """returns a copy of this construct"""
        self2 = object.__new__(self.__class__)
        self2.__setstate__(self.__getstate__())
        return self2

    def parse(self, data):
        """
        Parse an in-memory buffer.

        Strings, buffers, memoryviews, and other complete buffers can be
        parsed with this method.
        """

        return self.parse_stream(BytesIO(data))

    def parse_stream(self, stream):
        """
        Parse a stream.

        Files, pipes, sockets, and other streaming sources of data are handled
        by this method.
        """

        return self._parse(stream, Container())

    def _parse(self, stream, context):
        """
        Override me in your subclass.
        """

        raise NotImplementedError()

    def build(self, obj):
        """
        Build an object in memory.
        """
        stream = BytesIO()
        self.build_stream(obj, stream)
        return stream.getvalue()

    def build_stream(self, obj, stream):
        """
        Build an object directly into a stream.
        """
        self._build(obj, stream, Container())

    def _build(self, obj, stream, context):
        """
        Override me in your subclass.
        """

        raise NotImplementedError()

    def sizeof(self, context=None):
        """
        Calculate the size of this object, optionally using a context.

        Some constructs have no fixed size and can only know their size for a
        given hunk of data; these constructs will raise an error if they are
        not passed a context.

        :param ``Container`` context: contextual data

        :returns: int of the length of this construct
        :raises SizeofError: the size could not be determined
        """

        if context is None:
            context = Container()
        try:
            return self._sizeof(context)
        except Exception as e:
            raise SizeofError(e)

    def _sizeof(self, context):
        """
        Override me in your subclass.
        """

        raise SizeofError("Raw Constructs have no size!")

class Subconstruct(Construct):
    """
    Abstract subconstruct (wraps an inner construct, inheriting its
    name and flags).

    Parameters:
    * subcon - the construct to wrap
    """
    __slots__ = ["subcon"]
    def __init__(self, subcon):
        Construct.__init__(self, subcon.name, subcon.conflags)
        self.subcon = subcon
    def _parse(self, stream, context):
        return self.subcon._parse(stream, context)
    def _build(self, obj, stream, context):
        self.subcon._build(obj, stream, context)
    def _sizeof(self, context):
        return self.subcon._sizeof(context)

class Adapter(Subconstruct):
    """
    Abstract adapter: calls _decode for parsing and _encode for building.

    Parameters:
    * subcon - the construct to wrap
    """
    __slots__ = []
    def _parse(self, stream, context):
        return self._decode(self.subcon._parse(stream, context), context)
    def _build(self, obj, stream, context):
        self.subcon._build(self._encode(obj, context), stream, context)
    def _decode(self, obj, context):
        raise NotImplementedError()
    def _encode(self, obj, context):
        raise NotImplementedError()


#===============================================================================
# Fields
#===============================================================================
def _read_stream(stream, length):
    if length < 0:
        raise ValueError("length must be >= 0", length)
    data = stream.read(length)
    if len(data) != length:
        raise FieldError("expected %d, found %d" % (length, len(data)))
    return data

def _write_stream(stream, length, data):
    if length < 0:
        raise ValueError("length must be >= 0", length)
    if len(data) != length:
        raise FieldError("expected %d, found %d" % (length, len(data)))
    stream.write(data)

class StaticField(Construct):
    """
    A fixed-size byte field.

    :param str name: field name
    :param int length: number of bytes in the field
    """

    __slots__ = ["length"]
    def __init__(self, name, length):
        Construct.__init__(self, name)
        self.length = length
    def _parse(self, stream, context):
        return _read_stream(stream, self.length)
    def _build(self, obj, stream, context):
        _write_stream(stream, self.length, obj)
    def _sizeof(self, context):
        return self.length

class FormatField(StaticField):
    """
    A field that uses ``struct`` to pack and unpack data.

    See ``struct`` documentation for instructions on crafting format strings.

    :param str name: name of the field
    :param str endianness: format endianness string; one of "<", ">", or "="
    :param str format: a single format character
    """

    __slots__ = ["packer"]
    def __init__(self, name, endianity, format):
        if endianity not in (">", "<", "="):
            raise ValueError("endianity must be be '=', '<', or '>'",
                endianity)
        if len(format) != 1:
            raise ValueError("must specify one and only one format char")
        self.packer = Packer(endianity + format)
        StaticField.__init__(self, name, self.packer.size)
    def __getstate__(self):
        attrs = StaticField.__getstate__(self)
        attrs["packer"] = attrs["packer"].format
        return attrs
    def __setstate__(self, attrs):
        attrs["packer"] = Packer(attrs["packer"])
        return StaticField.__setstate__(self, attrs)
    def _parse(self, stream, context):
        try:
            return self.packer.unpack(_read_stream(stream, self.length))[0]
        except Exception as ex:
            raise FieldError(ex)
    def _build(self, obj, stream, context):
        try:
            _write_stream(stream, self.length, self.packer.pack(obj))
        except Exception as ex:
            raise FieldError(ex)

class MetaField(Construct):
    """
    A variable-length field. The length is obtained at runtime from a
    function.

    :param str name: name of the field
    :param callable lengthfunc: callable that takes a context and returns
                                length as an int

    >>> foo = Struct("foo",
    ...     Byte("length"),
    ...     MetaField("data", lambda ctx: ctx["length"])
    ... )
    >>> foo.parse("\\x03ABC")
    Container(data = 'ABC', length = 3)
    >>> foo.parse("\\x04ABCD")
    Container(data = 'ABCD', length = 4)
    """

    __slots__ = ["lengthfunc"]
    def __init__(self, name, lengthfunc):
        Construct.__init__(self, name)
        self.lengthfunc = lengthfunc
        self._set_flag(self.FLAG_DYNAMIC)
    def _parse(self, stream, context):
        return _read_stream(stream, self.lengthfunc(context))
    def _build(self, obj, stream, context):
        _write_stream(stream, self.lengthfunc(context), obj)
    def _sizeof(self, context):
        return self.lengthfunc(context)


#===============================================================================
# arrays and repeaters
#===============================================================================
class MetaArray(Subconstruct):
    """
    An array (repeater) of a meta-count. The array will iterate exactly
    `countfunc()` times. Will raise ArrayError if less elements are found.
    See also Array, Range and RepeatUntil.

    Parameters:
    * countfunc - a function that takes the context as a parameter and returns
      the number of elements of the array (count)
    * subcon - the subcon to repeat `countfunc()` times

    Example:
    MetaArray(lambda ctx: 5, UBInt8("foo"))
    """
    __slots__ = ["countfunc"]
    def __init__(self, countfunc, subcon):
        Subconstruct.__init__(self, subcon)
        self.countfunc = countfunc
        self._clear_flag(self.FLAG_COPY_CONTEXT)
        self._set_flag(self.FLAG_DYNAMIC)
    def _parse(self, stream, context):
        obj = ListContainer()
        c = 0
        count = self.countfunc(context)
        try:
            if self.subcon.conflags & self.FLAG_COPY_CONTEXT:
                while c < count:
                    obj.append(self.subcon._parse(stream, context.__copy__()))
                    c += 1
            else:
                while c < count:
                    obj.append(self.subcon._parse(stream, context))
                    c += 1
        except ConstructError as ex:
            raise ArrayError("expected %d, found %d" % (count, c), ex)
        return obj
    def _build(self, obj, stream, context):
        count = self.countfunc(context)
        if len(obj) != count:
            raise ArrayError("expected %d, found %d" % (count, len(obj)))
        if self.subcon.conflags & self.FLAG_COPY_CONTEXT:
            for subobj in obj:
                self.subcon._build(subobj, stream, context.__copy__())
        else:
            for subobj in obj:
                self.subcon._build(subobj, stream, context)
    def _sizeof(self, context):
        return self.subcon._sizeof(context) * self.countfunc(context)

class Range(Subconstruct):
    """
    A range-array. The subcon will iterate between `mincount` to `maxcount`
    times. If less than `mincount` elements are found, raises RangeError.
    See also GreedyRange and OptionalGreedyRange.

    The general-case repeater. Repeats the given unit for at least mincount
    times, and up to maxcount times. If an exception occurs (EOF, validation
    error), the repeater exits. If less than mincount units have been
    successfully parsed, a RangeError is raised.

    .. note::
       This object requires a seekable stream for parsing.

    :param int mincount: the minimal count
    :param int maxcount: the maximal count
    :param Construct subcon: the subcon to repeat

    >>> c = Range(3, 7, UBInt8("foo"))
    >>> c.parse("\\x01\\x02")
    Traceback (most recent call last):
      ...
    construct.core.RangeError: expected 3..7, found 2
    >>> c.parse("\\x01\\x02\\x03")
    [1, 2, 3]
    >>> c.parse("\\x01\\x02\\x03\\x04\\x05\\x06")
    [1, 2, 3, 4, 5, 6]
    >>> c.parse("\\x01\\x02\\x03\\x04\\x05\\x06\\x07")
    [1, 2, 3, 4, 5, 6, 7]
    >>> c.parse("\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\x09")
    [1, 2, 3, 4, 5, 6, 7]
    >>> c.build([1,2])
    Traceback (most recent call last):
      ...
    construct.core.RangeError: expected 3..7, found 2
    >>> c.build([1,2,3,4])
    '\\x01\\x02\\x03\\x04'
    >>> c.build([1,2,3,4,5,6,7,8])
    Traceback (most recent call last):
      ...
    construct.core.RangeError: expected 3..7, found 8
    """

    __slots__ = ["mincount", "maxcout"]
    def __init__(self, mincount, maxcout, subcon):
        Subconstruct.__init__(self, subcon)
        self.mincount = mincount
        self.maxcout = maxcout
        self._clear_flag(self.FLAG_COPY_CONTEXT)
        self._set_flag(self.FLAG_DYNAMIC)
    def _parse(self, stream, context):
        obj = ListContainer()
        c = 0
        try:
            if self.subcon.conflags & self.FLAG_COPY_CONTEXT:
                while c < self.maxcout:
                    pos = stream.tell()
                    obj.append(self.subcon._parse(stream, context.__copy__()))
                    c += 1
            else:
                while c < self.maxcout:
                    pos = stream.tell()
                    obj.append(self.subcon._parse(stream, context))
                    c += 1
        except ConstructError as ex:
            if c < self.mincount:
                raise RangeError("expected %d to %d, found %d" %
                    (self.mincount, self.maxcout, c), ex)
            stream.seek(pos)
        return obj
    def _build(self, obj, stream, context):
        if len(obj) < self.mincount or len(obj) > self.maxcout:
            raise RangeError("expected %d to %d, found %d" %
                (self.mincount, self.maxcout, len(obj)))
        cnt = 0
        try:
            if self.subcon.conflags & self.FLAG_COPY_CONTEXT:
                for subobj in obj:
                    if isinstance(obj, bytes):
                        subobj = bchr(subobj)
                    self.subcon._build(subobj, stream, context.__copy__())
                    cnt += 1
            else:
                for subobj in obj:
                    if isinstance(obj, bytes):
                        subobj = bchr(subobj)
                    self.subcon._build(subobj, stream, context)
                    cnt += 1
        except ConstructError as ex:
            if cnt < self.mincount:
                raise RangeError("expected %d to %d, found %d" %
                    (self.mincount, self.maxcout, len(obj)), ex)
    def _sizeof(self, context):
        raise SizeofError("can't calculate size")

class RepeatUntil(Subconstruct):
    """
    An array that repeats until the predicate indicates it to stop. Note that
    the last element (which caused the repeat to exit) is included in the
    return value.

    Parameters:
    * predicate - a predicate function that takes (obj, context) and returns
      True if the stop-condition is met, or False to continue.
    * subcon - the subcon to repeat.

    Example:
    # will read chars until b\x00 (inclusive)
    RepeatUntil(lambda obj, ctx: obj == b"\x00",
        Field("chars", 1)
    )
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
            if self.subcon.conflags & self.FLAG_COPY_CONTEXT:
                while True:
                    subobj = self.subcon._parse(stream, context.__copy__())
                    obj.append(subobj)
                    if self.predicate(subobj, context):
                        break
            else:
                while True:
                    subobj = self.subcon._parse(stream, context)
                    obj.append(subobj)
                    if self.predicate(subobj, context):
                        break
        except ConstructError as ex:
            raise ArrayError("missing terminator", ex)
        return obj
    def _build(self, obj, stream, context):
        terminated = False
        if self.subcon.conflags & self.FLAG_COPY_CONTEXT:
            for subobj in obj:
                self.subcon._build(subobj, stream, context.__copy__())
                if self.predicate(subobj, context):
                    terminated = True
                    break
        else:
            for subobj in obj:
                subobj = bchr(subobj)
                self.subcon._build(subobj, stream, context.__copy__())
                if self.predicate(subobj, context):
                    terminated = True
                    break
        if not terminated:
            raise ArrayError("missing terminator")
    def _sizeof(self, context):
        raise SizeofError("can't calculate size")


#===============================================================================
# structures and sequences
#===============================================================================
class Struct(Construct):
    """
    A sequence of named constructs, similar to structs in C. The elements are
    parsed and built in the order they are defined.
    See also Embedded.

    Parameters:
    * name - the name of the structure
    * subcons - a sequence of subconstructs that make up this structure.
    * nested - a keyword-only argument that indicates whether this struct
      creates a nested context. The default is True. This parameter is
      considered "advanced usage", and may be removed in the future.

    Example:
    Struct("foo",
        UBInt8("first_element"),
        UBInt16("second_element"),
        Padding(2),
        UBInt8("third_element"),
    )
    """
    __slots__ = ["subcons", "nested"]
    def __init__(self, name, *subcons, **kw):
        self.nested = kw.pop("nested", True)
        if kw:
            raise TypeError("the only keyword argument accepted is 'nested'", kw)
        Construct.__init__(self, name)
        self.subcons = subcons
        self._inherit_flags(*subcons)
        self._clear_flag(self.FLAG_EMBED)
    def _parse(self, stream, context):
        if "<obj>" in context:
            obj = context["<obj>"]
            del context["<obj>"]
        else:
            obj = Container()
            if self.nested:
                context = Container(_ = context)
        for sc in self.subcons:
            if sc.conflags & self.FLAG_EMBED:
                context["<obj>"] = obj
                sc._parse(stream, context)
            else:
                subobj = sc._parse(stream, context)
                if sc.name is not None:
                    obj[sc.name] = subobj
                    context[sc.name] = subobj
        return obj
    def _build(self, obj, stream, context):
        if "<unnested>" in context:
            del context["<unnested>"]
        elif self.nested:
            context = Container(_ = context)
        for sc in self.subcons:
            if sc.conflags & self.FLAG_EMBED:
                context["<unnested>"] = True
                subobj = obj
            elif sc.name is None:
                subobj = None
            else:
                subobj = getattr(obj, sc.name)
                context[sc.name] = subobj
            sc._build(subobj, stream, context)
    def _sizeof(self, context):
        if self.nested:
            context = Container(_ = context)
        return sum(sc._sizeof(context) for sc in self.subcons)

class Sequence(Struct):
    """
    A sequence of unnamed constructs. The elements are parsed and built in the
    order they are defined.
    See also Embedded.

    Parameters:
    * name - the name of the structure
    * subcons - a sequence of subconstructs that make up this structure.
    * nested - a keyword-only argument that indicates whether this struct
      creates a nested context. The default is True. This parameter is
      considered "advanced usage", and may be removed in the future.

    Example:
    Sequence("foo",
        UBInt8("first_element"),
        UBInt16("second_element"),
        Padding(2),
        UBInt8("third_element"),
    )
    """
    __slots__ = []
    def _parse(self, stream, context):
        if "<obj>" in context:
            obj = context["<obj>"]
            del context["<obj>"]
        else:
            obj = ListContainer()
            if self.nested:
                context = Container(_ = context)
        for sc in self.subcons:
            if sc.conflags & self.FLAG_EMBED:
                context["<obj>"] = obj
                sc._parse(stream, context)
            else:
                subobj = sc._parse(stream, context)
                if sc.name is not None:
                    obj.append(subobj)
                    context[sc.name] = subobj
        return obj
    def _build(self, obj, stream, context):
        if "<unnested>" in context:
            del context["<unnested>"]
        elif self.nested:
            context = Container(_ = context)
        objiter = iter(obj)
        for sc in self.subcons:
            if sc.conflags & self.FLAG_EMBED:
                context["<unnested>"] = True
                subobj = objiter
            elif sc.name is None:
                subobj = None
            else:
                subobj = advance_iterator(objiter)
                context[sc.name] = subobj
            sc._build(subobj, stream, context)

class Union(Construct):
    """
    a set of overlapping fields (like unions in C). when parsing,
    all fields read the same data; when building, only the first subcon
    (called "master") is used.

    Parameters:
    * name - the name of the union
    * master - the master subcon, i.e., the subcon used for building and
      calculating the total size
    * subcons - additional subcons

    Example:
    Union("what_are_four_bytes",
        UBInt32("one_dword"),
        Struct("two_words", UBInt16("first"), UBInt16("second")),
        Struct("four_bytes",
            UBInt8("a"),
            UBInt8("b"),
            UBInt8("c"),
            UBInt8("d")
        ),
    )
    """
    __slots__ = ["parser", "builder"]
    def __init__(self, name, master, *subcons, **kw):
        Construct.__init__(self, name)
        args = [Peek(sc) for sc in subcons]
        args.append(MetaField(None, lambda ctx: master._sizeof(ctx)))
        self.parser = Struct(name, Peek(master, perform_build = True), *args)
        self.builder = Struct(name, master)
    def _parse(self, stream, context):
        return self.parser._parse(stream, context)
    def _build(self, obj, stream, context):
        return self.builder._build(obj, stream, context)
    def _sizeof(self, context):
        return self.builder._sizeof(context)

#===============================================================================
# conditional
#===============================================================================
class Switch(Construct):
    """
    A conditional branch. Switch will choose the case to follow based on
    the return value of keyfunc. If no case is matched, and no default value
    is given, SwitchError will be raised.
    See also Pass.

    Parameters:
    * name - the name of the construct
    * keyfunc - a function that takes the context and returns a key, which
      will ne used to choose the relevant case.
    * cases - a dictionary mapping keys to constructs. the keys can be any
      values that may be returned by keyfunc.
    * default - a default value to use when the key is not found in the cases.
      if not supplied, an exception will be raised when the key is not found.
      You can use the builtin construct Pass for 'do-nothing'.
    * include_key - whether or not to include the key in the return value
      of parsing. defualt is False.

    Example:
    Struct("foo",
        UBInt8("type"),
        Switch("value", lambda ctx: ctx.type, {
                1 : UBInt8("spam"),
                2 : UBInt16("spam"),
                3 : UBInt32("spam"),
                4 : UBInt64("spam"),
            }
        ),
    )
    """

    class NoDefault(Construct):
        def _parse(self, stream, context):
            raise SwitchError("no default case defined")
        def _build(self, obj, stream, context):
            raise SwitchError("no default case defined")
        def _sizeof(self, context):
            raise SwitchError("no default case defined")
    NoDefault = NoDefault("No default value specified")

    __slots__ = ["subcons", "keyfunc", "cases", "default", "include_key"]

    def __init__(self, name, keyfunc, cases, default = NoDefault,
                 include_key = False):
        Construct.__init__(self, name)
        self._inherit_flags(*cases.values())
        self.keyfunc = keyfunc
        self.cases = cases
        self.default = default
        self.include_key = include_key
        self._inherit_flags(*cases.values())
        self._set_flag(self.FLAG_DYNAMIC)
    def _parse(self, stream, context):
        key = self.keyfunc(context)
        obj = self.cases.get(key, self.default)._parse(stream, context)
        if self.include_key:
            return key, obj
        else:
            return obj
    def _build(self, obj, stream, context):
        if self.include_key:
            key, obj = obj
        else:
            key = self.keyfunc(context)
        case = self.cases.get(key, self.default)
        case._build(obj, stream, context)
    def _sizeof(self, context):
        case = self.cases.get(self.keyfunc(context), self.default)
        return case._sizeof(context)

class Select(Construct):
    """
    Selects the first matching subconstruct. It will literally try each of
    the subconstructs, until one matches.

    Notes:
    * requires a seekable stream.

    Parameters:
    * name - the name of the construct
    * subcons - the subcons to try (order-sensitive)
    * include_name - a keyword only argument, indicating whether to include
      the name of the selected subcon in the return value of parsing. default
      is false.

    Example:
    Select("foo",
        UBInt64("large"),
        UBInt32("medium"),
        UBInt16("small"),
        UBInt8("tiny"),
    )
    """
    __slots__ = ["subcons", "include_name"]
    def __init__(self, name, *subcons, **kw):
        include_name = kw.pop("include_name", False)
        if kw:
            raise TypeError("the only keyword argument accepted "
                "is 'include_name'", kw)
        Construct.__init__(self, name)
        self.subcons = subcons
        self.include_name = include_name
        self._inherit_flags(*subcons)
        self._set_flag(self.FLAG_DYNAMIC)
    def _parse(self, stream, context):
        for sc in self.subcons:
            pos = stream.tell()
            context2 = context.__copy__()
            try:
                obj = sc._parse(stream, context2)
            except ConstructError:
                stream.seek(pos)
            else:
                context.__update__(context2)
                if self.include_name:
                    return sc.name, obj
                else:
                    return obj
        raise SelectError("no subconstruct matched")
    def _build(self, obj, stream, context):
        if self.include_name:
            name, obj = obj
            for sc in self.subcons:
                if sc.name == name:
                    sc._build(obj, stream, context)
                    return
        else:
            for sc in self.subcons:
                stream2 = BytesIO()
                context2 = context.__copy__()
                try:
                    sc._build(obj, stream2, context2)
                except Exception:
                    pass
                else:
                    context.__update__(context2)
                    stream.write(stream2.getvalue())
                    return
        raise SelectError("no subconstruct matched", obj)
    def _sizeof(self, context):
        raise SizeofError("can't calculate size")


#===============================================================================
# stream manipulation
#===============================================================================
class Pointer(Subconstruct):
    """
    Changes the stream position to a given offset, where the construction
    should take place, and restores the stream position when finished.
    See also Anchor, OnDemand and OnDemandPointer.

    Notes:
    * requires a seekable stream.

    Parameters:
    * offsetfunc: a function that takes the context and returns an absolute
      stream position, where the construction would take place
    * subcon - the subcon to use at `offsetfunc()`

    Example:
    Struct("foo",
        UBInt32("spam_pointer"),
        Pointer(lambda ctx: ctx.spam_pointer,
            Array(5, UBInt8("spam"))
        )
    )
    """
    __slots__ = ["offsetfunc"]
    def __init__(self, offsetfunc, subcon):
        Subconstruct.__init__(self, subcon)
        self.offsetfunc = offsetfunc
    def _parse(self, stream, context):
        newpos = self.offsetfunc(context)
        origpos = stream.tell()
        stream.seek(newpos)
        obj = self.subcon._parse(stream, context)
        stream.seek(origpos)
        return obj
    def _build(self, obj, stream, context):
        newpos = self.offsetfunc(context)
        origpos = stream.tell()
        stream.seek(newpos)
        self.subcon._build(obj, stream, context)
        stream.seek(origpos)
    def _sizeof(self, context):
        return 0

class Peek(Subconstruct):
    """
    Peeks at the stream: parses without changing the stream position.
    See also Union. If the end of the stream is reached when peeking,
    returns None.

    Notes:
    * requires a seekable stream.

    Parameters:
    * subcon - the subcon to peek at
    * perform_build - whether or not to perform building. by default this
      parameter is set to False, meaning building is a no-op.

    Example:
    Peek(UBInt8("foo"))
    """
    __slots__ = ["perform_build"]
    def __init__(self, subcon, perform_build = False):
        Subconstruct.__init__(self, subcon)
        self.perform_build = perform_build
    def _parse(self, stream, context):
        pos = stream.tell()
        try:
            return self.subcon._parse(stream, context)
        except FieldError:
            pass
        finally:
            stream.seek(pos)
    def _build(self, obj, stream, context):
        if self.perform_build:
            self.subcon._build(obj, stream, context)
    def _sizeof(self, context):
        return 0

class OnDemand(Subconstruct):
    """
    Allows for on-demand (lazy) parsing. When parsing, it will return a
    LazyContainer that represents a pointer to the data, but does not actually
    parses it from stream until it's "demanded".
    By accessing the 'value' property of LazyContainers, you will demand the
    data from the stream. The data will be parsed and cached for later use.
    You can use the 'has_value' property to know whether the data has already
    been demanded.
    See also OnDemandPointer.

    Notes:
    * requires a seekable stream.

    Parameters:
    * subcon -
    * advance_stream - whether or not to advance the stream position. by
      default this is True, but if subcon is a pointer, this should be False.
    * force_build - whether or not to force build. If set to False, and the
      LazyContainer has not been demaned, building is a no-op.

    Example:
    OnDemand(Array(10000, UBInt8("foo"))
    """
    __slots__ = ["advance_stream", "force_build"]
    def __init__(self, subcon, advance_stream = True, force_build = True):
        Subconstruct.__init__(self, subcon)
        self.advance_stream = advance_stream
        self.force_build = force_build
    def _parse(self, stream, context):
        obj = LazyContainer(self.subcon, stream, stream.tell(), context)
        if self.advance_stream:
            stream.seek(self.subcon._sizeof(context), 1)
        return obj
    def _build(self, obj, stream, context):
        if not isinstance(obj, LazyContainer):
            self.subcon._build(obj, stream, context)
        elif self.force_build or obj.has_value:
            self.subcon._build(obj.value, stream, context)
        elif self.advance_stream:
            stream.seek(self.subcon._sizeof(context), 1)

class Buffered(Subconstruct):
    """
    Creates an in-memory buffered stream, which can undergo encoding and
    decoding prior to being passed on to the subconstruct.
    See also Bitwise.

    Note:
    * Do not use pointers inside Buffered

    Parameters:
    * subcon - the subcon which will operate on the buffer
    * encoder - a function that takes a string and returns an encoded
      string (used after building)
    * decoder - a function that takes a string and returns a decoded
      string (used before parsing)
    * resizer - a function that takes the size of the subcon and "adjusts"
      or "resizes" it according to the encoding/decoding process.

    Example:
    Buffered(BitField("foo", 16),
        encoder = decode_bin,
        decoder = encode_bin,
        resizer = lambda size: size / 8,
    )
    """
    __slots__ = ["encoder", "decoder", "resizer"]
    def __init__(self, subcon, decoder, encoder, resizer):
        Subconstruct.__init__(self, subcon)
        self.encoder = encoder
        self.decoder = decoder
        self.resizer = resizer
    def _parse(self, stream, context):
        data = _read_stream(stream, self._sizeof(context))
        stream2 = BytesIO(self.decoder(data))
        return self.subcon._parse(stream2, context)
    def _build(self, obj, stream, context):
        size = self._sizeof(context)
        stream2 = BytesIO()
        self.subcon._build(obj, stream2, context)
        data = self.encoder(stream2.getvalue())
        assert len(data) == size
        _write_stream(stream, self._sizeof(context), data)
    def _sizeof(self, context):
        return self.resizer(self.subcon._sizeof(context))

class Restream(Subconstruct):
    """
    Wraps the stream with a read-wrapper (for parsing) or a
    write-wrapper (for building). The stream wrapper can buffer the data
    internally, reading it from- or writing it to the underlying stream
    as needed. For example, BitStreamReader reads whole bytes from the
    underlying stream, but returns them as individual bits.
    See also Bitwise.

    When the parsing or building is done, the stream's close method
    will be invoked. It can perform any finalization needed for the stream
    wrapper, but it must not close the underlying stream.

    Note:
    * Do not use pointers inside Restream

    Parameters:
    * subcon - the subcon
    * stream_reader - the read-wrapper
    * stream_writer - the write wrapper
    * resizer - a function that takes the size of the subcon and "adjusts"
      or "resizes" it according to the encoding/decoding process.

    Example:
    Restream(BitField("foo", 16),
        stream_reader = BitStreamReader,
        stream_writer = BitStreamWriter,
        resizer = lambda size: size / 8,
    )
    """
    __slots__ = ["stream_reader", "stream_writer", "resizer"]
    def __init__(self, subcon, stream_reader, stream_writer, resizer):
        Subconstruct.__init__(self, subcon)
        self.stream_reader = stream_reader
        self.stream_writer = stream_writer
        self.resizer = resizer
    def _parse(self, stream, context):
        stream2 = self.stream_reader(stream)
        obj = self.subcon._parse(stream2, context)
        stream2.close()
        return obj
    def _build(self, obj, stream, context):
        stream2 = self.stream_writer(stream)
        self.subcon._build(obj, stream2, context)
        stream2.close()
    def _sizeof(self, context):
        return self.resizer(self.subcon._sizeof(context))


#===============================================================================
# miscellaneous
#===============================================================================
class Reconfig(Subconstruct):
    """
    Reconfigures a subconstruct. Reconfig can be used to change the name and
    set and clear flags of the inner subcon.

    Parameters:
    * name - the new name
    * subcon - the subcon to reconfigure
    * setflags - the flags to set (default is 0)
    * clearflags - the flags to clear (default is 0)

    Example:
    Reconfig("foo", UBInt8("bar"))
    """
    __slots__ = []
    def __init__(self, name, subcon, setflags = 0, clearflags = 0):
        Construct.__init__(self, name, subcon.conflags)
        self.subcon = subcon
        self._set_flag(setflags)
        self._clear_flag(clearflags)

class Anchor(Construct):
    """
    Returns the "anchor" (stream position) at the point where it's inserted.
    Useful for adjusting relative offsets to absolute positions, or to measure
    sizes of constructs.
    absolute pointer = anchor + relative offset
    size = anchor_after - anchor_before
    See also Pointer.

    Notes:
    * requires a seekable stream.

    Parameters:
    * name - the name of the anchor

    Example:
    Struct("foo",
        Anchor("base"),
        UBInt8("relative_offset"),
        Pointer(lambda ctx: ctx.relative_offset + ctx.base,
            UBInt8("data")
        )
    )
    """
    __slots__ = []
    def _parse(self, stream, context):
        return stream.tell()
    def _build(self, obj, stream, context):
        context[self.name] = stream.tell()
    def _sizeof(self, context):
        return 0

class Value(Construct):
    """
    A computed value.

    Parameters:
    * name - the name of the value
    * func - a function that takes the context and return the computed value

    Example:
    Struct("foo",
        UBInt8("width"),
        UBInt8("height"),
        Value("total_pixels", lambda ctx: ctx.width * ctx.height),
    )
    """
    __slots__ = ["func"]
    def __init__(self, name, func):
        Construct.__init__(self, name)
        self.func = func
        self._set_flag(self.FLAG_DYNAMIC)
    def _parse(self, stream, context):
        return self.func(context)
    def _build(self, obj, stream, context):
        context[self.name] = self.func(context)
    def _sizeof(self, context):
        return 0

#class Dynamic(Construct):
#    """
#    Dynamically creates a construct and uses it for parsing and building.
#    This allows you to create change the construction tree on the fly.
#    Deprecated.
#
#    Parameters:
#    * name - the name of the construct
#    * factoryfunc - a function that takes the context and returns a new
#      construct object which will be used for parsing and building.
#
#    Example:
#    def factory(ctx):
#        if ctx.bar == 8:
#            return UBInt8("spam")
#        if ctx.bar == 9:
#            return String("spam", 9)
#
#    Struct("foo",
#        UBInt8("bar"),
#        Dynamic("spam", factory),
#    )
#    """
#    __slots__ = ["factoryfunc"]
#    def __init__(self, name, factoryfunc):
#        Construct.__init__(self, name, self.FLAG_COPY_CONTEXT)
#        self.factoryfunc = factoryfunc
#        self._set_flag(self.FLAG_DYNAMIC)
#    def _parse(self, stream, context):
#        return self.factoryfunc(context)._parse(stream, context)
#    def _build(self, obj, stream, context):
#        return self.factoryfunc(context)._build(obj, stream, context)
#    def _sizeof(self, context):
#        return self.factoryfunc(context)._sizeof(context)

class LazyBound(Construct):
    """
    Lazily bound construct, useful for constructs that need to make cyclic
    references (linked-lists, expression trees, etc.).

    Parameters:


    Example:
    foo = Struct("foo",
        UBInt8("bar"),
        LazyBound("next", lambda: foo),
    )
    """
    __slots__ = ["bindfunc", "bound"]
    def __init__(self, name, bindfunc):
        Construct.__init__(self, name)
        self.bound = None
        self.bindfunc = bindfunc
    def _parse(self, stream, context):
        if self.bound is None:
            self.bound = self.bindfunc()
        return self.bound._parse(stream, context)
    def _build(self, obj, stream, context):
        if self.bound is None:
            self.bound = self.bindfunc()
        self.bound._build(obj, stream, context)
    def _sizeof(self, context):
        if self.bound is None:
            self.bound = self.bindfunc()
        return self.bound._sizeof(context)

class Pass(Construct):
    """
    A do-nothing construct, useful as the default case for Switch, or
    to indicate Enums.
    See also Switch and Enum.

    Notes:
    * this construct is a singleton. do not try to instatiate it, as it
      will not work...

    Example:
    Pass
    """
    __slots__ = []
    def _parse(self, stream, context):
        pass
    def _build(self, obj, stream, context):
        assert obj is None
    def _sizeof(self, context):
        return 0
    def __reduce__(self):
        return self.__class__.__name__
Pass = Pass(None)

class Terminator(Construct):
    """
    Asserts the end of the stream has been reached at the point it's placed.
    You can use this to ensure no more unparsed data follows.

    Notes:
    * this construct is only meaningful for parsing. for building, it's
      a no-op.
    * this construct is a singleton. do not try to instatiate it, as it
      will not work...

    Example:
    Terminator
    """
    __slots__ = []
    def _parse(self, stream, context):
        if stream.read(1):
            raise TerminatorError("expected end of stream")
    def _build(self, obj, stream, context):
        assert obj is None
    def _sizeof(self, context):
        return 0
Terminator = Terminator(None)
