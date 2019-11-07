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
from os.path import dirname, isdir, isfile, join, realpath
from sys import exit as sys_exit
from sys import path

path.append("..")

import click

from platformio import fs, util
from platformio.managers.platform import PlatformFactory, PlatformManager

try:
    from urlparse import ParseResult, urlparse, urlunparse
except ImportError:
    from urllib.parse import ParseResult, urlparse, urlunparse

RST_COPYRIGHT = """..  Copyright (c) 2014-present PlatformIO <contact@platformio.org>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

API_PACKAGES = util.get_api_result("/packages")
API_FRAMEWORKS = util.get_api_result("/frameworks")
BOARDS = PlatformManager().get_installed_boards()
PLATFORM_MANIFESTS = PlatformManager().get_installed()
DOCS_ROOT_DIR = realpath(join(dirname(realpath(__file__)), "..", "docs"))


def is_compat_platform_and_framework(platform, framework):
    p = PlatformFactory.newPlatform(platform)
    return framework in (p.frameworks or {}).keys()


def campaign_url(url, source="platformio", medium="docs"):
    data = urlparse(url)
    query = data.query
    if query:
        query += "&"
    query += "utm_source=%s&utm_medium=%s" % (source, medium)
    return urlunparse(
        ParseResult(data.scheme, data.netloc, data.path, data.params, query,
                    data.fragment))


def generate_boards_table(boards, skip_columns=None):
    columns = [
        ("Name", ":ref:`board_{platform}_{id}`"),
        ("Platform", ":ref:`platform_{platform}`"),
        ("Debug", "{debug}"),
        ("MCU", "{mcu}"),
        ("Frequency", "{f_cpu}MHz"),
        ("Flash", "{rom}"),
        ("RAM", "{ram}"),
    ]
    lines = []
    lines.append("""
.. list-table::
    :header-rows:  1
""")

    # add header
    for (name, template) in columns:
        if skip_columns and name in skip_columns:
            continue
        prefix = "    * - " if name == "Name" else "      - "
        lines.append(prefix + name)

    for data in sorted(boards, key=lambda item: item['name']):
        has_onboard_debug = (data['debug'] and any(
            t.get("onboard") for (_, t) in data['debug']['tools'].items()))
        debug = "No"
        if has_onboard_debug:
            debug = "On-board"
        elif data['debug']:
            debug = "External"

        variables = dict(id=data['id'],
                         name=data['name'],
                         platform=data['platform'],
                         debug=debug,
                         mcu=data['mcu'].upper(),
                         f_cpu=int(data['fcpu'] / 1000000.0),
                         ram=fs.format_filesize(data['ram']),
                         rom=fs.format_filesize(data['rom']))

        for (name, template) in columns:
            if skip_columns and name in skip_columns:
                continue
            prefix = "    * - " if name == "Name" else "      - "
            lines.append(prefix + template.format(**variables))

    if lines:
        lines.append("")

    return lines


def generate_frameworks_contents(frameworks):
    if not frameworks:
        return []
    lines = []
    lines.append("""
Frameworks
----------
.. list-table::
    :header-rows:  1

    * - Name
      - Description""")
    known = set()
    for framework in API_FRAMEWORKS:
        known.add(framework['name'])
        if framework['name'] not in frameworks:
            continue
        lines.append("""
    * - :ref:`framework_{name}`
      - {description}""".format(**framework))
    if set(frameworks) - known:
        click.secho("Unknown frameworks %s " % (
        set(frameworks) - known), fg="red")
    return lines


def generate_platforms_contents(platforms):
    if not platforms:
        return []
    lines = []
    lines.append("""
