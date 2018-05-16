# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
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

import os
import urlparse
from os.path import dirname, isdir, isfile, join, realpath
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


def campaign_url(url, source="platformio", medium="docs"):
    data = urlparse.urlparse(url)
    query = data.query
    if query:
        query += "&"
    query += "utm_source=%s&utm_medium=%s" % (source, medium)
    return urlparse.urlunparse(
        urlparse.ParseResult(data.scheme, data.netloc, data.path, data.params,
                             query, data.fragment))


def generate_boards(boards, extend_debug=False, skip_columns=None):
    columns = [
        ("ID", "``{id}``"),
        ("Name", "`{name} <{url}>`_"),
        ("Platform", ":ref:`{platform_title} <platform_{platform}>`"),
        ("Debug", "{debug}"),
        ("MCU", "{mcu}"),
        ("Frequency", "{f_cpu:d}MHz"),
        ("Flash", "{rom}"),
        ("RAM", "{ram}"),
    ]
    platforms = {m['name']: m['title'] for m in PLATFORM_MANIFESTS}
    lines = []

    lines.append("""
.. list-table::
    :header-rows:  1
""")

    # add header
    for (name, template) in columns:
        if skip_columns and name in skip_columns:
            continue
        prefix = "    * - " if name == "ID" else "      - "
        lines.append(prefix + name)

    for data in sorted(boards, key=lambda item: item['id']):
        debug = [":ref:`Yes <piodebug>`" if data['debug'] else "No"]
        if extend_debug and data['debug']:
            debug_onboard = []
            debug_external = []
            for name, options in data['debug']['tools'].items():
                attrs = []
                if options.get("default"):
                    attrs.append("default")
                if options.get("onboard"):
                    attrs.append("on-board")
                tool = ":ref:`debugging_tool_%s`" % name
                if attrs:
                    tool = "%s (%s)" % (tool, ", ".join(attrs))
                if options.get("onboard"):
                    debug_onboard.append(tool)
                else:
                    debug_external.append(tool)
            debug = sorted(debug_onboard) + sorted(debug_external)

        variables = dict(
            id=data['id'],
            name=data['name'],
            platform=data['platform'],
            platform_title=platforms[data['platform']],
            debug=", ".join(debug),
            url=campaign_url(data['url']),
            mcu=data['mcu'].upper(),
            f_cpu=int(data['fcpu']) / 1000000,
            ram=util.format_filesize(data['ram']),
            rom=util.format_filesize(data['rom']))

        for (name, template) in columns:
            if skip_columns and name in skip_columns:
                continue
            prefix = "    * - " if name == "ID" else "      - "
            lines.append(prefix + template.format(**variables))

    if lines:
        lines.append("")

    return lines


def generate_debug_boards(boards, skip_columns=None):
    lines = []
    onboard_debug = [
        b for b in boards if b['debug'] and any(
            t.get("onboard") for (_, t) in b['debug']['tools'].items())
    ]
    external_debug = [
        b for b in boards if b['debug'] and b not in onboard_debug
    ]
    if onboard_debug or external_debug:
        lines.append("""
Debugging
---------

:ref:`piodebug` - "1-click" solution for debugging with a zero configuration.

Supported debugging tools are listed in "Debug" column. For more detailed
information, please scroll table by horizontal.
You can switch between debugging :ref:`debugging_tools` using
:ref:`projectconf_debug_tool` options.
""")
    if onboard_debug:
        lines.append("""
On-Board tools
~~~~~~~~~~~~~~

Boards listed below have on-board debugging tools and **ARE READY** for debugging!
You do not need to use/buy external debugger.
""")
        lines.extend(
            generate_boards(
                onboard_debug, extend_debug=True, skip_columns=skip_columns))
    if external_debug:
        lines.append("""
External tools
~~~~~~~~~~~~~~

Boards listed below are compatible with :ref:`piodebug` but depend on external
debugging tools. See "Debug" column for compatible debugging tools.
""")
        lines.extend(
            generate_boards(
                external_debug, extend_debug=True, skip_columns=skip_columns))
    return lines


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
      - Description""")
    for name in sorted(packagenames):
        assert name in API_PACKAGES, name
        lines.append("""
    * - `{name} <{url}>`__
      - {description}""".format(
            name=name,
            url=campaign_url(API_PACKAGES[name]['url']),
            description=API_PACKAGES[name]['description']))

    if is_embedded:
        lines.append("""
