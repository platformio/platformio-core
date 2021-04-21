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

from platformio import __registry_api__, fs
from platformio.clients.account import AccountClient
from platformio.clients.http import HTTPClient, HTTPClientError

# pylint: disable=too-many-arguments


class RegistryClient(HTTPClient):
    def __init__(self):
        super(RegistryClient, self).__init__(__registry_api__)

    def send_auth_request(self, *args, **kwargs):
        headers = kwargs.get("headers", {})
        if "Authorization" not in headers:
            token = AccountClient().fetch_authentication_token()
            headers["Authorization"] = "Bearer %s" % token
        kwargs["headers"] = headers
        return self.fetch_json_data(*args, **kwargs)

    def publish_package(  # pylint: disable=redefined-builtin
        self, owner, type, archive_path, released_at=None, private=False, notify=True
    ):
        with open(archive_path, "rb") as fp:
            return self.send_auth_request(
                "post",
                "/v3/packages/%s/%s" % (owner, type),
                params={
                    "private": 1 if private else 0,
                    "notify": 1 if notify else 0,
                    "released_at": released_at,
                },
                headers={
                    "Content-Type": "application/octet-stream",
                    "X-PIO-Content-SHA256": fs.calculate_file_hashsum(
                        "sha256", archive_path
                    ),
                },
                data=fp,
            )

    def unpublish_package(  # pylint: disable=redefined-builtin
        self, owner, type, name, version=None, undo=False
    ):
        path = "/v3/packages/%s/%s/%s" % (owner, type, name)
        if version:
            path += "/" + version
        return self.send_auth_request(
            "delete",
            path,
            params={"undo": 1 if undo else 0},
        )

    def update_resource(self, urn, private):
        return self.send_auth_request(
            "put",
            "/v3/resources/%s" % urn,
            data={"private": int(private)},
        )

    def grant_access_for_resource(self, urn, client, level):
        return self.send_auth_request(
            "put",
            "/v3/resources/%s/access" % urn,
            data={"client": client, "level": level},
        )

    def revoke_access_from_resource(self, urn, client):
        return self.send_auth_request(
            "delete",
            "/v3/resources/%s/access" % urn,
            data={"client": client},
        )

    def list_resources(self, owner):
        return self.send_auth_request(
            "get", "/v3/resources", params={"owner": owner} if owner else None
        )

    def list_packages(self, query=None, filters=None, page=None):
        assert query or filters
        search_query = []
        if filters:
            valid_filters = (
                "authors",
                "keywords",
                "frameworks",
                "platforms",
                "headers",
                "ids",
                "names",
                "owners",
                "types",
            )
            assert set(filters.keys()) <= set(valid_filters)
            for name, values in filters.items():
                for value in set(
                    values if isinstance(values, (list, tuple)) else [values]
                ):
                    search_query.append('%s:"%s"' % (name[:-1], value))
        if query:
            search_query.append(query)
        params = dict(query=" ".join(search_query))
        if page:
            params["page"] = int(page)
        return self.fetch_json_data(
            "get", "/v3/packages", params=params, cache_valid="1h"
        )

    def get_package(self, type_, owner, name, version=None):
        try:
            return self.fetch_json_data(
                "get",
                "/v3/packages/{owner}/{type}/{name}".format(
                    type=type_, owner=owner.lower(), name=name.lower()
                ),
                params=dict(version=version) if version else None,
                cache_valid="1h",
            )
        except HTTPClientError as e:
            if e.response is not None and e.response.status_code == 404:
                return None
            raise e
