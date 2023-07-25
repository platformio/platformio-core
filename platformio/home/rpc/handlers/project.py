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

import os
from pathlib import Path

import semantic_version

from platformio import app, fs
from platformio.home.rpc.handlers.base import BaseRPCHandler
from platformio.package.manager.platform import PlatformPackageManager
from platformio.platform.factory import PlatformFactory
from platformio.project.config import ProjectConfig
from platformio.project.helpers import get_project_dir
from platformio.project.integration.generator import ProjectGenerator


class ProjectRPC(BaseRPCHandler):
    NAMESPACE = "project"

    @staticmethod
    def config_call(init_kwargs, method, *args):
        assert isinstance(init_kwargs, dict)
        assert "path" in init_kwargs
        if os.path.isdir(init_kwargs["path"]):
            project_dir = init_kwargs["path"]
            init_kwargs["path"] = os.path.join(init_kwargs["path"], "platformio.ini")
        elif os.path.isfile(init_kwargs["path"]):
            project_dir = get_project_dir()
        else:
            project_dir = os.path.dirname(init_kwargs["path"])
        with fs.cd(project_dir):
            return getattr(ProjectConfig(**init_kwargs), method)(*args)

    async def init(self, configuration, options=None):
        project_dir = os.path.join(configuration["location"], configuration["name"])
        if not os.path.isdir(project_dir):
            os.makedirs(project_dir)

        args = ["project", "init", "-d", project_dir]
        ide = app.get_session_var("caller_id")
        if ide in ProjectGenerator.get_supported_ides():
            args.extend(["--ide", ide])

        exec_options = options.get("exec", {})
        if configuration.get("example"):
            await self.factory.notify_clients(
                method=exec_options.get("stdoutNotificationMethod"),
                params=["Copying example files...\n"],
                actor="frontend",
            )
            await self._pre_init_example(configuration, project_dir)
        else:
            args.extend(self._pre_init_empty(configuration))

        return await self.factory.manager.dispatcher["core.exec"](
            args, options=exec_options
        )

    @staticmethod
    def _pre_init_empty(configuration):
        project_options = []
        platform = configuration["platform"]
        board_id = configuration.get("board", {}).get("id")
        env_name = board_id or platform["name"]
        if configuration.get("description"):
            project_options.append(("description", configuration.get("description")))
        try:
            v = semantic_version.Version(platform.get("version"))
            assert not v.prerelease
            project_options.append(
                ("platform", "{name} @ ^{version}".format(**platform))
            )
        except (AssertionError, ValueError):
            project_options.append(
                ("platform", "{name} @ {version}".format(**platform))
            )
        if board_id:
            project_options.append(("board", board_id))
        if configuration.get("framework"):
            project_options.append(("framework", configuration["framework"]["name"]))

        args = ["-e", env_name, "--sample-code"]
        for name, value in project_options:
            args.extend(["-O", f"{name}={value}"])
        return args

    async def _pre_init_example(self, configuration, project_dir):
        for item in configuration["example"]["files"]:
            p = Path(project_dir).joinpath(item["path"])
            if not p.parent.is_dir():
                p.parent.mkdir(parents=True)
            p.write_text(
                await self.factory.manager.dispatcher["os.request_content"](
                    item["url"]
                ),
                encoding="utf-8",
            )
        return []

    @staticmethod
    def configuration(project_dir, env):
        with fs.cd(project_dir):
            config = ProjectConfig.get_instance()
            config.validate(envs=[env])
            platform = PlatformFactory.from_env(env, autoinstall=True)
            platform_pkg = PlatformPackageManager().get_package(platform.get_dir())
            board_id = config.get(f"env:{env}", "board", None)

            # frameworks
            frameworks = []
            for name in config.get(f"env:{env}", "framework", []):
                if name not in platform.frameworks:
                    continue
                f_pkg_name = platform.frameworks[name].get("package")
                if not f_pkg_name:
                    continue
                f_pkg = platform.get_package(f_pkg_name)
                if not f_pkg:
                    continue
                f_manifest = platform.pm.load_manifest(f_pkg)
                frameworks.append(
                    dict(
                        name=name,
                        title=f_manifest.get("title"),
                        version=str(f_pkg.metadata.version),
                    )
                )

            return dict(
                platform=dict(
                    ownername=platform_pkg.metadata.spec.owner
                    if platform_pkg.metadata.spec
                    else None,
                    name=platform.name,
                    title=platform.title,
                    version=str(platform_pkg.metadata.version),
                ),
                board=platform.board_config(board_id).get_brief_data()
                if board_id
                else None,
                frameworks=frameworks or None,
            )
