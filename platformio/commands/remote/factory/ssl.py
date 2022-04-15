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

import certifi
from OpenSSL import SSL  # pylint: disable=import-error
from twisted.internet import ssl  # pylint: disable=import-error


class SSLContextFactory(ssl.ClientContextFactory):
    def __init__(self, host):
        self.host = host
        self.certificate_verified = False

    def getContext(self):
        ctx = super().getContext()
        ctx.set_verify(
            SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, self.verifyHostname
        )
        ctx.load_verify_locations(certifi.where())
        return ctx

    def verifyHostname(  # pylint: disable=unused-argument,too-many-arguments
        self, connection, x509, errno, depth, status
    ):
        cn = x509.get_subject().commonName
        if cn.startswith("*"):
            cn = cn[1:]
        if self.host.endswith(cn):
            self.certificate_verified = True
        return status
