# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from math import ceil
from os.path import dirname, join, realpath
from sys import exit as sys_exit
from sys import path

path.append("..")

from platformio import util
from platformio.platforms.base import PlatformFactory, get_packages


def generate_boards(boards):

    def _round_memory_size(size):
        size = ceil(size)
        for b in (64, 32, 16, 8, 4, 2, 1):
            if b < size:
                return int(ceil(size / b) * b)
        assert NotImplemented()

    lines = []

    lines.append("""
.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM""")

    for board in sorted(boards):
        for type_, data in board.iteritems():
            assert type_ in util.get_boards()
            board_ram = float(data['upload']['maximum_ram_size']) / 1024
            lines.append("""
    * - ``{type}``
      - `{name} <{url}>`_
      - {mcu}
      - {f_cpu:d} MHz
      - {rom} Kb
      - {ram} Kb""".format(
                type=type_,
                name=data['name'],
                url=data['url'],
                mcu=data['build']['mcu'].upper(),
                f_cpu=int((data['build']['f_cpu'][:-1])) / 1000000,
                ram=int(board_ram) if board_ram % 1 == 0 else board_ram,
                rom=_round_memory_size(
                    data['upload']['maximum_size'] / 1024)
            ))

    return "\n".join(lines + [""])


def generate_packages(packages):
    allpackages = get_packages()
    lines = []
    lines.append(""".. list-table::
    :header-rows:  1

    * - Name
      - Contents""")
    for type_, data in packages.iteritems():
        assert type_ in allpackages
        contitems = [
            "`%s <%s>`_" % (name, url)
            for name, url in allpackages[type_]
        ]
        lines.append("""
    * - ``{type_}``
      - {contents}""".format(
            type_=type_,
            contents=", ".join(contitems)))

    lines.append("""
.. warning::
    **Linux Users:** Don't forget to install "udev" rules file
    `99-platformio-udev.rules <https://github.com/ivankravets/platformio/blob/develop/scripts/99-platformio-udev.rules>`_ (an instruction is located in the file).

""")
    return "\n".join(lines)


def generate_platform(name):
    print "Processing platform: %s" % name
    lines = []

    lines.append(".. _platform_%s:" % name)
    lines.append("")

    _title = "Platform ``%s``" % name
    lines.append(_title)
    lines.append("=" * len(_title))

    p = PlatformFactory.newPlatform(name)
    lines.extend([l.strip() for l in p.__doc__.split("\n")])

    lines.append(""".. contents::""")
    lines.append("""
Packages
--------
""")
    lines.append(generate_packages(p.get_packages()))
    lines.append("""
Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Web 2.0 <http://platformio.org/#!/boards>`_ site
    * For more detailed ``board`` information please scroll tables below by
      horizontal.
""")

    vendors = {}
    for board, data in util.get_boards().items():
        platform = data['platform']
        vendor = data['vendor']
        if name in platform:
            if vendor in vendors:
                vendors[vendor].append({board: data})
            else:
                vendors[vendor] = [{board: data}]
    for vendor, boards in sorted(vendors.iteritems()):
        lines.append(str(vendor))
        lines.append("~" * len(vendor))
        lines.append(generate_boards(boards))
    return "\n".join(lines)


def update_platform_docs():
    for name in PlatformFactory.get_platforms().keys():
        rst_path = join(
            dirname(realpath(__file__)), "..", "docs", "platforms", "%s.rst" % name)
        with open(rst_path, "w") as f:
            f.write(generate_platform(name))


def generate_framework(name, data):
    print "Processing framework: %s" % name
    lines = []

    lines.append(".. _framework_%s:" % name)
    lines.append("")

    _title = "Framework ``%s``" % name
    lines.append(_title)
    lines.append("=" * len(_title))
    lines.append(data['description'])
    lines.append("""\n.. contents::""")
    lines.append("""
Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Web 2.0 <http://platformio.org/#!/boards>`_ site
    * For more detailed ``board`` information please scroll tables below by horizontal.
""")

    vendors = {}
    for board, data in util.get_boards().items():
        frameworks = data['frameworks']
        vendor = data['vendor']
        if name in frameworks:
            if vendor in vendors:
                vendors[vendor].append({board: data})
            else:
                vendors[vendor] = [{board: data}]
    for vendor, boards in sorted(vendors.iteritems()):
        lines.append(str(vendor))
        lines.append("~" * len(vendor))
        lines.append(generate_boards(boards))
    return "\n".join(lines)


def update_framework_docs():
    for name, data in util.get_frameworks().items():
        rst_path = join(util.get_source_dir(), "..", "docs", "frameworks",
                        "%s.rst" % name)
        with open(rst_path, "w") as f:
            f.write(generate_framework(name, data))


def main():
    update_platform_docs()
    update_framework_docs()

if __name__ == "__main__":
    sys_exit(main())
