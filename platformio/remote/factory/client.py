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

from twisted.cred import credentials  # type: ignore
from twisted.internet import defer, protocol, reactor  # type: ignore
from twisted.spread import pb  # type: ignore

from platformio.account.client import AccountClient
from platformio.app import get_host_id


class RemoteClientFactory(pb.PBClientFactory, protocol.ReconnectingClientFactory):
    def clientConnectionMade(self, broker):
        if self.sslContextFactory and not self.sslContextFactory.certificate_verified:  # type: ignore
            self.remote_client.log.error(  # type: ignore
                "A remote cloud could not prove that its security certificate is "
                "from {host}. This may cause a misconfiguration or an attacker "
                "intercepting your connection.",
                host=self.sslContextFactory.host,  # type: ignore
            )
            return self.remote_client.disconnect()  # type: ignore
        pb.PBClientFactory.clientConnectionMade(self, broker)
        protocol.ReconnectingClientFactory.resetDelay(self)
        self.remote_client.log.info("Successfully connected")  # type: ignore
        self.remote_client.log.info("Authenticating")  # type: ignore

        auth_token = None
        try:
            auth_token = AccountClient().fetch_authentication_token()
        except Exception as exc:  # pylint:disable=broad-except
            d = defer.Deferred()
            d.addErrback(self.clientAuthorizationFailed)
            d.errback(pb.Error(exc))
            return d

        d = self.login(
            credentials.UsernamePassword(
                auth_token.encode(),  # type: ignore
                get_host_id().encode(),
            ),
            client=self.remote_client,  # type: ignore
        )
        d.addCallback(self.remote_client.cb_client_authorization_made)  # type: ignore
        d.addErrback(self.clientAuthorizationFailed)
        return d

    def clientAuthorizationFailed(self, err):
        AccountClient.delete_local_session()
        self.remote_client.cb_client_authorization_failed(err)  # type: ignore

    def clientConnectionFailed(self, connector, reason):
        self.remote_client.log.warn(  # type: ignore
            "Could not connect to PIO Remote Cloud. Reconnecting..."
        )
        self.remote_client.cb_disconnected(reason)  # type: ignore
        protocol.ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason
        )

    def clientConnectionLost(  # pylint: disable=arguments-differ
        self, connector, unused_reason
    ):
        if not reactor.running:  # type: ignore
            self.remote_client.log.info("Successfully disconnected")  # type: ignore
            return
        self.remote_client.log.warn(  # type: ignore
            "Connection is lost to PIO Remote Cloud. Reconnecting"
        )
        pb.PBClientFactory.clientConnectionLost(
            self, connector, unused_reason, reconnecting=1
        )
        self.remote_client.cb_disconnected(unused_reason)  # type: ignore
        protocol.ReconnectingClientFactory.clientConnectionLost(
            self, connector, unused_reason
        )
