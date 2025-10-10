#!C:\Users\SasiDharan G\OneDrive\Desktop\git\2bit\platformio-core\.venv\Scripts\python.exe

# Copyright (c) 2005-2018 Alexander Belchenko
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

'''Intel HEX file format hex2bin convertor utility.'''

VERSION = '2.3.0'

if __name__ == '__main__':
    import getopt
    import os
    import sys

    usage = '''Hex2Bin convertor utility.
Usage:
    python hex2bin.py [options] INFILE [OUTFILE]

Arguments:
    INFILE      name of hex file for processing.
    OUTFILE     name of output file. If omitted then output
                will be writing to stdout.

Options:
    -h, --help              this help message.
    -v, --version           version info.
    -p, --pad=FF            pad byte for empty spaces (ascii hex value).
    -r, --range=START:END   specify address range for writing output
                            (ascii hex value).
                            Range can be in form 'START:' or ':END'.
    -l, --length=NNNN,
    -s, --size=NNNN         size of output (decimal value).
'''

    pad = None
    start = None
    end = None
    size = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvp:r:l:s:",
                                  ["help", "version", "pad=", "range=",
                                   "length=", "size="])

        for o, a in opts:
            if o in ("-h", "--help"):
                print(usage)
                sys.exit(0)
            elif o in ("-v", "--version"):
                print(VERSION)
                sys.exit(0)
            elif o in ("-p", "--pad"):
                try:
                    pad = int(a, 16) & 0x0FF
                except:
                    raise getopt.GetoptError('Bad pad value')
            elif o in ("-r", "--range"):
                try:
                    l = a.split(":")
                    if l[0] != '':
                        start = int(l[0], 16)
                    if l[1] != '':
                        end = int(l[1], 16)
                except:
                    raise getopt.GetoptError('Bad range value(s)')
            elif o in ("-l", "--lenght", "-s", "--size"):
                try:
                    size = int(a, 10)
                except:
                    raise getopt.GetoptError('Bad size value')

        if start != None and end != None and size != None:
            raise getopt.GetoptError('Cannot specify START:END and SIZE simultaneously')

        if not args:
            raise getopt.GetoptError('Hex file is not specified')

        if len(args) > 2:
            raise getopt.GetoptError('Too many arguments')

    except getopt.GetoptError:
        msg = sys.exc_info()[1]     # current exception
        txt = 'ERROR: '+str(msg)  # that's required to get not-so-dumb result from 2to3 tool
        print(txt)
        print(usage)
        sys.exit(2)

    fin = args[0]
    if not os.path.isfile(fin):
        txt = "ERROR: File not found: %s" % fin  # that's required to get not-so-dumb result from 2to3 tool
        print(txt)
        sys.exit(1)

    if len(args) == 2:
        fout = args[1]
    else:
        # write to stdout
        from intelhex import compat
        fout = compat.get_binary_stdout()

    from intelhex import hex2bin
    sys.exit(hex2bin(fin, fout, start, end, size, pad))