Platforms
---------
.. list-table::
    :header-rows:  1

    * - Name
      - Description""")

    for name in sorted(platforms):
        p = PlatformFactory.newPlatform(name)
        lines.append("""
    * - :ref:`platform_{name}`
      - {description}""".format(name=p.name, description=p.description))
    return lines


def generate_debug_contents(boards, skip_board_columns=None, extra_rst=None):
    if not skip_board_columns:
        skip_board_columns = []
    skip_board_columns.append("Debug")
    lines = []
    onboard_debug = [
        b for b in boards if b['debug'] and any(
            t.get("onboard") for (_, t) in b['debug']['tools'].items())
    ]
    external_debug = [
        b for b in boards if b['debug'] and b not in onboard_debug
    ]
    if not onboard_debug and not external_debug:
        return lines

    lines.append("""
Debugging
---------

:ref:`piodebug` - "1-click" solution for debugging with a zero configuration.

.. contents::
    :local:
""")
    if extra_rst:
        lines.append(".. include:: %s" % extra_rst)

    lines.append("""
Tools & Debug Probes
~~~~~~~~~~~~~~~~~~~~

Supported debugging tools are listed in "Debug" column. For more detailed
information, please scroll table by horizontal.
You can switch between debugging :ref:`debugging_tools` using
:ref:`projectconf_debug_tool` option in :ref:`projectconf`.

.. warning::
    You will need to install debug tool drivers depending on your system.
    Please click on compatible debug tool below for the further instructions.
""")

    if onboard_debug:
        lines.append("""
On-Board Debug Tools
^^^^^^^^^^^^^^^^^^^^

Boards listed below have on-board debug probe and **ARE READY** for debugging!
You do not need to use/buy external debug probe.
""")
        lines.extend(
            generate_boards_table(onboard_debug,
                                  skip_columns=skip_board_columns))
    if external_debug:
        lines.append("""
External Debug Tools
^^^^^^^^^^^^^^^^^^^^

Boards listed below are compatible with :ref:`piodebug` but **DEPEND ON**
external debug probe. They **ARE NOT READY** for debugging.
Please click on board name for the further details.
""")
        lines.extend(
            generate_boards_table(external_debug,
                                  skip_columns=skip_board_columns))
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
        if name not in API_PACKAGES:
            click.secho("Unknown package `%s`" % name, fg="red")
            lines.append("""
    * - {name}
      -
                """.format(name=name))
        else:
            lines.append("""
    * - `{name} <{url}>`__
      - {description}""".format(name=name,
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


def generate_platform(name, rst_dir):
    print("Processing platform: %s" % name)

    compatible_boards = [
        board for board in BOARDS if name == board['platform']
    ]

    lines = []

    lines.append(RST_COPYRIGHT)
    p = PlatformFactory.newPlatform(name)
    assert p.repository_url.endswith(".git")
    github_url = p.repository_url[:-4]

    lines.append(".. _platform_%s:" % p.name)
    lines.append("")

    lines.append(p.title)
    lines.append("=" * len(p.title))
    lines.append("")
    lines.append(":Configuration:")
    lines.append("  :ref:`projectconf_env_platform` = ``%s``" % p.name)
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
    if isfile(join(rst_dir, "%s_extra.rst" % name)):
        lines.append(".. include:: %s_extra.rst" % p.name)

    #
    # Examples
    #
    lines.append("""
Examples
--------

Examples are listed from `%s development platform repository <%s>`_:
""" % (p.title, campaign_url("%s/tree/master/examples" % github_url)))
    examples_dir = join(p.get_dir(), "examples")
    if isdir(examples_dir):
        for eitem in os.listdir(examples_dir):
            example_dir = join(examples_dir, eitem)
            if not isdir(example_dir) or not os.listdir(example_dir):
                continue
            url = "%s/tree/master/examples/%s" % (github_url, eitem)
            lines.append("* `%s <%s>`_" % (eitem, campaign_url(url)))

    #
    # Debugging
    #
    if compatible_boards:
        lines.extend(
            generate_debug_contents(
                compatible_boards,
                skip_board_columns=["Platform"],
                extra_rst="%s_debug.rst" %
                name if isfile(join(rst_dir, "%s_debug.rst" %
                                    name)) else None))

    #
    # Development version of dev/platform
    #
    lines.append("""
Stable and upstream versions
----------------------------

