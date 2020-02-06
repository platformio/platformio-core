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

import os

import click


class PlatformioCLI(click.MultiCommand):

    leftover_args = []

    def __init__(self, *args, **kwargs):
        super(PlatformioCLI, self).__init__(*args, **kwargs)
        self._pio_cmds_dir = os.path.dirname(__file__)

    @staticmethod
    def in_silence():
        args = PlatformioCLI.leftover_args
        return args and any(
            [
                args[0] == "debug" and "--interpreter" in " ".join(args),
                args[0] == "upgrade",
                "--json-output" in args,
                "--version" in args,
            ]
        )

    def invoke(self, ctx):
        PlatformioCLI.leftover_args = ctx.args
        if hasattr(ctx, "protected_args"):
            PlatformioCLI.leftover_args = ctx.protected_args + ctx.args
        return super(PlatformioCLI, self).invoke(ctx)

    def list_commands(self, ctx):
        cmds = []
        for cmd_name in os.listdir(self._pio_cmds_dir):
            if cmd_name.startswith("__init__"):
                continue
            if os.path.isfile(os.path.join(self._pio_cmds_dir, cmd_name, "command.py")):
                cmds.append(cmd_name)
            elif cmd_name.endswith(".py"):
                cmds.append(cmd_name[:-3])
        cmds.sort()
        return cmds

    def get_command(self, ctx, cmd_name):
        mod = None
        try:
            mod_path = "platformio.commands." + cmd_name
            if os.path.isfile(os.path.join(self._pio_cmds_dir, cmd_name, "command.py")):
                mod_path = "platformio.commands.%s.command" % cmd_name
            mod = __import__(mod_path, None, None, ["cli"])
        except ImportError:
            try:
                return self._handle_obsolate_command(cmd_name)
            except AttributeError:
                pass
            raise click.UsageError('No such command "%s"' % cmd_name, ctx)
        return mod.cli

    @staticmethod
    def _handle_obsolate_command(name):
        # pylint: disable=import-outside-toplevel
        if name == "init":
            from platformio.commands.project import project_init

            return project_init
        raise AttributeError()
