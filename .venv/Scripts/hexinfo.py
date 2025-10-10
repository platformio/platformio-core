#!C:\Users\SasiDharan G\OneDrive\Desktop\git\2bit\platformio-core\.venv\Scripts\python.exe

# Copyright (c) 2015 Andrew Fernandes <andrew@fernandes.org>
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

"""Summarize the information in a hex file by printing the execution
        start address (if any), and the address ranges covered by the
        data (if any), in YAML format.
"""

VERSION = '2.3.0'

USAGE = '''hexinfo: summarize a hex file's contents.
Usage:
    python hexinfo.py [options] FILE [ FILE ... ]

Options:
    -h, --help              this help message.
    -v, --version           version info.
'''

import sys

INDENT = '  '
INLIST = '- '

def summarize_yaml(fname):
    print("{:s}file: '{:s}'".format(INLIST, fname))
    from intelhex import IntelHex
    ih = IntelHex(fname)
    if ih.start_addr:
        keys = sorted(ih.start_addr.keys())
        if keys == ['CS','IP']:
            entry = ih.start_addr['CS'] * 65536 + ih.start_addr['IP']
        elif keys == ['EIP']:
            entry = ih.start_addr['EIP']
        else:
            raise RuntimeError("unknown 'IntelHex.start_addr' found")
        print("{:s}entry: 0x{:08X}".format(INDENT, entry))
    segments = ih.segments()
    if segments:
        print("{:s}data:".format(INDENT))
        for s in segments:
            print("{:s}{:s}{{ first: 0x{:08X}, last: 0x{:08X}, length: 0x{:08X} }}".format(INDENT, INLIST, s[0], s[1]-1, s[1]-s[0]))
    print("")

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

    if len(args) < 1:
        sys.stderr.write("ERROR: You should specify one or more files to summarize.\n")
        sys.stderr.write(USAGE+"\n")
        return 1

    for fname in args:
        summarize_yaml(fname)

if __name__ == '__main__':
    sys.exit(main())
