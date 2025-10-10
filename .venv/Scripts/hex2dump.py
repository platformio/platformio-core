#!C:\Users\SasiDharan G\OneDrive\Desktop\git\2bit\platformio-core\.venv\Scripts\python.exe

# Copyright (c) 2008-2018 Alexander Belchenko
# All rights reserved.
#
# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided
# that the following conditions are met:
#
# * Redistributions of source code must retain
#   the above copyright notice, this list of conditions
#   and the following disclaimer.
# * Redistributions in binary form must reproduce
#   the above copyright notice, this list of conditions
#   and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the author nor the names
#   of its contributors may be used to endorse
#   or promote products derived from this software
#   without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Show content of hex file as hexdump."""

VERSION = '2.3.0'

USAGE = '''hex2dump: show content of hex file as hexdump.
Usage:
    python hex2dump.py [options] HEXFILE

Options:
    -h, --help              this help message.
    -v, --version           version info.
    -r, --range=START:END   specify address range for dumping
                            (ascii hex value).
                            Range can be in form 'START:' or ':END'.
    --width=N               dump N data bytes per line (default: 16).

Arguments:
    HEXFILE     name of hex file for processing (use '-' to read
                from stdin)
'''

import sys

DEFAULT_WIDTH = 16

def hex2dump(hexfile, start=None, end=None, width=DEFAULT_WIDTH):
    import intelhex
    if hexfile == '-':
        hexfile = sys.stdin
    try:
        ih = intelhex.IntelHex(hexfile)
    except (IOError, intelhex.IntelHexError):
        e = sys.exc_info()[1]     # current exception
        sys.stderr.write('Error reading file: %s\n' % e)
        return 1
    if not (start is None and end is None):
        ih = ih[slice(start,end)]
    ih.dump(tofile=sys.stdout, width=width)
    return 0


def main(argv=None):
    import getopt

    if argv is None:
        argv = sys.argv[1:]

    start = None
    end = None
    width = DEFAULT_WIDTH

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvp:r:",
                                  ["help", "version", "range=", "width="])
        for o, a in opts:
            if o in ("-h", "--help"):
                print(USAGE)
                return 0
            elif o in ("-v", "--version"):
                print(VERSION)
                return 0
            elif o in ("-r", "--range"):
                try:
                    l = a.split(":")
                    if l[0] != '':
                        start = int(l[0], 16)
                    if l[1] != '':
                        end = int(l[1], 16)
                except:
                    raise getopt.GetoptError('Bad range value(s)')
            elif o == "--width":
                try:
                    width = int(a)
                    if width < 1:
                        raise ValueError
                except:
                    raise getopt.GetoptError('Bad width value (%s)' % a)
        if not args:
            raise getopt.GetoptError('Hex file is not specified')
        if len(args) > 1:
            raise getopt.GetoptError('Too many arguments')
    except getopt.GetoptError:
        msg = sys.exc_info()[1]     # current exception
        txt = 'ERROR: '+str(msg)  # that's required to get not-so-dumb result from 2to3 tool
        print(txt)
        print(USAGE)
        return 2

    try:
        return hex2dump(args[0], start, end, width)
    except IOError:
        e = sys.exc_info()[1]     # current exception
        import errno
        if e.errno not in (0, errno.EPIPE):
            raise


if __name__ == '__main__':
    import sys
    sys.exit(main())