You can switch between `stable releases <{github_url}/releases>`__
of {title} development platform and the latest upstream version using
:ref:`projectconf_env_platform` option in :ref:`projectconf` as described below.

Stable
~~~~~~

.. code-block:: ini

    ; Latest stable version
    [env:latest_stable]
    platform = {name}
    board = ...

    ; Custom stable version
    [env:custom_stable]
    platform = {name}@x.y.z
    board = ...

Upstream
~~~~~~~~

.. code-block:: ini

    [env:upstream_develop]
    platform = {github_url}.git
    board = ...
""".format(name=p.name, title=p.title, github_url=github_url))

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
    compatible_frameworks = []
    for framework in API_FRAMEWORKS:
        if is_compat_platform_and_framework(name, framework['name']):
            compatible_frameworks.append(framework['name'])
    lines.extend(generate_frameworks_contents(compatible_frameworks))

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
            lines.extend(
                generate_boards_table(boards, skip_columns=["Platform"]))

    return "\n".join(lines)


def update_platform_docs():
    for manifest in PLATFORM_MANIFESTS:
        name = manifest['name']
        platforms_dir = join(DOCS_ROOT_DIR, "platforms")
        rst_path = join(platforms_dir, "%s.rst" % name)
        with open(rst_path, "w") as f:
            f.write(generate_platform(name, platforms_dir))


def generate_framework(type_, data, rst_dir=None):
    print("Processing framework: %s" % type_)

    compatible_platforms = [
        m for m in PLATFORM_MANIFESTS
        if is_compat_platform_and_framework(m['name'], type_)
    ]
    compatible_boards = [
        board for board in BOARDS if type_ in board['frameworks']
    ]

    lines = []

    lines.append(RST_COPYRIGHT)
    lines.append(".. _framework_%s:" % type_)
    lines.append("")

    lines.append(data['title'])
    lines.append("=" * len(data['title']))
    lines.append("")
    lines.append(":Configuration:")
    lines.append("  :ref:`projectconf_env_framework` = ``%s``" % type_)
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
    if isfile(join(rst_dir, "%s_extra.rst" % type_)):
        lines.append(".. include:: %s_extra.rst" % type_)

    #
    # Debugging
    #
    if compatible_boards:
        lines.extend(
            generate_debug_contents(
                compatible_boards,
                extra_rst="%s_debug.rst" %
                type_ if isfile(join(rst_dir, "%s_debug.rst" %
                                     type_)) else None))

    if compatible_platforms:
        # examples
        lines.append("""
Examples
--------
""")
        for manifest in compatible_platforms:
            p = PlatformFactory.newPlatform(manifest['name'])
            lines.append("* `%s for %s <%s>`_" %
                         (data['title'], manifest['title'],
                          campaign_url("%s/tree/master/examples" %
                                       p.repository_url[:-4])))

        # Platforms
        lines.extend(
            generate_platforms_contents(
                [manifest['name'] for manifest in compatible_platforms]))

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
            lines.extend(generate_boards_table(boards))
    return "\n".join(lines)


def update_framework_docs():
    for framework in API_FRAMEWORKS:
        name = framework['name']
        frameworks_dir = join(DOCS_ROOT_DIR, "frameworks")
        rst_path = join(frameworks_dir, "%s.rst" % name)
        with open(rst_path, "w") as f:
            f.write(generate_framework(name, framework, frameworks_dir))


def update_boards():
    lines = []

    lines.append(RST_COPYRIGHT)
    lines.append(".. _boards:")
    lines.append("")

    lines.append("Boards")
    lines.append("======")

    lines.append("""
Rapid Embedded Development, Continuous and IDE integration in a few
steps with PlatformIO thanks to built-in project generator for the most
popular embedded boards and IDE.

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <https://platformio.org/boards>`_
    * For more detailed ``board`` information please scroll tables below by horizontal.
""")

    platforms = {}
    for data in BOARDS:
        platform = data['platform']
        if platform in platforms:
            platforms[platform].append(data)
        else:
            platforms[platform] = [data]

    for platform, boards in sorted(platforms.items()):
        p = PlatformFactory.newPlatform(platform)
        lines.append(p.title)
        lines.append("-" * len(p.title))
        lines.append("""
