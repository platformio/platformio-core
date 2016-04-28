# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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

import sys

from setuptools import find_packages, setup

from platformio import (__author__, __description__, __email__, __license__,
                        __title__, __url__, __version__)

install_requires = [
    "bottle<0.13",
    "click>=3.2,<6",
    "lockfile>=0.9.1,<0.13",
    "requests>=2.4.0,<3",
    "colorama",
    "pyserial<4"
]

if sys.version_info < (2, 7, 0):
    install_requires[-1] = "pyserial<3"

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
            "boards/*.json",
            "ide/tpls/*/.*.tpl",
            "ide/tpls/*/*.tpl",
            "ide/tpls/*/*/*.tpl",
            "ide/tpls/*/.*/*.tpl"
        ]
    },
    entry_points={
        "console_scripts": [
            "pio = platformio.__main__:main",
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
        "iot", "ide", "build", "compile", "library manager",
        "embedded", "ci", "continuous integration", "arduino", "mbed",
        "esp8266", "framework", "ide", "ide integration", "library.json",
        "make", "cmake", "makefile", "mk", "pic32", "fpga"
    ]
)
