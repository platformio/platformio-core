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

import functools

from platformio.home.rpc.handlers.base import BaseRPCHandler
from platformio.project import memusage


class MemUsageRPC(BaseRPCHandler):
    NAMESPACE = "memusage"

    async def summary(self, project_dir, env, options=None):
        options = options or {}
        existing_reports = memusage.list_reports(project_dir, env)
        current_report = previous_report = None
        if options.get("cached") and existing_reports:
            current_report = memusage.read_report(existing_reports[-1])
            if len(existing_reports) > 1:
                previous_report = memusage.read_report(existing_reports[-2])
        else:
            if existing_reports:
                previous_report = memusage.read_report(existing_reports[-1])
            await self.factory.manager.dispatcher["core.exec"](
                ["run", "-d", project_dir, "-e", env, "-t", "__memusage"],
                options=options.get("exec"),
                raise_exception=True,
            )
            current_report = memusage.read_report(
                memusage.list_reports(project_dir, env)[-1]
            )

        max_top_items = 10
        return dict(
            timestamp=dict(
                current=current_report["timestamp"],
                previous=previous_report["timestamp"] if previous_report else None,
            ),
            device=current_report["device"],
            trend=dict(
                current=current_report["memory"]["total"],
                previous=previous_report["memory"]["total"]
                if previous_report
                else None,
            ),
            top=dict(
                files=self._calculate_top_files(current_report["memory"]["files"])[
                    0:max_top_items
                ],
                symbols=self._calculate_top_symbols(current_report["memory"]["files"])[
                    0:max_top_items
                ],
                sections=sorted(
                    current_report["memory"]["total"]["sections"].values(),
                    key=lambda item: item["size"],
                    reverse=True,
                )[0:max_top_items],
            ),
        )

    @staticmethod
    def _calculate_top_files(items):
        return [
            {"path": item["path"], "ram": item["ram_size"], "flash": item["flash_size"]}
            for item in sorted(
                items,
                key=lambda item: item["ram_size"] + item["flash_size"],
                reverse=True,
            )
        ]

    @staticmethod
    def _calculate_top_symbols(files):
        symbols = functools.reduce(
            lambda result, filex: result
            + [
                {
                    "name": s["name"],
                    "type": s["type"],
                    "size": s["size"],
                    "file": filex["path"],
                    "line": s.get("line"),
                }
                for s in filex["symbols"]
            ],
            files,
            [],
        )
        return sorted(symbols, key=lambda item: item["size"], reverse=True)
