# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from math import ceil
from os.path import dirname, isfile, join, realpath
from sys import exit as sys_exit
from sys import path

path.append("..")

from platformio import util
from platformio.managers.platform import PlatformFactory, PlatformManager

API_PACKAGES = util.get_api_result("/packages")
API_FRAMEWORKS = util.get_api_result("/frameworks")
BOARDS = PlatformManager().get_installed_boards()
PLATFORM_MANIFESTS = PlatformManager().get_installed()


def is_compat_platform_and_framework(platform, framework):
    p = PlatformFactory.newPlatform(platform)
    for pkg in p.packages.keys():
        if pkg.startswith("framework-%s" % framework):
            return True
    return False


def generate_boards(boards):

    def _round_memory_size(size):
        if size == 1:
            return 1

        size = ceil(size)
        for b in (64, 32, 16, 8, 4, 2, 1):
            if b < size:
                return int(ceil(size / b) * b)
        assert NotImplemented()

    lines = []

    lines.append("""
.. list-table::
    :header-rows:  1

    * - ID
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM""")

    for data in sorted(boards, key=lambda item: item['id']):
        board_ram = float(data['ram']) / 1024
        lines.append("""
    * - ``{id}``
      - `{name} <{url}>`_
      - {mcu}
      - {f_cpu:d} MHz
      - {rom} Kb
      - {ram} Kb""".format(
            id=data['id'],
            name=data['name'],
            url=data['url'],
            mcu=data['mcu'].upper(),
            f_cpu=int(data['fcpu']) / 1000000,
            ram=int(board_ram) if board_ram % 1 == 0 else board_ram,
            rom=_round_memory_size(data['rom'] / 1024)))

    return "\n".join(lines + [""])


def generate_packages(platform, packagenames, is_embedded):
    if not packagenames:
        return
    lines = []
    lines.append("""
Packages
--------
""")
    lines.append(""".. list-table::
    :header-rows:  1

    * - Name
      - Contents""")
    for name in sorted(packagenames):
        assert name in API_PACKAGES, name
        contitems = [
            "`{name} <{url}>`_".format(**item) for item in API_PACKAGES[name]
        ]
        lines.append("""
    * - ``{name}``
      - {contents}""".format(
            name=name, contents=", ".join(contitems)))

    if is_embedded:
        lines.append("""
.. warning::
    **Linux Users**:

    * Ubuntu/Debian users may need to add own "username" to the "dialout"
      group if they are not "root", doing this issuing a
      ``sudo usermod -a -G dialout yourusername``.
    * Install "udev" rules file `99-platformio-udev.rules <https://github.com/platformio/platformio/blob/develop/scripts/99-platformio-udev.rules>`_
      (an instruction is located in the file).
    * Raspberry Pi users, please read this article
      `Enable serial port on Raspberry Pi <https://hallard.me/enable-serial-port-on-raspberry-pi/>`__.
""")

        if platform == "teensy":
            lines.append("""
    **Windows Users:** Teensy programming uses only Windows built-in HID
    drivers. When Teensy is programmed to act as a USB Serial device,
    Windows XP, Vista, 7 and 8 require `this serial driver
    <http://www.pjrc.com/teensy/serial_install.exe>`_
    is needed to access the COM port your program uses. No special driver
    installation is necessary on Windows 10.
""")
        else:
            lines.append("""
    **Windows Users:** Please check that you have correctly installed USB
    driver from board manufacturer

""")

    return "\n".join(lines)


def generate_platform(name):
    print "Processing platform: %s" % name
    lines = []

    lines.append(
        """..  Copyright 2014-present PlatformIO <contact@platformio.org>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
""")

    lines.append(".. _platform_%s:" % name)
    lines.append("")

    _title = "Platform ``%s``" % name
    lines.append(_title)
    lines.append("=" * len(_title))

    p = PlatformFactory.newPlatform(name)
    lines.append(p.description)
    lines.append("""
For more detailed information please visit `vendor site <%s>`_.""" %
                 p.vendor_url)
    lines.append("""
.. contents::""")

    #
    # Packages
    #
    _packages_content = generate_packages(name, p.packages.keys(),
                                          p.is_embedded())
    if _packages_content:
        lines.append(_packages_content)

    #
    # Frameworks
    #
    _frameworks_lines = []
    for framework in API_FRAMEWORKS:
        if not is_compat_platform_and_framework(name, framework['name']):
            continue
        _frameworks_lines.append("""
    * - :ref:`framework_{name}`
      - {description}""".format(**framework))

    if _frameworks_lines:
        lines.append("""
Frameworks
----------
.. list-table::
    :header-rows:  1

    * - Name
      - Description""")
        lines.extend(_frameworks_lines)

    #
    # Boards
    #
    vendors = {}
    for board in BOARDS:
        vendor = board['vendor']
        if name in board['platform']:
            if vendor in vendors:
                vendors[vendor].append(board)
            else:
                vendors[vendor] = [board]

    if vendors:
        lines.append("""
Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/boards>`_
    * For more detailed ``board`` information please scroll tables below by
      horizontal.
""")

    for vendor, boards in sorted(vendors.iteritems()):
        lines.append(str(vendor))
        lines.append("~" * len(vendor))
        lines.append(generate_boards(boards))

    return "\n".join(lines)


