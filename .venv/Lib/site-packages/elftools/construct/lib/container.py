"""
Various containers.
"""

from pprint import pformat
from .py3compat import MutableMapping

def recursion_lock(retval, lock_name = "__recursion_lock__"):
    def decorator(func):
        def wrapper(self, *args, **kw):
            if getattr(self, lock_name, False):
                return retval
            setattr(self, lock_name, True)
            try:
                return func(self, *args, **kw)
            finally:
                setattr(self, lock_name, False)
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

class Container(MutableMapping):
    """
    A generic container of attributes.

    Containers are the common way to express parsed data.
    """

    def __init__(self, **kw):
        self.__dict__ = kw

    # The core dictionary interface.

    def __getitem__(self, name):
        return self.__dict__[name]

    def __delitem__(self, name):
        del self.__dict__[name]

    def __setitem__(self, name, value):
        self.__dict__[name] = value

    def keys(self):
        return self.__dict__.keys()

    def __len__(self):
        return len(self.__dict__.keys())

    # Extended dictionary interface.

    def update(self, other):
        self.__dict__.update(other)

    __update__ = update

    def __contains__(self, value):
        return value in self.__dict__

    # Rich comparisons.

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    # Copy interface.

    def copy(self):
        return self.__class__(**self.__dict__)

    __copy__ = copy

    # Iterator interface.

    def __iter__(self):
        return iter(self.__dict__)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.__dict__))

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, str(self.__dict__))

class FlagsContainer(Container):
    """
    A container providing pretty-printing for flags.

    Only set flags are displayed.
    """

    @recursion_lock("<...>")
    def __str__(self):
        d = dict((k, self[k]) for k in self
                 if self[k] and not k.startswith("_"))
        return "%s(%s)" % (self.__class__.__name__, pformat(d))

class ListContainer(list):
    """
    A container for lists.
    """

    __slots__ = ["__recursion_lock__"]

    @recursion_lock("[...]")
    def __str__(self):
        return pformat(self)

class LazyContainer(object):

    __slots__ = ["subcon", "stream", "pos", "context", "_value"]

    def __init__(self, subcon, stream, pos, context):
        self.subcon = subcon
        self.stream = stream
        self.pos = pos
        self.context = context
        self._value = NotImplemented

    def __eq__(self, other):
        try:
            return self._value == other._value
        except AttributeError:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return self.__pretty_str__()

    def __pretty_str__(self, nesting = 1, indentation = "    "):
        if self._value is NotImplemented:
            text = "<unread>"
        elif hasattr(self._value, "__pretty_str__"):
            text = self._value.__pretty_str__(nesting, indentation)
        else:
            text = str(self._value)
        return "%s: %s" % (self.__class__.__name__, text)

    def read(self):
        self.stream.seek(self.pos)
        return self.subcon._parse(self.stream, self.context)

    def dispose(self):
        self.subcon = None
        self.stream = None
        self.context = None
        self.pos = None

    def _get_value(self):
        if self._value is NotImplemented:
            self._value = self.read()
        return self._value

    value = property(_get_value)

    has_value = property(lambda self: self._value is not NotImplemented)
