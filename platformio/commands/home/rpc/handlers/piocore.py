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
from io import BytesIO, StringIO

import click
import jsonrpc  # pylint: disable=import-error
from twisted.internet import defer  # pylint: disable=import-error
from twisted.internet import threads  # pylint: disable=import-error
from twisted.internet import utils  # pylint: disable=import-error

from platformio import __main__, __version__, fs
from platformio.commands.home import helpers
from platformio.compat import PY2, get_filesystem_encoding, is_bytes, string_types

try:
    from thread import get_ident as thread_get_ident
except ImportError:
    from threading import get_ident as thread_get_ident


class MultiThreadingStdStream(object):
    def __init__(self, parent_stream):
        self._buffers = {thread_get_ident(): parent_stream}

    def __getattr__(self, name):
        thread_id = thread_get_ident()
        self._ensure_thread_buffer(thread_id)
        return getattr(self._buffers[thread_id], name)

    def _ensure_thread_buffer(self, thread_id):
        if thread_id not in self._buffers:
            self._buffers[thread_id] = BytesIO() if PY2 else StringIO()

    def write(self, value):
        thread_id = thread_get_ident()
        self._ensure_thread_buffer(thread_id)
        return self._buffers[thread_id].write(
            value.decode() if is_bytes(value) else value
        )

    def get_value_and_reset(self):
        result = ""
        try:
            result = self.getvalue()
            self.truncate(0)
            self.seek(0)
        except AttributeError:
            pass
        return result


class PIOCoreRPC(object):
    @staticmethod
    def version():
        return __version__

    @staticmethod
    def setup_multithreading_std_streams():
        if isinstance(sys.stdout, MultiThreadingStdStream):
            return
        PIOCoreRPC.thread_stdout = MultiThreadingStdStream(sys.stdout)
        PIOCoreRPC.thread_stderr = MultiThreadingStdStream(sys.stderr)
        sys.stdout = PIOCoreRPC.thread_stdout
        sys.stderr = PIOCoreRPC.thread_stderr

    @staticmethod
    def call(args, options=None):
        return defer.maybeDeferred(PIOCoreRPC._call_generator, args, options)

    @staticmethod
    @defer.inlineCallbacks
    def _call_generator(args, options=None):
        for i, arg in enumerate(args):
            if isinstance(arg, string_types):
                args[i] = arg.encode(get_filesystem_encoding()) if PY2 else arg
            else:
                args[i] = str(arg)

        to_json = "--json-output" in args

        try:
            if args and args[0] in ("account", "remote"):
                result = yield PIOCoreRPC._call_subprocess(args, options)
                defer.returnValue(PIOCoreRPC._process_result(result, to_json))
            else:
                result = yield PIOCoreRPC._call_inline(args, options)
                try:
                    defer.returnValue(PIOCoreRPC._process_result(result, to_json))
                except ValueError:
                    # fall-back to subprocess method
                    result = yield PIOCoreRPC._call_subprocess(args, options)
                    defer.returnValue(PIOCoreRPC._process_result(result, to_json))
        except Exception as e:  # pylint: disable=bare-except
            raise jsonrpc.exceptions.JSONRPCDispatchException(
                code=4003, message="PIO Core Call Error", data=str(e)
            )

    @staticmethod
    def _call_inline(args, options):
        PIOCoreRPC.setup_multithreading_std_streams()
        cwd = (options or {}).get("cwd") or os.getcwd()

        def _thread_task():
            with fs.cd(cwd):
                exit_code = __main__.main(["-c"] + args)
            return (
                PIOCoreRPC.thread_stdout.get_value_and_reset(),
                PIOCoreRPC.thread_stderr.get_value_and_reset(),
                exit_code,
            )

        return threads.deferToThread(_thread_task)

    @staticmethod
    def _call_subprocess(args, options):
        cwd = (options or {}).get("cwd") or os.getcwd()
        return utils.getProcessOutputAndValue(
            helpers.get_core_fullpath(),
            args,
            path=cwd,
            env={k: v for k, v in os.environ.items() if "%" not in k},
        )

    @staticmethod
    def _process_result(result, to_json=False):
        out, err, code = result
        text = ("%s\n\n%s" % (out, err)).strip()
        if code != 0:
            raise Exception(text)
        if not to_json:
            return text
        if is_bytes(out):
            out = out.decode()
        try:
            return json.loads(out)
        except ValueError as e:
            click.secho("%s => `%s`" % (e, out), fg="red", err=True)
            # if PIO Core prints unhandled warnings
            for line in out.split("\n"):
                line = line.strip()
                if not line:
                    continue
                try:
                    return json.loads(line)
                except ValueError:
                    pass
            raise e
