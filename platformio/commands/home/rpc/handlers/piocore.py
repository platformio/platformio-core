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
import sys
import thread
from io import BytesIO

import jsonrpc  # pylint: disable=import-error
from twisted.internet import threads  # pylint: disable=import-error

from platformio import __main__, __version__, util
from platformio.compat import string_types


class ThreadSafeStdBuffer(object):

    def __init__(self, parent_stream, parent_thread_id):
        self.parent_stream = parent_stream
        self.parent_thread_id = parent_thread_id
        self._buffer = {}

    def write(self, value):
        thread_id = thread.get_ident()
        if thread_id == self.parent_thread_id:
            return self.parent_stream.write(value)
        if thread_id not in self._buffer:
            self._buffer[thread_id] = BytesIO()
        return self._buffer[thread_id].write(value)

    def flush(self):
        return (self.parent_stream.flush()
                if thread.get_ident() == self.parent_thread_id else None)

    def getvalue_and_close(self, thread_id=None):
        thread_id = thread_id or thread.get_ident()
        if thread_id not in self._buffer:
            return ""
        result = self._buffer.get(thread_id).getvalue()
        self._buffer.get(thread_id).close()
        del self._buffer[thread_id]
        return result


class PIOCoreRPC(object):

    def __init__(self):
        cur_thread_id = thread.get_ident()
        PIOCoreRPC.thread_stdout = ThreadSafeStdBuffer(sys.stdout,
                                                       cur_thread_id)
        PIOCoreRPC.thread_stderr = ThreadSafeStdBuffer(sys.stderr,
                                                       cur_thread_id)
        sys.stdout = PIOCoreRPC.thread_stdout
        sys.stderr = PIOCoreRPC.thread_stderr

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
            with util.cd((options or {}).get("cwd") or os.getcwd()):
                exit_code = __main__.main(["-c"] + args)
            return (PIOCoreRPC.thread_stdout.getvalue_and_close(),
                    PIOCoreRPC.thread_stderr.getvalue_and_close(), exit_code)

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
        return json.loads(out) if json_output else text

    @staticmethod
    def _call_errback(failure):
        raise jsonrpc.exceptions.JSONRPCDispatchException(
            code=4003,
            message="PIO Core Call Error",
            data=failure.getErrorMessage())

    @staticmethod
    def version():
        return __version__
