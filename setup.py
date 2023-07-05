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

from setuptools import find_packages, setup

from platformio import (
    __author__,
    __description__,
    __email__,
    __license__,
    __title__,
    __url__,
    __version__,
)

env_marker_below_37 = "python_version < '3.7'"
env_marker_gte_37 = "python_version >= '3.7'"

minimal_requirements = [
    "bottle==0.12.*",
    "click==8.0.4; " + env_marker_below_37,
    "click==8.1.*; " + env_marker_gte_37,
    "colorama",
    "marshmallow==3.14.1; " + env_marker_below_37,
    "marshmallow==3.19.*; " + env_marker_gte_37,
    "pyelftools==0.29",
    "pyserial==3.5.*",  # keep in sync "device/monitor/terminal.py"
    "requests==2.*",
    "semantic_version==2.10.*",
    "tabulate==0.*",
]

home_requirements = [
    "aiofiles>=0.8.0",
    "ajsonrpc==1.2.*",
    "starlette==0.19.1; " + env_marker_below_37,
    "starlette==0.28.*; " + env_marker_gte_37,
    "uvicorn==0.16.0; " + env_marker_below_37,
    "uvicorn==0.22.*; " + env_marker_gte_37,
    "wsproto==1.0.0; " + env_marker_below_37,
    "wsproto==1.2.*; " + env_marker_gte_37,
]

# issue 4614: urllib3 v2.0 only supports OpenSSL 1.1.1+
try:
    import ssl

    if ssl.OPENSSL_VERSION.startswith("OpenSSL ") and ssl.OPENSSL_VERSION_INFO < (
        1,
        1,
        1,
    ):
        minimal_requirements.append("urllib3<2")
except ImportError:
    pass


setup(
    name=__title__,
    version=__version__,
    description=__description__,
    long_description=open("README.rst").read(),
    author=__author__,
    author_email=__email__,
    url=__url__,
    license=__license__,
    install_requires=minimal_requirements + home_requirements,
    python_requires=">=3.6",
    packages=find_packages(include=["platformio", "platformio.*"]),
    package_data={
        "platformio": [
            "assets/system/99-platformio-udev.rules",
            "project/integration/tpls/*/*.tpl",
            "project/integration/tpls/*/.*.tpl",  # include hidden files
            "project/integration/tpls/*/.*/*.tpl",  # include hidden folders
            "project/integration/tpls/*/*/*.tpl",  # NetBeans
            "project/integration/tpls/*/*/*/*.tpl",  # NetBeans
        ]
    },
    entry_points={
        "console_scripts": [
            "platformio = platformio.__main__:main",
            "pio = platformio.__main__:main",
            "piodebuggdb = platformio.__main__:debug_gdb_main",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Compilers",
    ],
    keywords=[
        "iot",
        "embedded",
        "arduino",
        "mbed",
        "esp8266",
        "esp32",
        "fpga",
        "firmware",
        "continuous-integration",
        "cloud-ide",
        "avr",
        "arm",
        "ide",
        "unit-testing",
        "hardware",
        "verilog",
        "microcontroller",
        "debug",
    ],
)
