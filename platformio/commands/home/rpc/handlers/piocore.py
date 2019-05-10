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

from __future__ import absolute_import

import json
import os
import re

import jsonrpc  # pylint: disable=import-error
from twisted.internet import utils  # pylint: disable=import-error

from platformio import __version__
from platformio.commands.home import helpers
from platformio.compat import get_filesystem_encoding, string_types


class PIOCoreRPC(object):

    @staticmethod
    def call(args, options=None):
        json_output = "--json-output" in args
        try:
            args = [
                arg.encode(get_filesystem_encoding()) if isinstance(
                    arg, string_types) else str(arg) for arg in args
            ]
        except UnicodeError:
            raise jsonrpc.exceptions.JSONRPCDispatchException(
                code=4002, message="PIO Core: non-ASCII chars in arguments")
        d = utils.getProcessOutputAndValue(
            helpers.get_core_fullpath(),
            args,
            path=(options or {}).get("cwd"),
            env={k: v
                 for k, v in os.environ.items() if "%" not in k})
        d.addCallback(PIOCoreRPC._call_callback, json_output)
        d.addErrback(PIOCoreRPC._call_errback)
        return d

    @staticmethod
    def _call_callback(result, json_output=False):
        result = list(result)
        assert len(result) == 3
        for i in (0, 1):
            result[i] = result[i].decode(get_filesystem_encoding()).strip()
        out, err, code = result
        text = ("%s\n\n%s" % (out, err)).strip()
        if code != 0:
            raise Exception(text)

        if not json_output:
            return text

        try:
            return json.loads(out)
        except ValueError as e:
            if "sh: " in out:
                return json.loads(
                    re.sub(r"^sh: [^\n]+$", "", out, flags=re.M).strip())
            raise e

    @staticmethod
    def _call_errback(failure):
        raise jsonrpc.exceptions.JSONRPCDispatchException(
            code=4003,
            message="PIO Core Call Error",
            data=failure.getErrorMessage())

    @staticmethod
    def version():
        return __version__
