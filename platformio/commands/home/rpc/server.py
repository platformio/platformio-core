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

# pylint: disable=import-error

import click
import jsonrpc
from autobahn.twisted.websocket import (WebSocketServerFactory,
                                        WebSocketServerProtocol)
from jsonrpc.exceptions import JSONRPCDispatchException
from twisted.internet import defer

from platformio.compat import PY2, dump_json_to_unicode, is_bytes


class JSONRPCServerProtocol(WebSocketServerProtocol):

    def onMessage(self, payload, isBinary):  # pylint: disable=unused-argument
        # click.echo("> %s" % payload)
        response = jsonrpc.JSONRPCResponseManager.handle(
            payload, self.factory.dispatcher).data
        # if error
        if "result" not in response:
            self.sendJSONResponse(response)
            return None

        d = defer.maybeDeferred(lambda: response['result'])
        d.addCallback(self._callback, response)
        d.addErrback(self._errback, response)

        return None

    def _callback(self, result, response):
        response['result'] = result
        self.sendJSONResponse(response)

    def _errback(self, failure, response):
        if isinstance(failure.value, JSONRPCDispatchException):
            e = failure.value
        else:
            e = JSONRPCDispatchException(code=4999,
                                         message=failure.getErrorMessage())
        del response["result"]
        response['error'] = e.error._data  # pylint: disable=protected-access
        self.sendJSONResponse(response)

    def sendJSONResponse(self, response):
        # click.echo("< %s" % response)
        if "error" in response:
            click.secho("Error: %s" % response['error'], fg="red", err=True)
        response = dump_json_to_unicode(response)
        if not PY2 and not is_bytes(response):
            response = response.encode("utf-8")
        self.sendMessage(response)


class JSONRPCServerFactory(WebSocketServerFactory):

    protocol = JSONRPCServerProtocol

    def __init__(self):
        super(JSONRPCServerFactory, self).__init__()
        self.dispatcher = jsonrpc.Dispatcher()

    def addHandler(self, handler, namespace):
        self.dispatcher.build_method_map(handler, prefix="%s." % namespace)
