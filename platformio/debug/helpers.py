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

import re
import sys
import time
from fnmatch import fnmatch
from hashlib import sha1
from io import BytesIO
from os.path import isfile

from platformio import util
from platformio.commands import PlatformioCLI
from platformio.commands.run.command import cli as cmd_run
from platformio.commands.run.command import print_processing_header
from platformio.commands.test.helpers import get_test_names
from platformio.commands.test.processor import TestProcessorBase
from platformio.compat import IS_WINDOWS, is_bytes
from platformio.debug.exception import DebugInvalidOptionsError


class GDBMIConsoleStream(BytesIO):  # pylint: disable=too-few-public-methods

    STDOUT = sys.stdout

    def write(self, text):
        self.STDOUT.write(escape_gdbmi_stream("~", text))
        self.STDOUT.flush()


def is_gdbmi_mode():
    return "--interpreter" in " ".join(PlatformioCLI.leftover_args)


def escape_gdbmi_stream(prefix, stream):
    bytes_stream = False
    if is_bytes(stream):
        bytes_stream = True
        stream = stream.decode()

    if not stream:
        return b"" if bytes_stream else ""

    ends_nl = stream.endswith("\n")
    stream = re.sub(r"\\+", "\\\\\\\\", stream)
    stream = stream.replace('"', '\\"')
    stream = stream.replace("\n", "\\n")
    stream = '%s"%s"' % (prefix, stream)
    if ends_nl:
        stream += "\n"

    return stream.encode() if bytes_stream else stream


def get_default_debug_env(config):
    default_envs = config.default_envs()
    all_envs = config.envs()
    for env in default_envs:
        if config.get("env:" + env, "build_type") == "debug":
            return env
    for env in all_envs:
        if config.get("env:" + env, "build_type") == "debug":
            return env
    return default_envs[0] if default_envs else all_envs[0]


def predebug_project(
    ctx, project_dir, project_config, env_name, preload, verbose
):  # pylint: disable=too-many-arguments
    debug_testname = project_config.get("env:" + env_name, "debug_test")
    if debug_testname:
        test_names = get_test_names(project_config)
        if debug_testname not in test_names:
            raise DebugInvalidOptionsError(
                "Unknown test name `%s`. Valid names are `%s`"
                % (debug_testname, ", ".join(test_names))
            )
        print_processing_header(env_name, project_config, verbose)
        tp = TestProcessorBase(
            ctx,
            debug_testname,
            env_name,
            dict(
                project_config=project_config,
                project_dir=project_dir,
                without_building=False,
                without_uploading=True,
                without_testing=True,
                verbose=False,
            ),
        )
        tp.build_or_upload(["__debug", "__test"] + (["upload"] if preload else []))
    else:
        ctx.invoke(
            cmd_run,
            project_dir=project_dir,
            project_conf=project_config.path,
            environment=[env_name],
            target=["__debug"] + (["upload"] if preload else []),
            verbose=verbose,
        )

    if preload:
        time.sleep(5)


def has_debug_symbols(prog_path):
    if not isfile(prog_path):
        return False
    matched = {
        b".debug_info": False,
        b".debug_abbrev": False,
        b" -Og": False,
        b" -g": False,
        # b"__PLATFORMIO_BUILD_DEBUG__": False,
    }
    with open(prog_path, "rb") as fp:
        last_data = b""
        while True:
            data = fp.read(1024)
            if not data:
                break
            for pattern, found in matched.items():
                if found:
                    continue
                if pattern in last_data + data:
                    matched[pattern] = True
            last_data = data
    return all(matched.values())


def is_prog_obsolete(prog_path):
    prog_hash_path = prog_path + ".sha1"
    if not isfile(prog_path):
        return True
    shasum = sha1()
    with open(prog_path, "rb") as fp:
        while True:
            data = fp.read(1024)
            if not data:
                break
            shasum.update(data)
    new_digest = shasum.hexdigest()
    old_digest = None
    if isfile(prog_hash_path):
        with open(prog_hash_path, encoding="utf8") as fp:
            old_digest = fp.read()
    if new_digest == old_digest:
        return False
    with open(prog_hash_path, mode="w", encoding="utf8") as fp:
        fp.write(new_digest)
    return True


def reveal_debug_port(env_debug_port, tool_name, tool_settings):
    def _get_pattern():
        if not env_debug_port:
            return None
        if set(["*", "?", "[", "]"]) & set(env_debug_port):
            return env_debug_port
        return None

    def _is_match_pattern(port):
        pattern = _get_pattern()
        if not pattern:
            return True
        return fnmatch(port, pattern)

    def _look_for_serial_port(hwids):
        for item in util.get_serialports(filter_hwid=True):
            if not _is_match_pattern(item["port"]):
                continue
            port = item["port"]
            if tool_name.startswith("blackmagic"):
                if IS_WINDOWS and port.startswith("COM") and len(port) > 4:
                    port = "\\\\.\\%s" % port
                if "GDB" in item["description"]:
                    return port
            for hwid in hwids:
                hwid_str = ("%s:%s" % (hwid[0], hwid[1])).replace("0x", "")
                if hwid_str in item["hwid"]:
                    return port
        return None

    if env_debug_port and not _get_pattern():
        return env_debug_port
    if not tool_settings.get("require_debug_port"):
        return None

    debug_port = _look_for_serial_port(tool_settings.get("hwids", []))
    if not debug_port:
        raise DebugInvalidOptionsError("Please specify `debug_port` for environment")
    return debug_port
