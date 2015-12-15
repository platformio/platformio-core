# Copyright 2014-2015 Ivan Kravets <me@ikravets.com>
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

from platform import system

from setuptools import find_packages, setup

from platformio import (__author__, __description__, __email__, __license__,
                        __title__, __url__, __version__, util)

install_requires = [
    "bottle",
    "click>=3.2,<6",
    "lockfile>=0.9.1",
    "pyserial",
    "requests>=2.4.0"
]

if system() == "Windows":
    install_requires.append("colorama")

if (not util.test_scons() and not util.install_scons()) or util.scons_in_pip():
    install_requires.append("scons")

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
        "iot", "build tool", "compiler", "builder", "library manager",
        "embedded", "ci", "continuous integration", "arduino", "mbed",
        "framework", "ide", "ide integration", "library.json", "make", "cmake",
        "makefile", "mk"
    ]
)
