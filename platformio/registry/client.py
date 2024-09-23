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

# pylint: disable=too-many-arguments

from platformio import __registry_mirror_hosts__, fs
from platformio.account.client import AccountClient, AccountError
from platformio.http import HTTPClient, HTTPClientError


class RegistryClient(HTTPClient):
    def __init__(self):
        endpoints = [f"https://api.{host}" for host in __registry_mirror_hosts__]
        super().__init__(endpoints)

    @staticmethod
    def allowed_private_packages():
        private_permissions = set(
            [
                "service.registry.publish-private-tool",
                "service.registry.publish-private-platform",
                "service.registry.publish-private-library",
            ]
        )
        try:
            info = AccountClient().get_account_info() or {}
            for item in info.get("packages", []):
                if set(item.keys()) & private_permissions:
                    return True
        except AccountError:
            pass
        return False

    def publish_package(  # pylint: disable=redefined-builtin, too-many-positional-arguments
        self, owner, type, archive_path, released_at=None, private=False, notify=True
    ):
        with open(archive_path, "rb") as fp:
            return self.fetch_json_data(
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
                x_with_authorization=True,
            )

    def unpublish_package(  # pylint: disable=redefined-builtin, too-many-positional-arguments
        self, owner, type, name, version=None, undo=False
    ):
        path = "/v3/packages/%s/%s/%s" % (owner, type, name)
        if version:
            path += "/" + version
        return self.fetch_json_data(
            "delete", path, params={"undo": 1 if undo else 0}, x_with_authorization=True
        )

    def update_resource(self, urn, private):
        return self.fetch_json_data(
            "put",
            "/v3/resources/%s" % urn,
            data={"private": int(private)},
            x_with_authorization=True,
        )

    def grant_access_for_resource(self, urn, client, level):
        return self.fetch_json_data(
            "put",
            "/v3/resources/%s/access" % urn,
            data={"client": client, "level": level},
            x_with_authorization=True,
        )

    def revoke_access_from_resource(self, urn, client):
        return self.fetch_json_data(
            "delete",
            "/v3/resources/%s/access" % urn,
            data={"client": client},
            x_with_authorization=True,
        )

    def list_resources(self, owner):
        return self.fetch_json_data(
            "get",
            "/v3/resources",
            params={"owner": owner} if owner else None,
            x_cache_valid="1h",
            x_with_authorization=True,
        )

    def list_packages(self, query=None, qualifiers=None, page=None, sort=None):
        search_query = []
        if qualifiers:
            valid_qualifiers = (
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
            assert set(qualifiers.keys()) <= set(valid_qualifiers)
            for name, values in qualifiers.items():
                for value in set(
                    values if isinstance(values, (list, tuple)) else [values]
                ):
                    search_query.append('%s:"%s"' % (name[:-1], value))
        if query:
            search_query.append(query)
        params = dict(query=" ".join(search_query))
        if page:
            params["page"] = int(page)
        if sort:
            params["sort"] = sort
        return self.fetch_json_data(
            "get",
            "/v3/search",
            params=params,
            x_cache_valid="1h",
            x_with_authorization=self.allowed_private_packages(),
        )

    def get_package(
        self, typex, owner, name, version=None, extra_path=None
    ):  # pylint: disable=too-many-positional-arguments
        try:
            return self.fetch_json_data(
                "get",
                "/v3/packages/{owner}/{type}/{name}{extra_path}".format(
                    type=typex,
                    owner=owner.lower(),
                    name=name.lower(),
                    extra_path=extra_path or "",
                ),
                params=dict(version=version) if version else None,
                x_cache_valid="1h",
                x_with_authorization=self.allowed_private_packages(),
            )
        except HTTPClientError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return None
            raise exc
