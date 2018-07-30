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


def generate_debug_contents(boards, skip_board_columns=None, extra_rst=None):
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
Debug Tools
~~~~~~~~~~~

Supported debugging tools are listed in "Debug" column. For more detailed
information, please scroll table by horizontal.
You can switch between debugging :ref:`debugging_tools` using
:ref:`projectconf_debug_tool` options.

.. warning::
    You will need to install debug tool drivers depending on your system.
    Please click on compatible debug tool below for the further instructions.
""")

    if onboard_debug:
        lines.append("""
On-Board Debug Tools
^^^^^^^^^^^^^^^^^^^^

Boards listed below have on-board debug tool and **ARE READY** for debugging!
You do not need to use/buy external debug tool.
""")
        lines.extend(
            generate_boards(
                onboard_debug,
                extend_debug=True,
                skip_columns=skip_board_columns))
    if external_debug:
        lines.append("""
External Debug Tools
^^^^^^^^^^^^^^^^^^^^

Boards listed below are compatible with :ref:`piodebug` but **DEPEND ON**
external debug tool. See "Debug" column for compatible debug tools.
""")
        lines.extend(
            generate_boards(
                external_debug,
                extend_debug=True,
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


def generate_platform(name, rst_dir):
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
    assert p.repository_url.endswith(".git")
    github_url = p.repository_url[:-4]

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
            if not isdir(join(examples_dir, eitem)):
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
                extra_rst="%s_debug.rst" % name
                if isfile(join(rst_dir, "%s_debug.rst" % name)) else None))

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
            f.write(generate_platform(name, platforms_dir))


def generate_framework(type_, data, rst_dir=None):
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
    if isfile(join(rst_dir, "%s_extra.rst" % type_)):
        lines.append(".. include:: %s_extra.rst" % type_)

    #
    # Debugging
    #
    if compatible_boards:
        lines.extend(
            generate_debug_contents(
                compatible_boards,
                extra_rst="%s_debug.rst" % type_
                if isfile(join(rst_dir, "%s_debug.rst" % type_)) else None))

    if compatible_platforms:
        # examples
        lines.append("""
Examples
--------
""")
        for manifest in compatible_platforms:
            p = PlatformFactory.newPlatform(manifest['name'])
            lines.append(
                "* `%s for %s <%s>`_" %
                (data['title'], manifest['title'],
                 campaign_url(
                     "%s/tree/master/examples" % p.repository_url[:-4])))

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
            f.write(generate_framework(name, framework, frameworks_dir))


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
    tools_to_platforms = {}
    vendors = {}
    platforms = []
    frameworks = []
    for data in BOARDS:
        if not data['debug']:
            continue

        for tool in data['debug']['tools']:
            tool = str(tool)
            if tool not in tools_to_platforms:
                tools_to_platforms[tool] = []
            tools_to_platforms[tool].append(data['platform'])

        platforms.append(data['platform'])
        frameworks.extend(data['frameworks'])
        vendor = data['vendor']
        if vendor in vendors:
            vendors[vendor].append(data)
        else:
            vendors[vendor] = [data]

    def _update_tool_compat_platforms(content):
        begin_tpl = ".. begin_compatible_platforms_"
        end_tpl = ".. end_compatible_platforms_"
        for tool, platforms in tools_to_platforms.items():
            begin = begin_tpl + tool
            end = end_tpl + tool
            begin_index = content.index(begin)
            end_index = content.index(end)
            chunk = ["\n\n**Compatible development platforms:**\n"]
            chunk.extend([
                "* :ref:`platform_%s`" % str(p)
                for p in sorted(set(platforms))
            ])
            chunk.extend(["\n"])
            content = content[:begin_index + len(begin)] + "\n".join(
                chunk) + content[end_index:]
        return content

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
        content = _update_tool_compat_platforms(fp.read())
        fp.seek(0)
        fp.truncate()
        fp.write(content[:content.index(".. _debugging_platforms:")] +
                 "\n".join(lines))


def update_project_examples():
    platform_readme_tpl = """
# {title}: development platform for [PlatformIO](https://platformio.org)

{description}

* [Home](https://platformio.org/platforms/{name}) (home page in PlatformIO Registry)
* [Documentation](http://docs.platformio.org/page/platforms/{name}.html) (advanced usage, packages, boards, frameworks, etc.)

# Examples

{examples}
"""
    framework_readme_tpl = """
# {title}: framework for [PlatformIO](https://platformio.org)

{description}

* [Home](https://platformio.org/frameworks/{name}) (home page in PlatformIO Registry)
* [Documentation](http://docs.platformio.org/page/frameworks/{name}.html)

# Examples

{examples}
"""

    project_examples_dir = join(util.get_source_dir(), "..", "examples")
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
                if not isdir(join(platform_examples_dir, item)):
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
            "http://docs.platformio.org/en/latest/frameworks/%s.html#examples"
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
    update_embedded_boards()
    update_debugging()
    update_project_examples()


if __name__ == "__main__":
    sys_exit(main())
