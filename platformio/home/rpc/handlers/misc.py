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
import time

from platformio.cache import ContentCache
from platformio.compat import aio_create_task
from platformio.home.rpc.handlers.os import OSRPC


class MiscRPC:
    async def load_latest_tweets(self, data_url):
        cache_key = ContentCache.key_from_args(data_url, "tweets")
        cache_valid = "180d"
        with ContentCache() as cc:
            cache_data = cc.get(cache_key)
            if cache_data:
                cache_data = json.loads(cache_data)
                # automatically update cache in background every 12 hours
                if cache_data["time"] < (time.time() - (3600 * 12)):
                    aio_create_task(
                        self._preload_latest_tweets(data_url, cache_key, cache_valid)
                    )
                return cache_data["result"]

        return await self._preload_latest_tweets(data_url, cache_key, cache_valid)

    @staticmethod
    async def _preload_latest_tweets(data_url, cache_key, cache_valid):
        result = json.loads((await OSRPC.fetch_content(data_url)))
        with ContentCache() as cc:
            cc.set(
                cache_key,
                json.dumps({"time": int(time.time()), "result": result}),
                cache_valid,
            )
        return result
