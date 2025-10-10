#!/usr/bin/python
# (c) Alexander Belchenko, 2007, 2009

# [2013/08] NOTE: This file is keeping for historical reasons.
# It may or may not work actually with current version of intelhex,
# and most likely it requires some fixes here and there.

"""Benchmarking.

Run each test 3 times and get median value.
Using 10K array as base test time.

Each other test compared with base with next formula::

         Tc * Nb
    q = ---------
         Tb * Nc

Here:

* Tc - execution time of current test
* Tb - execution time of base
* Nb - array size of base (10K)
* Nc - array size of current test

If resulting value is ``q <= 1.0`` it's the best possible result,
i.e. time increase proportionally to array size.
"""

import gc
import sys
import time

import intelhex
from intelhex.compat import StringIO, range_g

def median(values):
    """Return median value for the list of values.
    @param  values:     list of values for processing.
    @return:            median value.
    """
    values.sort()
    n = int(len(values) / 2)
    return values[n]

def run_test(func, fobj):
    """Run func with argument fobj and measure execution time.
    @param  func:   function for test
    @param  fobj:   data for test
    @return:        execution time
    """
    gc.disable()
    try:
        begin = time.time()
        func(fobj)
        end = time.time()
    finally:
        gc.enable()
    return end - begin

def run_readtest_N_times(func, hexstr, n):
    """Run each test N times.
    @param  func:   function for test
    @param  hexstr: string with content of hex file to read
    @param  n:      times to repeat.
    @return:        (median time, times list)
    """
    assert n > 0
    times = []
    for i in range_g(n):
        sio = StringIO(hexstr)
        times.append(run_test(func, sio))
        sio.close()
    t = median(times)
    return t, times

def run_writetest_N_times(func, n):
    """Run each test N times.
    @param  func:   function for test
    @param  n:      times to repeat.
    @return:        (median time, times list)
    """
    assert n > 0
    times = []
    for i in range_g(n):
        sio = StringIO()
        times.append(run_test(func, sio))
        sio.close()
    t = median(times)
    return t, times

def time_coef(tc, nc, tb, nb):
    """Return time coefficient relative to base numbers.
    @param  tc:     current test time
    @param  nc:     current test data size
    @param  tb:     base test time
    @param  nb:     base test data size
    @return:        time coef.
    """
    tc = float(tc)
    nc = float(nc)
    tb = float(tb)
    nb = float(nb)
    q = (tc * nb) / (tb * nc)
    return q

def get_test_data(n1, offset, n2):
    """Create test data on given pattern.
    @param  n1:     size of first part of array at base address 0.
    @param  offset: offset for second part of array.
    @param  n2:     size of second part of array at given offset.
    @return:        (overall size, hex file, IntelHex object)
    """
    # make IntelHex object
    ih = intelhex.IntelHex()
    addr = 0
    for i in range_g(n1):
        ih[addr] = addr % 256
        addr += 1
    addr += offset
    for i in range_g(n2):
        ih[addr] = addr % 256
        addr += 1
    # make hex file
    sio = StringIO()
    ih.write_hex_file(sio)
    hexstr = sio.getvalue()
    sio.close()
    #
    return n1+n2, hexstr, ih

def get_base_50K():
    return get_test_data(50000, 0, 0)

def get_250K():
    return get_test_data(250000, 0, 0)

def get_100K_100K():
    return get_test_data(100000, 1000000, 100000)

def get_0_100K():
    return get_test_data(0, 1000000, 100000)

def get_1M():
    return get_test_data(1000000, 0, 0)


