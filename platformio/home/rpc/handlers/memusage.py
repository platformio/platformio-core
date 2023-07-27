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
import os

from platformio.home.rpc.handlers.base import BaseRPCHandler
from platformio.project import memusage


class MemUsageRPC(BaseRPCHandler):
    NAMESPACE = "memusage"

    async def profile(self, project_dir, env, options=None):
        options = options or {}
        report_dir = memusage.get_report_dir(project_dir, env)
        if options.get("lazy"):
            existing_reports = memusage.list_reports(report_dir)
            if existing_reports:
                return existing_reports[-1]
        await self.factory.manager.dispatcher["core.exec"](
            ["run", "-d", project_dir, "-e", env, "-t", "__memusage"],
            options=options.get("exec"),
            raise_exception=True,
        )
        return memusage.list_reports(report_dir)[-1]

    def summary(self, report_path):
        max_top_items = 10
        report_dir = os.path.dirname(report_path)
        existing_reports = memusage.list_reports(report_dir)
        current_report = memusage.read_report(report_path)
        previous_report = None
        try:
            current_index = existing_reports.index(report_path)
            if current_index > 0:
                previous_report = memusage.read_report(
                    existing_reports[current_index - 1]
                )
        except ValueError:
            pass

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
                    current_report["memory"]["sections"].values(),
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

    async def history(self, project_dir, env, nums=10):
        result = []
        report_dir = memusage.get_report_dir(project_dir, env)
        reports = memusage.list_reports(report_dir)[nums * -1 :]
        for path in reports:
            data = memusage.read_report(path)
            result.append(
                {
                    "timestamp": data["timestamp"],
                    "ram": data["memory"]["total"]["ram_size"],
                    "flash": data["memory"]["total"]["flash_size"],
                }
            )
        return result