.. toctree::
    :maxdepth: 1
        """)
        for board in sorted(boards, key=lambda item: item['name']):
            lines.append("    %s/%s" % (platform, board["id"]))
        lines.append("")

    emboards_rst = join(DOCS_ROOT_DIR, "boards", "index.rst")
    with open(emboards_rst, "w") as f:
        f.write("\n".join(lines))

    # individual board page
    for data in BOARDS:
        # if data['id'] != "m5stack-core-esp32":
        #     continue
        rst_path = join(DOCS_ROOT_DIR, "boards", data["platform"],
                        "%s.rst" % data["id"])
        if not isdir(dirname(rst_path)):
            os.makedirs(dirname(rst_path))
        update_embedded_board(rst_path, data)


def update_embedded_board(rst_path, board):
    platform = PlatformFactory.newPlatform(board['platform'])
    board_config = platform.board_config(board['id'])

    board_manifest_url = platform.repository_url
    assert board_manifest_url
    if board_manifest_url.endswith(".git"):
        board_manifest_url = board_manifest_url[:-4]
    board_manifest_url += "/blob/master/boards/%s.json" % board['id']

    variables = dict(id=board['id'],
                     name=board['name'],
                     platform=board['platform'],
                     platform_description=platform.description,
                     url=campaign_url(board['url']),
                     mcu=board_config.get("build", {}).get("mcu", ""),
                     mcu_upper=board['mcu'].upper(),
                     f_cpu=board['fcpu'],
                     f_cpu_mhz=int(int(board['fcpu']) / 1000000),
                     ram=fs.format_filesize(board['ram']),
                     rom=fs.format_filesize(board['rom']),
                     vendor=board['vendor'],
                     board_manifest_url=board_manifest_url,
                     upload_protocol=board_config.get("upload.protocol", ""))

    lines = [RST_COPYRIGHT]
    lines.append(".. _board_{platform}_{id}:".format(**variables))
    lines.append("")
    lines.append(board['name'])
    lines.append("=" * len(board['name']))
    lines.append("""
.. contents::

Hardware
--------

Platform :ref:`platform_{platform}`: {platform_description}

.. list-table::

  * - **Microcontroller**
    - {mcu_upper}
  * - **Frequency**
    - {f_cpu_mhz:d}MHz
  * - **Flash**
    - {rom}
  * - **RAM**
    - {ram}
  * - **Vendor**
    - `{vendor} <{url}>`__
""".format(**variables))

    #
    # Configuration
    #
    lines.append("""
Configuration
-------------

Please use ``{id}`` ID for :ref:`projectconf_env_board` option in :ref:`projectconf`:

.. code-block:: ini

  [env:{id}]
  platform = {platform}
  board = {id}

You can override default {name} settings per build environment using
``board_***`` option, where ``***`` is a JSON object path from
board manifest `{id}.json <{board_manifest_url}>`_. For example,
``board_build.mcu``, ``board_build.f_cpu``, etc.

.. code-block:: ini

  [env:{id}]
  platform = {platform}
  board = {id}

  ; change microcontroller
  board_build.mcu = {mcu}

  ; change MCU frequency
  board_build.f_cpu = {f_cpu}L
""".format(**variables))

    #
    # Uploading
    #
    upload_protocols = board_config.get("upload.protocols", [])
    if len(upload_protocols) > 1:
        lines.append("""
Uploading
---------
%s supports the next uploading protocols:
""" % board['name'])
        for protocol in sorted(upload_protocols):
            lines.append("* ``%s``" % protocol)
        lines.append("""
Default protocol is ``%s``""" % variables['upload_protocol'])
        lines.append("""
You can change upload protocol using :ref:`projectconf_upload_protocol` option:

.. code-block:: ini

  [env:{id}]
  platform = {platform}
  board = {id}

  upload_protocol = {upload_protocol}
