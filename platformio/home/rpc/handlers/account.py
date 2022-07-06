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

from ajsonrpc.core import JSONRPC20DispatchException

from platformio.account.client import AccountClient


class AccountRPC:
    @staticmethod
    def call_client(method, *args, **kwargs):
        try:
            client = AccountClient()
            return getattr(client, method)(*args, **kwargs)
        except Exception as exc:  # pylint: disable=bare-except
            raise JSONRPC20DispatchException(
                code=4003, message="PIO Account Call Error", data=str(exc)
            ) from exc
