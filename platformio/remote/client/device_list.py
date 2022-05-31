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

import json

import click

from platformio.remote.client.base import RemoteClientBase


class DeviceListClient(RemoteClientBase):
    def __init__(self, agents, json_output):
        RemoteClientBase.__init__(self)
        self.agents = agents
        self.json_output = json_output

    def agent_pool_ready(self):
        d = self.agentpool.callRemote("cmd", self.agents, "device.list")
        d.addCallback(self._cbResult)
        d.addErrback(self.cb_global_error)

    def _cbResult(self, result):
        data = {}
        for (success, value) in result:
            if not success:
                click.secho(value, fg="red", err=True)
                continue
            (agent_name, devlist) = value
            data[agent_name] = devlist

        if self.json_output:
            click.echo(json.dumps(data))
        else:
            for agent_name, devlist in data.items():
                click.echo("Agent %s" % click.style(agent_name, fg="cyan", bold=True))
                click.echo("=" * (6 + len(agent_name)))
                for item in devlist:
                    click.secho(item["port"], fg="cyan")
                    click.echo("-" * len(item["port"]))
                    click.echo("Hardware ID: %s" % item["hwid"])
                    click.echo("Description: %s" % item["description"])
                    click.echo("")
        self.disconnect()