""".format(**variables))

    #
    # Debugging
    #
    lines.append("Debugging")
    lines.append("---------")
    if not board['debug']:
        lines.append(
            ":ref:`piodebug` currently does not support {name} board.".format(
                **variables))
    else:
        default_debug_tool = board_config.get_debug_tool_name()
        has_onboard_debug = any(
            t.get("onboard") for (_, t) in board['debug']['tools'].items())
        lines.append("""
:ref:`piodebug` - "1-click" solution for debugging with a zero configuration.

.. warning::
    You will need to install debug tool drivers depending on your system.
    Please click on compatible debug tool below for the further
    instructions and configuration information.

You can switch between debugging :ref:`debugging_tools` using
:ref:`projectconf_debug_tool` option in :ref:`projectconf`.
""")
        if has_onboard_debug:
            lines.append(
                "{name} has on-board debug probe and **IS READY** for "
                "debugging. You don't need to use/buy external debug probe.".
                format(**variables))
        else:
            lines.append(
                "{name} does not have on-board debug probe and **IS NOT "
                "READY** for debugging. You will need to use/buy one of "
                "external probe listed below.".format(**variables))
        lines.append("""
.. list-table::
  :header-rows:  1

  * - Compatible Tools
    - On-board
    - Default""")
        for (tool_name, tool_data) in sorted(board['debug']['tools'].items()):
            lines.append("""  * - :ref:`debugging_tool_{name}`
    - {onboard}
    - {default}""".format(
                name=tool_name,
                onboard="Yes" if tool_data.get("onboard") else "",
                default="Yes" if tool_name == default_debug_tool else ""))

    if board['frameworks']:
        lines.extend(generate_frameworks_contents(board['frameworks']))

    with open(rst_path, "w") as f:
        f.write("\n".join(lines))


def update_debugging():
    tool_to_platforms = {}
    tool_to_boards = {}
    vendors = {}
    platforms = []
    frameworks = []
    for data in BOARDS:
        if not data['debug']:
            continue

        for tool in data['debug']['tools']:
            tool = str(tool)
            if tool not in tool_to_platforms:
                tool_to_platforms[tool] = []
            tool_to_platforms[tool].append(data['platform'])
            if tool not in tool_to_boards:
                tool_to_boards[tool] = []
            tool_to_boards[tool].append(data['id'])

        platforms.append(data['platform'])
        frameworks.extend(data['frameworks'])
        vendor = data['vendor']
        if vendor in vendors:
            vendors[vendor].append(data)
        else:
            vendors[vendor] = [data]

    platforms = sorted(set(platforms))
    frameworks = sorted(set(frameworks))

    lines = [".. _debugging_platforms:"]
    lines.extend(generate_platforms_contents(platforms))
    lines.extend(generate_frameworks_contents(frameworks))

    # Boards
    lines.append("""
Boards
------

.. note::
    For more detailed ``board`` information please scroll tables below by horizontal.
""")
    for vendor, boards in sorted(vendors.items()):
        lines.append(str(vendor))
        lines.append("~" * len(vendor))
        lines.extend(generate_boards_table(boards))

    # save
    with open(join(fs.get_source_dir(), "..", "docs", "plus", "debugging.rst"),
              "r+") as fp:
        content = fp.read()
        fp.seek(0)
        fp.truncate()
        fp.write(content[:content.index(".. _debugging_platforms:")] +
                 "\n".join(lines))

    # Debug tools
    for tool, platforms in tool_to_platforms.items():
        tool_path = join(DOCS_ROOT_DIR, "plus", "debug-tools", "%s.rst" % tool)
        if not isfile(tool_path):
            click.secho("Unknown debug tool `%s`" % tool, fg="red")
            continue
        platforms = sorted(set(platforms))

        lines = [".. begin_platforms"]
        lines.extend(generate_platforms_contents(platforms))
        tool_frameworks = []
        for platform in platforms:
            for framework in frameworks:
                if is_compat_platform_and_framework(platform, framework):
                    tool_frameworks.append(framework)
        lines.extend(generate_frameworks_contents(tool_frameworks))

        lines.append("""