.. warning::
    **Linux Users**:

        * Install "udev" rules :ref:`faq_udev_rules`
        * Raspberry Pi users, please read this article
          `Enable serial port on Raspberry Pi <https://hallard.me/enable-serial-port-on-raspberry-pi/>`__.
""")

        if platform == "teensy":
            lines.append("""
    **Windows Users:**

        Teensy programming uses only Windows built-in HID
        drivers. When Teensy is programmed to act as a USB Serial device,
        Windows XP, Vista, 7 and 8 require `this serial driver
        <http://www.pjrc.com/teensy/serial_install.exe>`_
        is needed to access the COM port your program uses. No special driver
        installation is necessary on Windows 10.
""")
        else:
            lines.append("""
    **Windows Users:**

        Please check that you have a correctly installed USB driver from board
        manufacturer
""")

    return "\n".join(lines)


def generate_platform(name, has_extra=False):
    print "Processing platform: %s" % name

    compatible_boards = [
        board for board in BOARDS if name in board['platform']
    ]

    lines = []

    lines.append(
        """..  Copyright (c) 2014-present PlatformIO <contact@platformio.org>
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
    p = PlatformFactory.newPlatform(name)

    lines.append(".. _platform_%s:" % p.name)
    lines.append("")

    lines.append(p.title)
    lines.append("=" * len(p.title))
    lines.append(":ref:`projectconf_env_platform` = ``%s``" % p.name)
    lines.append("")
    lines.append(p.description)
    lines.append("""
For more detailed information please visit `vendor site <%s>`_.""" %
                 campaign_url(p.vendor_url))
    lines.append("""
.. contents:: Contents
    :local:
    :depth: 1
""")

    #
    # Extra
    #
    if has_extra:
        lines.append(".. include:: %s_extra.rst" % p.name)

    #
    # Examples
    #
    lines.append("""
Examples
--------

Examples are listed from `%s development platform repository <%s>`_:
""" % (p.title,
       campaign_url(
           "https://github.com/platformio/platform-%s/tree/develop/examples" %
           p.name)))
    examples_dir = join(p.get_dir(), "examples")
    if isdir(examples_dir):
        for eitem in os.listdir(examples_dir):
            if not isdir(join(examples_dir, eitem)):
                continue
            url = ("https://github.com/platformio/platform-%s"
                   "/tree/develop/examples/%s" % (p.name, eitem))
            lines.append("* `%s <%s>`_" % (eitem, campaign_url(url)))

    #
    # Debugging
    #
    if compatible_boards:
        lines.extend(
            generate_debug_boards(
                compatible_boards, skip_columns=["Platform"]))

    #
    # Development version of dev/platform
    #
    lines.append("""
Stable and upstream versions
----------------------------

You can switch between `stable releases <https://github.com/platformio/platform-{name}/releases>`__
of {title} development platform and the latest upstream version using
:ref:`projectconf_env_platform` option in :ref:`projectconf` as described below:

.. code-block:: ini

    ; Custom stable version
    [env:stable]
    platform ={name}@x.y.z
    board = ...
    ...

    ; The latest upstream/development version
    [env:upstream]
    platform = https://github.com/platformio/platform-{name}.git
    board = ...
    ...
""".format(name=p.name, title=p.title))

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
    if compatible_boards:
        vendors = {}
        for board in compatible_boards:
            if board['vendor'] not in vendors:
                vendors[board['vendor']] = []
            vendors[board['vendor']].append(board)

        lines.append("""
Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <https://platformio.org/boards>`_
    * For more detailed ``board`` information please scroll tables below by
      horizontal.
""")

        for vendor, boards in sorted(vendors.items()):
            lines.append(str(vendor))
            lines.append("~" * len(vendor))
            lines.extend(generate_boards(boards, skip_columns=["Platform"]))

    return "\n".join(lines)