def update_platform_docs():
    for manifest in PLATFORM_MANIFESTS:
        name = manifest['name']
        platforms_dir = join(
            dirname(realpath(__file__)), "..", "docs", "platforms")
        rst_path = join(platforms_dir, "%s.rst" % name)
        with open(rst_path, "w") as f:
            f.write(generate_platform(name))
            if isfile(join(platforms_dir, "%s_extra.rst" % name)):
                f.write("\n.. include:: %s_extra.rst\n" % name)


def generate_framework(type_, data):
    print "Processing framework: %s" % type_
    lines = []

    lines.append(
        """..  Copyright 2014-present PlatformIO <contact@platformio.org>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
""")

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

    _found_platform = False
    for manifest in PLATFORM_MANIFESTS:
        if not is_compat_platform_and_framework(manifest['name'], type_):
            continue
        _found_platform = True
        p = PlatformFactory.newPlatform(manifest['name'])
        lines.append("""
    * - :ref:`platform_{type_}`
      - {description}""".format(
            type_=manifest['name'], description=p.description))
    if not _found_platform:
        del lines[-1]

    lines.append("""
Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/boards>`_
    * For more detailed ``board`` information please scroll tables below by horizontal.
""")

    vendors = {}
    for data in BOARDS:
        frameworks = data['frameworks']
        vendor = data['vendor']
        if type_ in frameworks:
            if vendor in vendors:
                vendors[vendor].append(data)
            else:
                vendors[vendor] = [data]
    for vendor, boards in sorted(vendors.iteritems()):
        lines.append(str(vendor))
        lines.append("~" * len(vendor))
        lines.append(generate_boards(boards))
    return "\n".join(lines)


def update_framework_docs():
    for framework in API_FRAMEWORKS:
        name = framework['name']
        frameworks_dir = join(
            dirname(realpath(__file__)), "..", "docs", "frameworks")
        rst_path = join(frameworks_dir, "%s.rst" % name)
        with open(rst_path, "w") as f:
            f.write(generate_framework(name, framework))
            if isfile(join(frameworks_dir, "%s_extra.rst" % name)):
                f.write("\n.. include:: %s_extra.rst\n" % name)


def update_create_platform_doc():
    lines = []
    lines.append(""".. _platform_creating_packages:

Packages
--------

*PlatformIO* has pre-built packages for the most popular operation systems:
*Mac OS*, *Linux (+ARM)* and *Windows*.

.. list-table::
    :header-rows:  1

    * - Name
      - Contents""")
    for name, items in sorted(API_PACKAGES.iteritems()):
        contitems = ["`{name} <{url}>`_".format(**item) for item in items]
        lines.append("""
    * - ``{name}``
      - {contents}""".format(
            name=name, contents=", ".join(contitems)))

    with open(
            join(util.get_source_dir(), "..", "docs", "platforms",
                 "creating_platform.rst"), "r+") as fp:
        content = fp.read()
        fp.seek(0, 0)
        fp.write(content[:content.index(".. _platform_creating_packages:")] +
                 "\n".join(lines) + "\n\n" + content[content.index(
                     ".. _platform_creating_manifest_file:"):])


def update_embedded_boards():
    lines = []

    lines.append(
        """..  Copyright 2014-present PlatformIO <contact@platformio.org>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
""")

    lines.append(".. _embedded_boards:")
    lines.append("")

    lines.append("Embedded Boards")
    lines.append("===============")

    lines.append("""
Rapid Embedded Development, Continuous and IDE integration in a few
steps with PlatformIO thanks to built-in project generator for the most
popular embedded boards and IDE.

* You can list pre-configured boards using :ref:`cmd_boards` command or
  `PlatformIO Boards Explorer <http://platformio.org/boards>`_
* For more detailed ``board`` information please scroll tables below by
  horizontal.
""")

    lines.append(".. contents::")
    lines.append("")

    vendors = {}
    for data in BOARDS:
        vendor = data['vendor']
        if vendor in vendors:
            vendors[vendor].append(data)
        else:
            vendors[vendor] = [data]

    for vendor, boards in sorted(vendors.iteritems()):
        lines.append(str(vendor))
        lines.append("~" * len(vendor))
        lines.append(generate_boards(boards))

    emboards_rst = join(
        dirname(realpath(__file__)), "..", "docs", "platforms",
        "embedded_boards.rst")
    with open(emboards_rst, "w") as f:
        f.write("\n".join(lines))


def main():
    update_create_platform_doc()
    update_platform_docs()
    update_framework_docs()
    update_embedded_boards()


if __name__ == "__main__":
    sys_exit(main())