Boards
------

.. note::
    For more detailed ``board`` information please scroll tables below by horizontal.
""")
        lines.extend(
            generate_boards_table(
                [b for b in BOARDS if b['id'] in tool_to_boards[tool]],
                skip_columns=None))

        with open(tool_path, "r+") as fp:
            content = fp.read()
            fp.seek(0)
            fp.truncate()
            fp.write(content[:content.index(".. begin_platforms")] +
                     "\n".join(lines))


def update_project_examples():
    platform_readme_tpl = """
# {title}: development platform for [PlatformIO](https://platformio.org)

{description}

* [Home](https://platformio.org/platforms/{name}) (home page in PlatformIO Registry)
* [Documentation](https://docs.platformio.org/page/platforms/{name}.html) (advanced usage, packages, boards, frameworks, etc.)

# Examples

{examples}
"""
    framework_readme_tpl = """
# {title}: framework for [PlatformIO](https://platformio.org)

{description}

* [Home](https://platformio.org/frameworks/{name}) (home page in PlatformIO Registry)
* [Documentation](https://docs.platformio.org/page/frameworks/{name}.html)

# Examples

{examples}
"""

    project_examples_dir = join(fs.get_source_dir(), "..", "examples")
    framework_examples_md_lines = {}
    embedded = []
    desktop = []

    for manifest in PLATFORM_MANIFESTS:
        p = PlatformFactory.newPlatform(manifest['name'])
        github_url = p.repository_url[:-4]

        # Platform README
        platform_examples_dir = join(p.get_dir(), "examples")
        examples_md_lines = []
        if isdir(platform_examples_dir):
            for item in os.listdir(platform_examples_dir):
                example_dir = join(platform_examples_dir, item)
                if not isdir(example_dir) or not os.listdir(example_dir):
                    continue
                url = "%s/tree/master/examples/%s" % (github_url, item)
                examples_md_lines.append("* [%s](%s)" % (item, url))

        readme_dir = join(project_examples_dir, "platforms", p.name)
        if not isdir(readme_dir):
            os.makedirs(readme_dir)
        with open(join(readme_dir, "README.md"), "w") as fp:
            fp.write(
                platform_readme_tpl.format(
                    name=p.name,
                    title=p.title,
                    description=p.description,
                    examples="\n".join(examples_md_lines)))

        # Framework README
        for framework in API_FRAMEWORKS:
            if not is_compat_platform_and_framework(p.name, framework['name']):
                continue
            if framework['name'] not in framework_examples_md_lines:
                framework_examples_md_lines[framework['name']] = []
            lines = []
            lines.append("- [%s](%s)" % (p.title, github_url))
            lines.extend("  %s" % l for l in examples_md_lines)
            lines.append("")
            framework_examples_md_lines[framework['name']].extend(lines)

        # Root README
        line = "* [%s](%s)" % (p.title, "%s/tree/master/examples" % github_url)
        if p.is_embedded():
            embedded.append(line)
        else:
            desktop.append(line)

    # Frameworks
    frameworks = []
    for framework in API_FRAMEWORKS:
        readme_dir = join(project_examples_dir, "frameworks",
                          framework['name'])
        if not isdir(readme_dir):
            os.makedirs(readme_dir)
        with open(join(readme_dir, "README.md"), "w") as fp:
            fp.write(
                framework_readme_tpl.format(
                    name=framework['name'],
                    title=framework['title'],
                    description=framework['description'],
                    examples="\n".join(
                        framework_examples_md_lines[framework['name']])))
        url = campaign_url(
            "https://docs.platformio.org/en/latest/frameworks/%s.html#examples"
            % framework['name'],
            source="github",
            medium="examples")
        frameworks.append("* [%s](%s)" % (framework['title'], url))

    with open(join(project_examples_dir, "README.md"), "w") as fp:
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
    update_platform_docs()
    update_framework_docs()
    update_boards()
    update_debugging()
    update_project_examples()


if __name__ == "__main__":
    sys_exit(main())