def update_platform_docs():
    for manifest in PLATFORM_MANIFESTS:
        name = manifest['name']
        platforms_dir = join(
            dirname(realpath(__file__)), "..", "docs", "platforms")
        rst_path = join(platforms_dir, "%s.rst" % name)
        with open(rst_path, "w") as f:
            f.write(
                generate_platform(name,
                                  isfile(
                                      join(platforms_dir,
                                           "%s_extra.rst" % name))))


def generate_framework(type_, data, has_extra=False):
    print "Processing framework: %s" % type_

    compatible_platforms = [
        m for m in PLATFORM_MANIFESTS
        if is_compat_platform_and_framework(m['name'], type_)
    ]
    compatible_boards = [
        board for board in BOARDS if type_ in board['frameworks']
    ]

    lines = []

    lines.append(
        """..  Copyright (c) 2014-present PlatformIO <contact@platformio.org>
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

    lines.append(data['title'])
    lines.append("=" * len(data['title']))
    lines.append(":ref:`projectconf_env_framework` = ``%s``" % type_)
    lines.append("")
    lines.append(data['description'])
    lines.append("""
For more detailed information please visit `vendor site <%s>`_.
""" % campaign_url(data['url']))

    lines.append("""
.. contents:: Contents
    :local:
    :depth: 1""")

    # Extra
    if has_extra:
        lines.append(".. include:: %s_extra.rst" % type_)

    #
    # Debugging
    #
    if compatible_boards:
        lines.extend(generate_debug_boards(compatible_boards))

    if compatible_platforms:
        # examples
        lines.append("""
Examples
--------
""")
        for manifest in compatible_platforms:
            lines.append("* `%s for %s <%s>`_" % (
                data['title'], manifest['title'],
                campaign_url(
                    "https://github.com/platformio/platform-%s/tree/develop/examples"
                    % manifest['name'])))

        # Platforms
        lines.append("""
Platforms
---------
.. list-table::
    :header-rows:  1

    * - Name
      - Description""")

        for manifest in compatible_platforms:
            p = PlatformFactory.newPlatform(manifest['name'])
            lines.append("""
    * - :ref:`platform_{type_}`
      - {description}""".format(
                type_=manifest['name'], description=p.description))

    #
    # Boards
    #
    if compatible_boards:
        vendors = {}
        for board in compatible_boards:
            if board['vendor'] not in vendors:
                vendors[board['vendor']] = []
            vendors[board['vendor']].append(board)
        lines.append("""
Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <https://platformio.org/boards>`_
    * For more detailed ``board`` information please scroll tables below by horizontal.
""")
        for vendor, boards in sorted(vendors.items()):
            lines.append(str(vendor))
            lines.append("~" * len(vendor))
            lines.extend(generate_boards(boards))
    return "\n".join(lines)


def update_framework_docs():
    for framework in API_FRAMEWORKS:
        name = framework['name']
        frameworks_dir = join(
            dirname(realpath(__file__)), "..", "docs", "frameworks")
        rst_path = join(frameworks_dir, "%s.rst" % name)
        with open(rst_path, "w") as f:
            f.write(
                generate_framework(name, framework,
                                   isfile(
                                       join(frameworks_dir,
                                            "%s_extra.rst" % name))))


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
      - Description""")
    for name, items in sorted(API_PACKAGES.iteritems()):
        lines.append("""
    * - `{name} <{url}>`__
      - {description}""".format(
            name=name,
            url=API_PACKAGES[name]['url'],
            description=API_PACKAGES[name]['description']))

    with open(
            join(util.get_source_dir(), "..", "docs", "platforms",
                 "creating_platform.rst"), "r+") as fp:
        content = fp.read()
        fp.seek(0)
        fp.truncate()
        fp.write(content[:content.index(".. _platform_creating_packages:")] +
                 "\n".join(lines) + "\n\n" + content[content.index(
                     ".. _platform_creating_manifest_file:"):])


