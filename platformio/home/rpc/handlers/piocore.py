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

import io
import json
import os
import sys
import threading

import click
from ajsonrpc.core import JSONRPC20DispatchException
from starlette.concurrency import run_in_threadpool

from platformio import __main__, __version__, fs, proc
from platformio.compat import get_locale_encoding, is_bytes
from platformio.home import helpers


class MultiThreadingStdStream:
    def __init__(self, parent_stream):
        self._buffers = {threading.get_ident(): parent_stream}

    def __getattr__(self, name):
        thread_id = threading.get_ident()
        self._ensure_thread_buffer(thread_id)
        return getattr(self._buffers[thread_id], name)

    def _ensure_thread_buffer(self, thread_id):
        if thread_id not in self._buffers:
            self._buffers[thread_id] = io.StringIO()

    def write(self, value):
        thread_id = threading.get_ident()
        self._ensure_thread_buffer(thread_id)
        return self._buffers[thread_id].write(
            value.decode() if is_bytes(value) else value
        )

    def get_value_and_reset(self):
        result = ""
        try:
            result = self.getvalue()
            self.seek(0)
            self.truncate(0)
        except AttributeError:
            pass
        return result


class PIOCoreRPC:
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
    async def call(args, options=None):
        for i, arg in enumerate(args):
            if not isinstance(arg, str):
                args[i] = str(arg)

        options = options or {}
        to_json = "--json-output" in args

        try:
            if options.get("force_subprocess"):
                result = await PIOCoreRPC._call_subprocess(args, options)
                return PIOCoreRPC._process_result(result, to_json)
            result = await PIOCoreRPC._call_inline(args, options)
            try:
                return PIOCoreRPC._process_result(result, to_json)
            except ValueError:
                # fall-back to subprocess method
                result = await PIOCoreRPC._call_subprocess(args, options)
                return PIOCoreRPC._process_result(result, to_json)
        except Exception as exc:  # pylint: disable=bare-except
            raise JSONRPC20DispatchException(
                code=4003, message="PIO Core Call Error", data=str(exc)
            ) from exc

    @staticmethod
    async def _call_subprocess(args, options):
        result = await run_in_threadpool(
            proc.exec_command,
            [helpers.get_core_fullpath()] + args,
            cwd=options.get("cwd") or os.getcwd(),
        )
        return (result["out"], result["err"], result["returncode"])

    @staticmethod
    async def _call_inline(args, options):
        PIOCoreRPC.setup_multithreading_std_streams()

        def _thread_safe_call(args, cwd):
            with fs.cd(cwd):
                exit_code = __main__.main(["-c"] + args)
            return (
                PIOCoreRPC.thread_stdout.get_value_and_reset(),
                PIOCoreRPC.thread_stderr.get_value_and_reset(),
                exit_code,
            )

        return await run_in_threadpool(
            _thread_safe_call, args=args, cwd=options.get("cwd") or os.getcwd()
        )

    @staticmethod
    def _process_result(result, to_json=False):
        out, err, code = result
        if out and is_bytes(out):
            out = out.decode(get_locale_encoding())
        if err and is_bytes(err):
            err = err.decode(get_locale_encoding())
        text = ("%s\n\n%s" % (out, err)).strip()
        if code != 0:
            raise Exception(text)
        if not to_json:
            return text
        try:
            return json.loads(out)
        except ValueError as exc:
            click.secho("%s => `%s`" % (exc, out), fg="red", err=True)
            # if PIO Core prints unhandled warnings
            for line in out.split("\n"):
                line = line.strip()
                if not line:
                    continue
                try:
                    return json.loads(line)
                except ValueError:
                    pass
            raise exc
