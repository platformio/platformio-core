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

from platformio import (__author__, __description__, __email__, __license__,
                        __title__, __url__, __version__)

install_requires = [
    "arrow<1",
    "bottle<0.13",
    "click>=5,<6",
    "colorama",
    "lockfile>=0.9.1,<0.13",
    "pyserial>=3,<4,!=3.3",
    "requests>=2.4.0,<3",
    "semantic_version>=2.5.0"
]

setup(
    name=__title__,
    version=__version__,
    description=__description__,
    long_description=open("README.rst").read(),
    author=__author__,
    author_email=__email__,
    url=__url__,
    license=__license__,
    install_requires=install_requires,
    packages=find_packages(),
    package_data={
        "platformio": [
            "projectconftpl.ini",
            "ide/tpls/*/.*.tpl",
            "ide/tpls/*/*.tpl",
            "ide/tpls/*/*/*.tpl",
            "ide/tpls/*/.*/*.tpl"
        ]
    },
    entry_points={
        "console_scripts": [
            "pio = platformio.__main__:main",
            "piodebuggdb = platformio.__main__:debug_gdb_main",
            "platformio = platformio.__main__:main"
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
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Compilers"
    ],
    keywords=[
        "iot", "embedded", "arduino", "mbed", "esp8266", "esp32", "fpga",
        "firmware", "continuous-integration", "cloud-ide", "avr", "arm",
        "ide", "unit-testing", "hardware", "verilog", "microcontroller",
        "debug"
    ])
