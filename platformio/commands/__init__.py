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
from os.path import dirname

import click


class PlatformioCLI(click.MultiCommand):

    leftover_args = []

    @staticmethod
    def in_silence():
        args = PlatformioCLI.leftover_args
        return args and any([
            args[0] == "debug" and "--interpreter" in " ".join(args),
            args[0] == "upgrade", "--json-output" in args, "--version" in args
        ])

    def invoke(self, ctx):
        PlatformioCLI.leftover_args = ctx.args
        if hasattr(ctx, "protected_args"):
            PlatformioCLI.leftover_args = ctx.protected_args + ctx.args
        return super(PlatformioCLI, self).invoke(ctx)

    def list_commands(self, ctx):
        cmds = []
        for filename in os.listdir(dirname(__file__)):
            if filename.startswith("__init__"):
                continue
            if filename.endswith(".py"):
                cmds.append(filename[:-3])
        cmds.sort()
        return cmds

    def get_command(self, ctx, cmd_name):
        mod = None
        try:
            mod = __import__("platformio.commands." + cmd_name, None, None,
                             ["cli"])
        except ImportError:
            try:
                return self._handle_obsolate_command(cmd_name)
            except AttributeError:
                raise click.UsageError('No such command "%s"' % cmd_name, ctx)
        return mod.cli

    @staticmethod
    def _handle_obsolate_command(name):
        if name == "platforms":
            from platformio.commands import platform
            return platform.cli
        if name == "serialports":
            from platformio.commands import device
            return device.cli
        raise AttributeError()
