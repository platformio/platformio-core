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

import click
from twisted.spread import pb  # pylint: disable=import-error

from platformio.remote.client.base import RemoteClientBase


class AsyncClientBase(RemoteClientBase):
    def __init__(self, command, agents, options):
        RemoteClientBase.__init__(self)
        self.command = command
        self.agents = agents
        self.options = options

        self._acs_total = 0
        self._acs_ended = 0

    def agent_pool_ready(self):
        pass

    def cb_async_result(self, result):
        if self._acs_total == 0:
            self._acs_total = len(result)
        for (success, value) in result:
            if not success:
                raise pb.Error(value)
            self.acread_data(*value)

    def acread_data(self, agent_id, ac_id, agent_name=None):
        d = self.agentpool.callRemote("acread", agent_id, ac_id)
        d.addCallback(self.cb_acread_result, agent_id, ac_id, agent_name)
        d.addErrback(self.cb_global_error)

    def cb_acread_result(self, result, agent_id, ac_id, agent_name):
        if result is None:
            self.acclose(agent_id, ac_id)
        else:
            if self._acs_total > 1 and agent_name:
                click.echo("[%s] " % agent_name, nl=False)
            click.echo(result, nl=False)
            self.acread_data(agent_id, ac_id, agent_name)

    def acclose(self, agent_id, ac_id):
        d = self.agentpool.callRemote("acclose", agent_id, ac_id)
        d.addCallback(self.cb_acclose_result)
        d.addErrback(self.cb_global_error)

    def cb_acclose_result(self, exit_code):
        self._acs_ended += 1
        if self._acs_ended != self._acs_total:
            return
        self.disconnect(exit_code)
