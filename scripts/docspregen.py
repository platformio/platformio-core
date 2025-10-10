#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
PlatformIO documentation generator (refactor of original script).

Features:
 - CLI (click)
 - dry-run support
 - logging
 - safer file writes
 - typed functions
"""
from __future__ import annotations

import functools
import logging
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from urllib.parse import ParseResult, urlparse, urlunparse

import click

# Add repo root to path for local imports (mirrors original script behavior)
sys.path.append("..")

from platformio import fs  # noqa: E402
from platformio.package.manager.platform import PlatformPackageManager  # noqa: E402
from platformio.platform.factory import PlatformFactory  # noqa: E402

LOG = logging.getLogger("pio-docs-gen")
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

SKIP_DEBUG_TOOLS = {"esp-bridge", "esp-builtin", "dfu"}
STATIC_FRAMEWORK_DATA: Dict[str, Dict[str, str]] = {
    "arduino": {
        "title": "Arduino",
        "description": (
            "Arduino Wiring-based Framework allows writing cross-platform software "
            "to control devices attached to a wide range of Arduino boards to "
            "create all kinds of creative coding, interactive objects, spaces "
            "or physical experiences."
        ),
    },
    "cmsis": {
        "title": "CMSIS",
        "description": "Vendor-independent hardware abstraction layer for the Cortex-M processor series",
    },
    "freertos": {
        "title": "FreeRTOS",
        "description": (
            "FreeRTOS is a real-time operating system kernel for embedded devices "
            "that has been ported to 40 microcontroller platforms."
        ),
    },
}


def reg_package_url(type_: str, owner: str, name: str) -> str:
    if type_ == "library"_