class Measure(object):
    """Measure execution time helper."""

    data_set = [
        # (data name, getter)
        ('base 50K', get_base_50K),     # first should be base numbers
        ('250K', get_250K),
        ('1M', get_1M),
        ('100K+100K', get_100K_100K),
        ('0+100K', get_0_100K),
        ]

    def __init__(self, n=3, read=True, write=True):
        self.n = n
        self.read = read
        self.write = write
        self.results = []

    def measure_one(self, data):
        """Do measuring of read and write operations.
        @param  data:   3-tuple from get_test_data
        @return:        (time readhex, time writehex)
        """
        _unused, hexstr, ih = data
        tread, twrite = 0.0, 0.0
        if self.read:
            tread = run_readtest_N_times(intelhex.IntelHex, hexstr, self.n)[0]
        if self.write:
            twrite = run_writetest_N_times(ih.write_hex_file, self.n)[0]
        return tread, twrite

    def measure_all(self):
        for name, getter in self.data_set:
            data = getter()
            times = self.measure_one(data)
            self.results.append((name, times, data[0]))

    def print_report(self, to_file=None):
        if to_file is None:
            to_file = sys.stdout

        base_title, base_times, base_n = self.results[0]
        base_read, base_write = base_times
        read_report = ['%-10s\t%7.3f' % (base_title, base_read)]
        write_report = ['%-10s\t%7.3f' % (base_title, base_write)]

        for item in self.results[1:]:
            cur_title, cur_times, cur_n = item
            cur_read, cur_write = cur_times
            if self.read:
                qread = time_coef(cur_read, cur_n,
                                  base_read, base_n)
                read_report.append('%-10s\t%7.3f\t%7.3f' % (cur_title,
                                                           cur_read,
                                                           qread))
            if self.write:
                qwrite = time_coef(cur_write, cur_n,
                                   base_write, base_n)
                write_report.append('%-10s\t%7.3f\t%7.3f' % (cur_title,
                                                            cur_write,
                                                            qwrite))
        if self.read:
            to_file.write('Read operation:\n')
            to_file.write('\n'.join(read_report))
            to_file.write('\n\n')
        if self.write:
            to_file.write('Write operation:\n')
            to_file.write('\n'.join(write_report))
            to_file.write('\n\n')


HELP = """\
Usage: python _bench.py [OPTIONS]

Options:
    -h      this help
    -n N    repeat tests N times
    -r      run only tests for read operation
    -w      run only tests for write operation

If option -r or -w is not specified then all tests will be run.
"""


def main(argv=None):
    """Main function to run benchmarks.
    @param  argv:   command-line arguments.
    @return:        exit code (0 is OK).
    """
    import getopt

    # default values
    test_read = None
    test_write = None
    n = 3       # number of repeat

    if argv is None:
        argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, 'hn:rw', [])

        for o,a in opts:
            if o == '-h':
                print(HELP)
                return 0
            elif o == '-n':
                n = int(a)
            elif o == '-r':
                test_read = True
            elif o == '-w':
                test_write = True

        if args:
            raise getopt.GetoptError('Arguments are not used.')
    except getopt.GetoptError:
        msg = sys.exc_info()[1]     # current exception
        txt = str(msg)
        print(txt)
        return 1

    if (test_read, test_write) == (None, None):
        test_read = test_write = True

    m = Measure(n, test_read, test_write)
    m.measure_all()
    m.print_report()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


"""

Some Results
************


21/04/2007 revno.40
Python 2.5 @ Windows XP, Intel Celeron M CPU 430 @ 1.73GHz

Read operation:
base 10K  	  0.031
100K      	  0.360	  1.161
1M        	  3.500	  1.129
100K+100K 	  0.719	  1.160
0+100K    	  0.360	  1.161

Write operation:
base 10K  	  0.031
100K      	  0.297	  0.958
1M        	  2.953	  0.953
100K+100K 	  1.328	  2.142
0+100K    	  0.312	  1.006


21/04/2007 revno.46
Python 2.5 @ Windows XP, Intel Celeron M CPU 430 @ 1.73GHz

Read operation:
base 10K  	  0.016
100K      	  0.203	  1.269
1M        	  2.000	  1.250
100K+100K 	  0.422	  1.319
0+100K    	  0.203	  1.269

Write operation:
base 10K  	  0.031
100K      	  0.297	  0.958
1M        	  2.969	  0.958
100K+100K 	  1.328	  2.142
0+100K    	  0.312	  1.006


22/04/2007 revno.48
Python 2.5 @ Windows XP, Intel Celeron M CPU 430 @ 1.73GHz

Read operation:
base 10K  	  0.016
100K      	  0.187	  1.169
1M        	  1.891	  1.182
100K+100K 	  0.406	  1.269
0+100K    	  0.188	  1.175

Write operation:
base 10K  	  0.031
100K      	  0.296	  0.955
1M        	  2.969	  0.958
100K+100K 	  1.328	  2.142
0+100K    	  0.312	  1.006


19/08/2008 revno.72
Python 2.5.2 @ Windows XP, Intel Celeron M CPU 430 @ 1.73GHz

Read operation:
base 10K          0.016
100K              0.171   1.069
1M                1.734   1.084
100K+100K         0.375   1.172
0+100K            0.172   1.075

Write operation:
base 10K          0.016
100K              0.156   0.975
1M                1.532   0.957
100K+100K         0.344   1.075
0+100K            0.156   0.975

"""
