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

from twisted.cred import credentials  # pylint: disable=import-error
from twisted.internet import defer, protocol, reactor  # pylint: disable=import-error
from twisted.spread import pb  # pylint: disable=import-error

from platformio.account.client import AccountClient
from platformio.app import get_host_id


class RemoteClientFactory(pb.PBClientFactory, protocol.ReconnectingClientFactory):
    def clientConnectionMade(self, broker):
        if self.sslContextFactory and not self.sslContextFactory.certificate_verified:
            self.remote_client.log.error(
                "A remote cloud could not prove that its security certificate is "
                "from {host}. This may cause a misconfiguration or an attacker "
                "intercepting your connection.",
                host=self.sslContextFactory.host,
            )
            return self.remote_client.disconnect()
        pb.PBClientFactory.clientConnectionMade(self, broker)
        protocol.ReconnectingClientFactory.resetDelay(self)
        self.remote_client.log.info("Successfully connected")
        self.remote_client.log.info("Authenticating")

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
                auth_token.encode(),
                get_host_id().encode(),
            ),
            client=self.remote_client,
        )
        d.addCallback(self.remote_client.cb_client_authorization_made)
        d.addErrback(self.clientAuthorizationFailed)
        return d

    def clientAuthorizationFailed(self, err):
        AccountClient.delete_local_session()
        self.remote_client.cb_client_authorization_failed(err)

    def clientConnectionFailed(self, connector, reason):
        self.remote_client.log.warn(
            "Could not connect to PIO Remote Cloud. Reconnecting..."
        )
        self.remote_client.cb_disconnected(reason)
        protocol.ReconnectingClientFactory.clientConnectionFailed(
            self, connector, reason
        )

    def clientConnectionLost(  # pylint: disable=arguments-differ
        self, connector, unused_reason
    ):
        if not reactor.running:
            self.remote_client.log.info("Successfully disconnected")
            return
        self.remote_client.log.warn(
            "Connection is lost to PIO Remote Cloud. Reconnecting"
        )
        pb.PBClientFactory.clientConnectionLost(
            self, connector, unused_reason, reconnecting=1
        )
        self.remote_client.cb_disconnected(unused_reason)
        protocol.ReconnectingClientFactory.clientConnectionLost(
            self, connector, unused_reason
        )
