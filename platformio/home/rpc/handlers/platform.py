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

from platformio.home.rpc.handlers.base import BaseRPCHandler
from platformio.package.manager.platform import PlatformPackageManager
from platformio.platform.factory import PlatformFactory


class PlatformRPC(BaseRPCHandler):
    @staticmethod
    def list_installed(options=None):
        result = []
        options = options or {}

        def _matchSearchQuery(p):
            searchQuery = options.get("searchQuery")
            if not searchQuery:
                return True
            content_blocks = [p.name, p.title, p.description]
            if p.frameworks:
                content_blocks.append(" ".join(p.frameworks.keys()))
            for board in p.get_boards().values():
                board_data = board.get_brief_data()
                for key in ("id", "mcu", "vendor"):
                    content_blocks.append(board_data.get(key))
            return searchQuery.strip() in " ".join(content_blocks)

        pm = PlatformPackageManager()
        for pkg in pm.get_installed():
            p = PlatformFactory.new(pkg)
            if not _matchSearchQuery(p):
                continue
            result.append(
                dict(
                    __pkg_path=pkg.path,
                    __pkg_meta=pkg.metadata.as_dict(),
                    name=p.name,
                    title=p.title,
                    description=p.description,
                )
            )
        return result

    @staticmethod
    def get_boards(spec):
        p = PlatformFactory.new(spec)
        return sorted(
            [b.get_brief_data() for b in p.get_boards().values()],
            key=lambda item: item["name"],
        )
