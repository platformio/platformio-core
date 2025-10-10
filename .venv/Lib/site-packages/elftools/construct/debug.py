"""
Debugging utilities for constructs
"""
from __future__ import print_function
import sys
import traceback
import pdb
import inspect
from .core import Construct, Subconstruct
from .lib import HexString, Container, ListContainer


class Probe(Construct):
    """
    A probe: dumps the context, stack frames, and stream content to the screen
    to aid the debugging process.
    See also Debugger.

    Parameters:
    * name - the display name
    * show_stream - whether or not to show stream contents. default is True.
      the stream must be seekable.
    * show_context - whether or not to show the context. default is True.
    * show_stack - whether or not to show the upper stack frames. default
      is True.
    * stream_lookahead - the number of bytes to dump when show_stack is set.
      default is 100.

    Example:
    Struct("foo",
        UBInt8("a"),
        Probe("between a and b"),
        UBInt8("b"),
    )
    """
    __slots__ = [
        "printname", "show_stream", "show_context", "show_stack",
        "stream_lookahead"
    ]
    counter = 0

    def __init__(self, name = None, show_stream = True,
                 show_context = True, show_stack = True,
                 stream_lookahead = 100):
        Construct.__init__(self, None)
        if name is None:
            Probe.counter += 1
            name = "<unnamed %d>" % (Probe.counter,)
        self.printname = name
        self.show_stream = show_stream
        self.show_context = show_context
        self.show_stack = show_stack
        self.stream_lookahead = stream_lookahead
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.printname)
    def _parse(self, stream, context):
        self.printout(stream, context)
    def _build(self, obj, stream, context):
        self.printout(stream, context)
    def _sizeof(self, context):
        return 0

    def printout(self, stream, context):
        obj = Container()
        if self.show_stream:
            obj.stream_position = stream.tell()
            follows = stream.read(self.stream_lookahead)
            if not follows:
                obj.following_stream_data = "EOF reached"
            else:
                stream.seek(-len(follows), 1)
                obj.following_stream_data = HexString(follows)
            print

        if self.show_context:
            obj.context = context

        if self.show_stack:
            obj.stack = ListContainer()
            frames = [s[0] for s in inspect.stack()][1:-1]
            frames.reverse()
            for f in frames:
                a = Container()
                a.__update__(f.f_locals)
                obj.stack.append(a)

        print("=" * 80)
        print("Probe", self.printname)
        print(obj)
        print("=" * 80)

class Debugger(Subconstruct):
    """
    A pdb-based debugger. When an exception occurs in the subcon, a debugger
    will appear and allow you to debug the error (and even fix on-the-fly).

    Parameters:
    * subcon - the subcon to debug

    Example:
    Debugger(
        Enum(UBInt8("foo"),
            a = 1,
            b = 2,
            c = 3
        )
    )
    """
    __slots__ = ["retval"]
    def _parse(self, stream, context):
        try:
            return self.subcon._parse(stream, context)
        except Exception:
            self.retval = NotImplemented
            self.handle_exc("(you can set the value of 'self.retval', "
                "which will be returned)")
            if self.retval is NotImplemented:
                raise
            else:
                return self.retval
    def _build(self, obj, stream, context):
        try:
            self.subcon._build(obj, stream, context)
        except Exception:
            self.handle_exc()
    def handle_exc(self, msg = None):
        print("=" * 80)
        print("Debugging exception of %s:" % (self.subcon,))
        print("".join(traceback.format_exception(*sys.exc_info())[1:]))
        if msg:
            print(msg)
        pdb.post_mortem(sys.exc_info()[2])
        print("=" * 80)
