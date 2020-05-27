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

import jsonrpc  # pylint: disable=import-error

from platformio.clients.account import AccountClient


class AccountRPC(object):
    @staticmethod
    def call_client(method, *args, **kwargs):
        try:
            client = AccountClient()
            return getattr(client, method)(*args, **kwargs)
        except Exception as e:  # pylint: disable=bare-except
            raise jsonrpc.exceptions.JSONRPCDispatchException(
                code=4003, message="PIO Account Call Error", data=str(e)
            )