def update_embedded_boards():
    lines = []

    lines.append(
        """..  Copyright (c) 2014-present PlatformIO <contact@platformio.org>
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

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <https://platformio.org/boards>`_
    * For more detailed ``board`` information please scroll tables below by horizontal.
""")

    lines.append("""
.. contents:: Vendors
    :local:
    """)

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
        lines.extend(generate_boards(boards))

    emboards_rst = join(
        dirname(realpath(__file__)), "..", "docs", "platforms",
        "embedded_boards.rst")
    with open(emboards_rst, "w") as f:
        f.write("\n".join(lines))


def update_debugging():
    vendors = {}
    platforms = []
    frameworks = []
    for data in BOARDS:
        if not data['debug']:
            continue
        platforms.append(data['platform'])
        frameworks.extend(data['frameworks'])
        vendor = data['vendor']
        if vendor in vendors:
            vendors[vendor].append(data)
        else:
            vendors[vendor] = [data]

    lines = []
    # Platforms
    lines.append(""".. _debugging_platforms:

Platforms
---------
.. list-table::
    :header-rows:  1

    * - Name
      - Description""")

    for manifest in PLATFORM_MANIFESTS:
        if manifest['name'] not in platforms:
            continue
        p = PlatformFactory.newPlatform(manifest['name'])
        lines.append("""
    * - :ref:`platform_{type_}`
      - {description}""".format(
            type_=manifest['name'], description=p.description))

    # Frameworks
    lines.append("""
Frameworks
----------
.. list-table::
    :header-rows:  1

    * - Name
      - Description""")
    for framework in API_FRAMEWORKS:
        if framework['name'] not in frameworks:
            continue
        lines.append("""
    * - :ref:`framework_{name}`
      - {description}""".format(**framework))

    # Boards
    lines.append("""
Boards
------

.. note::
    For more detailed ``board`` information please scroll tables below by horizontal.
""")
    for vendor, boards in sorted(vendors.iteritems()):
        lines.append(str(vendor))
        lines.append("~" * len(vendor))
        lines.extend(generate_boards(boards, extend_debug=True))

    with open(
            join(util.get_source_dir(), "..", "docs", "plus", "debugging.rst"),
            "r+") as fp:
        content = fp.read()
        fp.seek(0)
        fp.truncate()
        fp.write(content[:content.index(".. _debugging_platforms:")] +
                 "\n".join(lines))


def update_examples_readme():
    examples_dir = join(util.get_source_dir(), "..", "examples")

    # Platforms
    embedded = []
    desktop = []
    for manifest in PLATFORM_MANIFESTS:
        p = PlatformFactory.newPlatform(manifest['name'])
        url = campaign_url(
            "http://docs.platformio.org/en/latest/platforms/%s.html#examples" %
            p.name,
            source="github",
            medium="examples")
        line = "* [%s](%s)" % (p.title, url)
        if p.is_embedded():
            embedded.append(line)
        else:
            desktop.append(line)

    # Frameworks
    frameworks = []
    for framework in API_FRAMEWORKS:
        url = campaign_url(
            "http://docs.platformio.org/en/latest/frameworks/%s.html#examples"
            % framework['name'],
            source="github",
            medium="examples")
        frameworks.append("* [%s](%s)" % (framework['title'], url))

    with open(join(examples_dir, "README.md"), "w") as fp:
        fp.write("""# PlatformIO Project Examples

- [Development platforms](#development-platforms):
  - [Embedded](#embedded)
  - [Desktop](#desktop)
- [Frameworks](#frameworks)

## Development platforms

### Embedded

%s

### Desktop

%s

## Frameworks

%s
""" % ("\n".join(embedded), "\n".join(desktop), "\n".join(frameworks)))


def main():
    update_create_platform_doc()
    update_platform_docs()
    update_framework_docs()
    update_embedded_boards()
    update_debugging()
    update_examples_readme()


if __name__ == "__main__":
    sys_exit(main())
