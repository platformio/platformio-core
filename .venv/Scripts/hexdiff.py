#!C:\Users\SasiDharan G\OneDrive\Desktop\git\2bit\platformio-core\.venv\Scripts\python.exe

# Copyright (c) 2011-2018 Alexander Belchenko
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

"""Produce diff for 2 hex files using hex dump as string representation
of compared data.
"""

VERSION = '2.3.0'

USAGE = '''hexdiff: diff dumps of 2 hex files.
Usage:
    python hexdiff.py [options] FILE1 FILE2

Options:
    -h, --help              this help message.
    -v, --version           version info.
'''

import sys


def main(argv=None):
    import getopt

    if argv is None:
        argv = sys.argv[1:]
    try:
        opts, args = getopt.gnu_getopt(argv, 'hv', ['help', 'version'])

        for o,a in opts:
            if o in ('-h', '--help'):
                print(USAGE)
                return 0
            elif o in ('-v', '--version'):
                print(VERSION)
                return 0

    except getopt.GetoptError:
        e = sys.exc_info()[1]     # current exception
        sys.stderr.write(str(e)+"\n")
        sys.stderr.write(USAGE+"\n")
        return 1

    if len(args) != 2:
        sys.stderr.write("ERROR: You should specify 2 files to diff.\n")
        sys.stderr.write(USAGE+"\n")
        return 1

    fname1, fname2 = args

    from intelhex import IntelHex, diff_dumps
    ih1 = IntelHex(fname1)
    ih2 = IntelHex(fname2)
    diff_dumps(ih1, ih2, name1=fname1, name2=fname2)


if __name__ == '__main__':
    sys.exit(main())
