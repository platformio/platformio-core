#-------------------------------------------------------------------------------
# py3compat.py
#
# Some Python2&3 compatibility code
#-------------------------------------------------------------------------------
import sys
PY3 = sys.version_info[0] == 3

try:
    from collections.abc import MutableMapping  # python >= 3.3
except ImportError:
    from collections import MutableMapping  # python < 3.3


if PY3:
    import io
    StringIO = io.StringIO
    BytesIO = io.BytesIO

    def bchr(i):
        """ When iterating over b'...' in Python 2 you get single b'_' chars
            and in Python 3 you get integers. Call bchr to always turn this
            to single b'_' chars.
        """
        return bytes((i,))

    def u(s):
        return s

    def int2byte(i):
        return bytes((i,))

    def byte2int(b):
        return b

    def str2bytes(s):
        return s.encode("latin-1")

    def str2unicode(s):
        return s

    def bytes2str(b):
        return b.decode('latin-1')

    def decodebytes(b, encoding):
        return bytes(b, encoding)

    advance_iterator = next

else:
    import cStringIO
    StringIO = BytesIO = cStringIO.StringIO

    int2byte = chr
    byte2int = ord
    bchr = lambda i: i

    def u(s):
        return unicode(s, "unicode_escape")

    def str2bytes(s):
        return s

    def str2unicode(s):
        return unicode(s, "unicode_escape")

    def bytes2str(b):
        return b

    def decodebytes(b, encoding):
        return b.decode(encoding)

    def advance_iterator(it):
        return it.next()
