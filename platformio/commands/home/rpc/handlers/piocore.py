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
from io import BytesIO

import jsonrpc  # pylint: disable=import-error
from twisted.internet import threads  # pylint: disable=import-error

from platformio import __main__, __version__, util
from platformio.compat import string_types


class PIOCoreRPC(object):

    @staticmethod
    def call(args, options=None):
        try:
            args = [
                str(arg) if not isinstance(arg, string_types) else arg
                for arg in args
            ]
        except UnicodeError:
            raise jsonrpc.exceptions.JSONRPCDispatchException(
                code=4002, message="PIO Core: non-ASCII chars in arguments")

        def _call_cli():
            outbuff = BytesIO()
            errbuff = BytesIO()
            with util.capture_std_streams(outbuff, errbuff):
                with util.cd((options or {}).get("cwd") or os.getcwd()):
                    exit_code = __main__.main(["-c"] + args)
            result = (outbuff.getvalue(), errbuff.getvalue(), exit_code)
            outbuff.close()
            errbuff.close()
            return result

        d = threads.deferToThread(_call_cli)
        d.addCallback(PIOCoreRPC._call_callback, "--json-output" in args)
        d.addErrback(PIOCoreRPC._call_errback)
        return d

    @staticmethod
    def _call_callback(result, json_output=False):
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
