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

"""Merge content of several hex files into one file."""

VERSION = '2.3.0'

USAGE = '''hexmerge: merge content of hex files.
Usage:
    python hexmerge.py [options] FILES...

Options:
    -h, --help              this help message.
    -v, --version           version info.
    -o, --output=FILENAME   output file name (emit output to stdout
                            if option is not specified)
    -r, --range=START:END   specify address range for output
                            (ascii hex value). Both values are inclusive.
                            Range can be in form 'START:' or ':END'.
    --no-start-addr         Don't write start addr to output file.
    --overlap=METHOD        What to do when data in files overlapped.
                            Supported variants:
                            * error -- stop and show error message (default)
                            * ignore -- keep data from first file that
                                        contains data at overlapped address
                            * replace -- use data from last file that
                                         contains data at overlapped address

Arguments:
    FILES       list of hex files for merging
                (use '-' to read content from stdin)

You can specify address range for each file in the form:

    filename:START:END

See description of range option above.

You can omit START or END, so supported variants are:

    filename:START:     read filename and use data starting from START addr
    filename::END       read filename and use data till END addr

Use entire file content:

    filename
or
    filename::
'''

import sys


def main(args=None):
    import getopt

    output = None
    start = None
    end = None
    write_start_addr = True
    overlap = 'error'

    if args is None:
        args = sys.argv[1:]
    try:
        opts, args = getopt.gnu_getopt(args, 'hvo:r:',
                                       ['help', 'version',
                                        'output=', 'range=',
                                        'no-start-addr', 'overlap=',
                                       ])

        for o,a in opts:
            if o in ('-h', '--help'):
                print(USAGE)
                return 0
            elif o in ('-v', '--version'):
                print(VERSION)
                return 0
            elif o in ('-o', '--output'):
                output = a
            elif o in ("-r", "--range"):
                try:
                    l = a.split(":")
                    if l[0] != '':
                        start = int(l[0], 16)
                    if l[1] != '':
                        end = int(l[1], 16)
                except (ValueError, IndexError):
                    raise getopt.GetoptError('Bad range value(s)')
            elif o == '--no-start-addr':
                write_start_addr = False
            elif o == '--overlap':
                if a in ('error', 'ignore', 'replace'):
                    overlap = a
                else:
                    raise getopt.GetoptError('Bad overlap value')

        if len(args) == 0:
            raise getopt.GetoptError('You should specify file list')

    except getopt.GetoptError:
        e = sys.exc_info()[1]     # current exception
        sys.stderr.write(str(e)+"\n")
        sys.stderr.write(USAGE+"\n")
        return 1

    import intelhex
    # TODO: move actual merge code into intelhex package as helper function
    #       and write couple of tests for it.
    res = intelhex.IntelHex()

    def end_addr_inclusive(addr):
        if addr is not None:
            return addr + 1
        return addr

    for f in args:
        try:
            fname, fstart, fend = intelhex._get_file_and_addr_range(f)
        except intelhex._BadFileNotation:
            sys.stderr.write('Bad argument: "%s"\n' % f)
            sys.stderr.write(USAGE+"\n")
            return 1
        if fname == '-':
            fname = sys.stdin
        ih = intelhex.IntelHex(fname)
        if (fstart, fend) != (None, None):
            ih = ih[fstart:end_addr_inclusive(fend)]
        try:
            res.merge(ih, overlap)
        except intelhex.AddressOverlapError:
            e = sys.exc_info()[1]     # current exception
            sys.stderr.write('Merging: '+fname+"\n")
            sys.stderr.write(str(e)+"\n")
            return 1

    if (start, end) != (None, None):
        res = res[start:end_addr_inclusive(end)]
    if output is None:
        output = sys.stdout
    res.write_hex_file(output, write_start_addr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
