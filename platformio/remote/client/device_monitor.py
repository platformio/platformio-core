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
from fnmatch import fnmatch

import click
from twisted.internet import protocol, reactor, task  # pylint: disable=import-error
from twisted.spread import pb  # pylint: disable=import-error

from platformio.remote.client.base import RemoteClientBase


class SMBridgeProtocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.add_client(self)

    def connectionLost(self, reason):  # pylint: disable=unused-argument
        self.factory.remove_client(self)

    def dataReceived(self, data):
        self.factory.send_to_server(data)


class SMBridgeFactory(protocol.ServerFactory):
    def __init__(self, cdm):
        self.cdm = cdm
        self._clients = []

    def buildProtocol(self, addr):  # pylint: disable=unused-argument
        p = SMBridgeProtocol()
        p.factory = self  # pylint: disable=attribute-defined-outside-init
        return p

    def add_client(self, client):
        self.cdm.log.debug("SMBridge: Client connected")
        self._clients.append(client)
        self.cdm.acread_data()

    def remove_client(self, client):
        self.cdm.log.debug("SMBridge: Client disconnected")
        self._clients.remove(client)
        if not self._clients:
            self.cdm.client_terminal_stopped()

    def has_clients(self):
        return len(self._clients)

    def send_to_clients(self, data):
        if not self._clients:
            return None
        for client in self._clients:
            client.transport.write(data)
        return len(data)

    def send_to_server(self, data):
        self.cdm.acwrite_data(data)


class DeviceMonitorClient(  # pylint: disable=too-many-instance-attributes
    RemoteClientBase
):

    MAX_BUFFER_SIZE = 1024 * 1024

    def __init__(self, agents, **kwargs):
        RemoteClientBase.__init__(self)
        self.agents = agents
        self.cmd_options = kwargs

        self._bridge_factory = SMBridgeFactory(self)
        self._agent_id = None
        self._ac_id = None
        self._d_acread = None
        self._d_acwrite = None
        self._acwrite_buffer = b""

    def agent_pool_ready(self):
        d = task.deferLater(
            reactor, 1, self.agentpool.callRemote, "cmd", self.agents, "device.list"
        )
        d.addCallback(self._cb_device_list)
        d.addErrback(self.cb_global_error)

    def _cb_device_list(self, result):
        devices = []
        hwid_devindexes = []
        for (success, value) in result:
            if not success:
                click.secho(value, fg="red", err=True)
                continue
            (agent_name, ports) = value
            for item in ports:
                if "VID:PID" in item["hwid"]:
                    hwid_devindexes.append(len(devices))
                devices.append((agent_name, item))

        if len(result) == 1 and self.cmd_options["port"]:
            if set(["*", "?", "[", "]"]) & set(self.cmd_options["port"]):
                for agent, item in devices:
                    if fnmatch(item["port"], self.cmd_options["port"]):
                        return self.start_remote_monitor(agent, item["port"])
            return self.start_remote_monitor(result[0][1][0], self.cmd_options["port"])

        device = None
        if len(hwid_devindexes) == 1:
            device = devices[hwid_devindexes[0]]
        else:
            click.echo("Available ports:")
            for i, device in enumerate(devices):
                click.echo(
                    "{index}. {host}{port} \t{description}".format(
                        index=i + 1,
                        host=device[0] + ":" if len(result) > 1 else "",
                        port=device[1]["port"],
                        description=device[1]["description"]
                        if device[1]["description"] != "n/a"
                        else "",
                    )
                )
            device_index = click.prompt(
                "Please choose a port (number in the list above)",
                type=click.Choice([str(i + 1) for i, _ in enumerate(devices)]),
            )
            device = devices[int(device_index) - 1]

        self.start_remote_monitor(device[0], device[1]["port"])

        return None

    def start_remote_monitor(self, agent, port):
        options = {"port": port}
        for key in ("baud", "parity", "rtscts", "xonxoff", "rts", "dtr"):
            options[key] = self.cmd_options[key]

        click.echo(
            "Starting Serial Monitor on {host}:{port}".format(
                host=agent, port=options["port"]
            )
        )
        d = self.agentpool.callRemote("cmd", [agent], "device.monitor", options)
        d.addCallback(self.cb_async_result)
        d.addErrback(self.cb_global_error)

    def cb_async_result(self, result):
        if len(result) != 1:
            raise pb.Error("Invalid response from Remote Cloud")
        success, value = result[0]
        if not success:
            raise pb.Error(value)

        reconnected = self._agent_id is not None
        self._agent_id, self._ac_id = value

        if reconnected:
            self.acread_data(force=True)
            self.acwrite_data("", force=True)
            return

        # start bridge
        port = reactor.listenTCP(0, self._bridge_factory)
        address = port.getHost()
        self.log.debug("Serial Bridge is started on {address!r}", address=address)
        if "sock" in self.cmd_options:
            with open(
                os.path.join(self.cmd_options["sock"], "sock"),
                mode="w",
                encoding="utf8",
            ) as fp:
                fp.write("socket://localhost:%d" % address.port)

    def client_terminal_stopped(self):
        try:
            d = self.agentpool.callRemote("acclose", self._agent_id, self._ac_id)
            d.addCallback(lambda r: self.disconnect())
            d.addErrback(self.cb_global_error)
        except (AttributeError, pb.DeadReferenceError):
            self.disconnect(exit_code=1)

    def acread_data(self, force=False):
        if force and self._d_acread:
            self._d_acread.cancel()
            self._d_acread = None

        if (
            self._d_acread and not self._d_acread.called
        ) or not self._bridge_factory.has_clients():
            return

        try:
            self._d_acread = self.agentpool.callRemote(
                "acread", self._agent_id, self._ac_id
            )
            self._d_acread.addCallback(self.cb_acread_result)
            self._d_acread.addErrback(self.cb_global_error)
        except (AttributeError, pb.DeadReferenceError):
            self.disconnect(exit_code=1)

    def cb_acread_result(self, result):
        if result is None:
            self.disconnect(exit_code=1)
        else:
            self._bridge_factory.send_to_clients(result)
            self.acread_data()

    def acwrite_data(self, data, force=False):
        if force and self._d_acwrite:
            self._d_acwrite.cancel()
            self._d_acwrite = None

        self._acwrite_buffer += data
        if len(self._acwrite_buffer) > self.MAX_BUFFER_SIZE:
            self._acwrite_buffer = self._acwrite_buffer[-1 * self.MAX_BUFFER_SIZE :]
        if (self._d_acwrite and not self._d_acwrite.called) or not self._acwrite_buffer:
            return

        data = self._acwrite_buffer
        self._acwrite_buffer = b""
        try:
            d = self.agentpool.callRemote("acwrite", self._agent_id, self._ac_id, data)
            d.addCallback(self.cb_acwrite_result)
            d.addErrback(self.cb_global_error)
        except (AttributeError, pb.DeadReferenceError):
            self.disconnect(exit_code=1)

    def cb_acwrite_result(self, result):
        assert result > 0
        if self._acwrite_buffer:
            self.acwrite_data(b"")
