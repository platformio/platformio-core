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
from typing import Callable, Optional
from urllib.parse import urlparse

from platformio import __registry_mirror_hosts__
from platformio.cache import ContentCache
from platformio.exception import UserSideException
from platformio.http import HTTPClient
from platformio.registry.client import RegistryClient


class RegistryFileMirrorIterator:
    HTTP_CLIENT_INSTANCES = {}

    def __init__(
        self,
        download_url: str,
        get_resume_offset: Optional[Callable[[], int]] = None,
    ) -> None:
        self.download_url = download_url
        # bytes of the partial the client will resume from; sent as a hint
        self.get_resume_offset = get_resume_offset
        self.mirror: Optional[str] = None  # X-PIO-Mirror of the last result
        self._url_parts = urlparse(download_url)
        self._mirror = "%s://%s" % (self._url_parts.scheme, self._url_parts.netloc)
        self._visited_mirrors = []

    def __iter__(self):  # pylint: disable=non-iterator-returned
        return self

    def __next__(self):
        cache_key = ContentCache.key_from_args(
            "head", self.download_url, self._visited_mirrors
        )
        resume_offset = self.get_resume_offset() if self.get_resume_offset else 0
        with ContentCache("http") as cc:
            # the registry must see a resume, so a cached result is not used
            result = cc.get(cache_key) if not resume_offset else None
            if result is not None:
                try:
                    headers = json.loads(result)
                    mirror = headers.get("X-PIO-Mirror")
                    # Only use the cached entry if it identifies a mirror we
                    # have not already tried. Without this, a cached redirect
                    # to a failing mirror would be returned forever because
                    # _visited_mirrors never advances on the cache-hit path.
                    if mirror and mirror not in self._visited_mirrors:
                        self._visited_mirrors.append(mirror)
                        self.mirror = mirror
                        return (
                            headers["Location"],
                            headers["X-PIO-Content-SHA256"],
                        )
                except (ValueError, KeyError):
                    pass

            params = {}
            if self._visited_mirrors:
                params["bypass"] = ",".join(self._visited_mirrors)
            if resume_offset:
                params["resume"] = resume_offset
            http = self.get_http_client()
            response = http.send_request(
                "head",
                self._url_parts.path,
                allow_redirects=False,
                params=params or None,
                x_with_authorization=RegistryClient.allowed_private_packages(),
            )
            if response.status_code == 429:
                raise UserSideException(
                    "Download limit exceeded. Try again in 24 hours. "
                    "If this persists, contact <contact@platformio.org>"
                )
            stop_conditions = [
                response.status_code not in (302, 307),
                not response.headers.get("Location"),
                not response.headers.get("X-PIO-Mirror"),
                response.headers.get("X-PIO-Mirror") in self._visited_mirrors,
            ]
            if any(stop_conditions):
                raise StopIteration
            self.mirror = response.headers.get("X-PIO-Mirror")
            self._visited_mirrors.append(self.mirror)
            cc.set(
                cache_key,
                json.dumps(
                    {
                        "Location": response.headers.get("Location"),
                        "X-PIO-Content-SHA256": response.headers.get(
                            "X-PIO-Content-SHA256"
                        ),
                        "X-PIO-Mirror": response.headers.get("X-PIO-Mirror"),
                    }
                ),
                "1h",
            )
            return (
                response.headers.get("Location"),
                response.headers.get("X-PIO-Content-SHA256"),
            )

    def get_http_client(self):
        if self._mirror not in RegistryFileMirrorIterator.HTTP_CLIENT_INSTANCES:
            endpoints = [self._mirror]
            for host in __registry_mirror_hosts__:
                endpoint = f"https://dl.{host}"
                if endpoint not in endpoints:
                    endpoints.append(endpoint)
            RegistryFileMirrorIterator.HTTP_CLIENT_INSTANCES[self._mirror] = HTTPClient(
                endpoints
            )
        return RegistryFileMirrorIterator.HTTP_CLIENT_INSTANCES[self._mirror]
