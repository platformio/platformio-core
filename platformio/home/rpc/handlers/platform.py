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

import os.path

from platformio.compat import aio_to_thread
from platformio.home.rpc.handlers.base import BaseRPCHandler
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.manifest.parser import ManifestParserFactory
from platformio.package.meta import PackageSpec
from platformio.platform.factory import PlatformFactory


class PlatformRPC(BaseRPCHandler):
    async def fetch_platforms(self, search_query=None, page=0, force_installed=False):
        if force_installed:
            return {
                "items": await aio_to_thread(
                    self._load_installed_platforms, search_query
                )
            }

        search_result = await self.factory.manager.dispatcher["registry.call_client"](
            method="list_packages",
            query=search_query,
            qualifiers={
                "types": ["platform"],
            },
            page=page,
        )
        return {
            "page": search_result["page"],
            "limit": search_result["limit"],
            "total": search_result["total"],
            "items": [
                {
                    "id": item["id"],
                    "ownername": item["owner"]["username"],
                    "name": item["name"],
                    "version": item["version"]["name"],
                    "description": item["description"],
                    "tier": item["tier"],
                }
                for item in search_result["items"]
            ],
        }

    @staticmethod
    def _load_installed_platforms(search_query=None):
        search_query = (search_query or "").strip()

        def _matchSearchQuery(p):
            content_blocks = [p.name, p.title, p.description]
            if p.frameworks:
                content_blocks.append(" ".join(p.frameworks.keys()))
            for board in p.get_boards().values():
                board_data = board.get_brief_data()
                for key in ("id", "mcu", "vendor"):
                    content_blocks.append(board_data.get(key))
            return search_query in " ".join(content_blocks)

        items = []
        pm = PlatformPackageManager()
        for pkg in pm.get_installed():
            p = PlatformFactory.new(pkg)
            if search_query and not _matchSearchQuery(p):
                continue
            items.append(
                {
                    "__pkg_path": pkg.path,
                    "ownername": pkg.metadata.spec.owner if pkg.metadata.spec else None,
                    "name": p.name,
                    "version": str(pkg.metadata.version),
                    "title": p.title,
                    "description": p.description,
                }
            )
        return items

    async def fetch_boards(self, platform_spec):
        spec = PackageSpec(platform_spec)
        if spec.owner:
            return await self.factory.manager.dispatcher["registry.call_client"](
                method="get_package",
                typex="platform",
                owner=spec.owner,
                name=spec.name,
                extra_path="/boards",
            )
        return await aio_to_thread(self._load_installed_boards, spec)

    @staticmethod
    def _load_installed_boards(platform_spec):
        p = PlatformFactory.new(platform_spec)
        return sorted(
            [b.get_brief_data() for b in p.get_boards().values()],
            key=lambda item: item["name"],
        )

    async def fetch_examples(self, platform_spec):
        spec = PackageSpec(platform_spec)
        if spec.owner:
            return await self.factory.manager.dispatcher["registry.call_client"](
                method="get_package",
                typex="platform",
                owner=spec.owner,
                name=spec.name,
                extra_path="/examples",
            )
        return await aio_to_thread(self._load_installed_examples, spec)

    @staticmethod
    def _load_installed_examples(platform_spec):
        platform = PlatformFactory.new(platform_spec)
        platform_dir = platform.get_dir()
        parser = ManifestParserFactory.new_from_dir(platform_dir)
        result = parser.as_dict().get("examples") or []
        for example in result:
            example["files"] = [
                {
                    "path": item,
                    "url": (
                        "file://%s"
                        + os.path.join(platform_dir, "examples", example["name"], item)
                    ),
                }
                for item in example["files"]
            ]
        return result
