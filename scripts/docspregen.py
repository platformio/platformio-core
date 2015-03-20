# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from math import ceil
from os.path import dirname, join, realpath
from sys import exit as sys_exit
from sys import path

path.append("..")

from platformio import util
from platformio.platforms.base import PlatformFactory, get_packages


def is_compat_platform_and_framework(platform, framework):
    p = PlatformFactory.newPlatform(platform)
    for pkg in p.get_packages().keys():
        if pkg.startswith("framework-%s" % framework):
            return True
    return False


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
    lines.append(p.get_description())
    lines.append("""
For more detailed information please visit `vendor site <%s>`_.""" %
                 p.get_vendor_url())
    lines.append("""
.. contents::""")
    lines.append("""
Packages
--------
""")
    lines.append(generate_packages(p.get_packages()))

    lines.append("""
Frameworks
----------
.. list-table::
    :header-rows:  1

    * - Name
      - Description""")

    _frameworks = util.get_frameworks()
    for framework in sorted(_frameworks.keys()):
        if not is_compat_platform_and_framework(name, framework):
            continue
        lines.append("""
    * - :ref:`framework_{type_}`
      - {description}""".format(
            type_=framework,
            description=_frameworks[framework]['description']))

    lines.append("""
Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/#!/boards>`_
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
            dirname(realpath(__file__)), "..", "docs", "platforms",
            "%s.rst" % name)
        with open(rst_path, "w") as f:
            f.write(generate_platform(name))


def generate_framework(type_, data):
    print "Processing framework: %s" % type_
    lines = []

    lines.append(".. _framework_%s:" % type_)
    lines.append("")

    _title = "Framework ``%s``" % type_
    lines.append(_title)
    lines.append("=" * len(_title))
    lines.append(data['description'])
    lines.append("""
For more detailed information please visit `vendor site <%s>`_.
""" % data['url'])

    lines.append(".. contents::")

    lines.append("""
Platforms
---------
.. list-table::
    :header-rows:  1

    * - Name
      - Description""")

    for platform in sorted(PlatformFactory.get_platforms().keys()):
        if not is_compat_platform_and_framework(platform, type_):
            continue
        p = PlatformFactory.newPlatform(platform)
        lines.append("""
    * - :ref:`platform_{type_}`
      - {description}""".format(
            type_=platform,
            description=p.get_description()))

    lines.append("""
Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/#!/boards>`_
    * For more detailed ``board`` information please scroll tables below by horizontal.
""")

    vendors = {}
    for board, data in util.get_boards().items():
        frameworks = data['frameworks']
        vendor = data['vendor']
        if type_ in frameworks:
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
