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

from platformio import exception, fs, util
from platformio.commands import PlatformioCLI
from platformio.commands.debug.exception import DebugInvalidOptionsError
from platformio.commands.platform import platform_install as cmd_platform_install
from platformio.commands.run.command import cli as cmd_run
from platformio.compat import is_bytes
from platformio.managers.platform import PlatformFactory
from platformio.project.config import ProjectConfig
from platformio.project.options import ProjectOptions


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


def predebug_project(ctx, project_dir, env_name, preload, verbose):
    ctx.invoke(
        cmd_run,
        project_dir=project_dir,
        environment=[env_name],
        target=["debug"] + (["upload"] if preload else []),
        verbose=verbose,
    )
    if preload:
        time.sleep(5)


def validate_debug_options(cmd_ctx, env_options):
    def _cleanup_cmds(items):
        items = ProjectConfig.parse_multi_values(items)
        return ["$LOAD_CMDS" if item == "$LOAD_CMD" else item for item in items]

    try:
        platform = PlatformFactory.newPlatform(env_options["platform"])
    except exception.UnknownPlatform:
        cmd_ctx.invoke(
            cmd_platform_install,
            platforms=[env_options["platform"]],
            skip_default_package=True,
        )
        platform = PlatformFactory.newPlatform(env_options["platform"])

    board_config = platform.board_config(env_options["board"])
    tool_name = board_config.get_debug_tool_name(env_options.get("debug_tool"))
    tool_settings = board_config.get("debug", {}).get("tools", {}).get(tool_name, {})
    server_options = None

    # specific server per a system
    if isinstance(tool_settings.get("server", {}), list):
        for item in tool_settings["server"][:]:
            tool_settings["server"] = item
            if util.get_systype() in item.get("system", []):
                break

    # user overwrites debug server
    if env_options.get("debug_server"):
        server_options = {
            "cwd": None,
            "executable": None,
            "arguments": env_options.get("debug_server"),
        }
        server_options["executable"] = server_options["arguments"][0]
        server_options["arguments"] = server_options["arguments"][1:]
    elif "server" in tool_settings:
        server_options = tool_settings["server"]
        server_package = server_options.get("package")
        server_package_dir = (
            platform.get_package_dir(server_package) if server_package else None
        )
        if server_package and not server_package_dir:
            platform.install_packages(
                with_packages=[server_package], skip_default_package=True, silent=True
            )
            server_package_dir = platform.get_package_dir(server_package)
        server_options.update(
            dict(
                cwd=server_package_dir if server_package else None,
                executable=server_options.get("executable"),
                arguments=[
                    a.replace("$PACKAGE_DIR", server_package_dir)
                    if server_package_dir
                    else a
                    for a in server_options.get("arguments", [])
                ],
            )
        )

    extra_cmds = _cleanup_cmds(env_options.get("debug_extra_cmds"))
    extra_cmds.extend(_cleanup_cmds(tool_settings.get("extra_cmds")))
    result = dict(
        tool=tool_name,
        upload_protocol=env_options.get(
            "upload_protocol", board_config.get("upload", {}).get("protocol")
        ),
        load_cmds=_cleanup_cmds(
            env_options.get(
                "debug_load_cmds",
                tool_settings.get(
                    "load_cmds",
                    tool_settings.get(
                        "load_cmd", ProjectOptions["env.debug_load_cmds"].default
                    ),
                ),
            )
        ),
        load_mode=env_options.get(
            "debug_load_mode",
            tool_settings.get(
                "load_mode", ProjectOptions["env.debug_load_mode"].default
            ),
        ),
        init_break=env_options.get(
            "debug_init_break",
            tool_settings.get(
                "init_break", ProjectOptions["env.debug_init_break"].default
            ),
        ),
        init_cmds=_cleanup_cmds(
            env_options.get("debug_init_cmds", tool_settings.get("init_cmds"))
        ),
        extra_cmds=extra_cmds,
        require_debug_port=tool_settings.get("require_debug_port", False),
        port=reveal_debug_port(
            env_options.get("debug_port", tool_settings.get("port")),
            tool_name,
            tool_settings,
        ),
        server=server_options,
    )
    return result


def configure_esp32_load_cmds(debug_options, configuration):
    ignore_conds = [
        debug_options["load_cmds"] != ["load"],
        "xtensa-esp32" not in configuration.get("cc_path", ""),
        not configuration.get("flash_extra_images"),
        not all(
            [isfile(item["path"]) for item in configuration.get("flash_extra_images")]
        ),
    ]
    if any(ignore_conds):
        return debug_options["load_cmds"]

    mon_cmds = [
        'monitor program_esp32 "{{{path}}}" {offset} verify'.format(
            path=fs.to_unix_path(item["path"]), offset=item["offset"]
        )
        for item in configuration.get("flash_extra_images")
    ]
    mon_cmds.append(
        'monitor program_esp32 "{%s.bin}" 0x10000 verify'
        % fs.to_unix_path(configuration["prog_path"][:-4])
    )
    return mon_cmds


def has_debug_symbols(prog_path):
    if not isfile(prog_path):
        return False
    matched = {
        b".debug_info": False,
        b".debug_abbrev": False,
        b" -Og": False,
        b" -g": False,
        b"__PLATFORMIO_BUILD_DEBUG__": False,
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
        with open(prog_hash_path) as fp:
            old_digest = fp.read()
    if new_digest == old_digest:
        return False
    with open(prog_hash_path, "w") as fp:
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
                if (
                    "windows" in util.get_systype()
                    and port.startswith("COM")
                    and len(port) > 4
                ):
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
