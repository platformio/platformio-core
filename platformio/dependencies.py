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

from platformio.compat import is_proxy_set


def get_core_dependencies():
    return {
        "contrib-piohome": "~3.4.2",
        "contrib-pioremote": "~1.0.0",
        "tool-scons": "~4.40801.0",
        "tool-cppcheck": "~1.21100.0",
        "tool-clangtidy": "~1.150005.0",
        "tool-pvs-studio": "~7.18.0",
    }


def get_pip_dependencies():
    core = [
        "bottle == 0.13.*",
        "click >=8.0.4, <9",
        "colorama",
        "marshmallow == 3.*",
        "pyelftools >=0.27, <1",
        "pyserial == 3.5.*",  # keep in sync "device/monitor/terminal.py"
        "requests%s == 2.*" % ("[socks]" if is_proxy_set(socks=True) else ""),
        "semantic_version == 2.10.*",
        "tabulate == 0.*",
    ]

    home = [
        # PIO Home requirements
        "ajsonrpc == 1.2.*",
        "starlette >=0.19, <0.46",
        "uvicorn >=0.16, <0.35",
        "wsproto == 1.*",
    ]

    extra = []
    # issue #4702; Broken "requests/charset_normalizer" on macOS ARM
    extra.append(
        'chardet >= 3.0.2,<6; platform_system == "Darwin" and "arm" in platform_machine'
    )

    # issue 4614: urllib3 v2.0 only supports OpenSSL 1.1.1+
    try:
        import ssl  # pylint: disable=import-outside-toplevel

        if ssl.OPENSSL_VERSION.startswith("OpenSSL ") and ssl.OPENSSL_VERSION_INFO < (
            1,
            1,
            1,
        ):
            extra.append("urllib3<2")
    except ImportError:
        pass

    return core + home + extra
