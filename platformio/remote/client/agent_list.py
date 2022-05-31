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

from datetime import datetime

import click

from platformio.remote.client.base import RemoteClientBase


class AgentListClient(RemoteClientBase):
    def agent_pool_ready(self):
        d = self.agentpool.callRemote("list", True)
        d.addCallback(self._cbResult)
        d.addErrback(self.cb_global_error)

    def _cbResult(self, result):
        for item in result:
            click.secho(item["name"], fg="cyan")
            click.echo("-" * len(item["name"]))
            click.echo("ID: %s" % item["id"])
            click.echo(
                "Started: %s"
                % datetime.fromtimestamp(item["started"]).strftime("%Y-%m-%d %H:%M:%S")
            )
            click.echo("")
        self.disconnect()
