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

from platformio.package.commands.install import install_project_env_dependencies
from platformio.platform.factory import PlatformFactory
from platformio.project.exception import UndefinedEnvPlatformError
from platformio.test.runners.base import CTX_META_TEST_RUNNING_NAME

# pylint: disable=too-many-instance-attributes


class EnvironmentProcessor:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        cmd_ctx,
        name,
        config,
        targets,
        upload_port,
        jobs,
        program_args,
        silent,
        verbose,
    ):
        self.cmd_ctx = cmd_ctx
        self.name = name
        self.config = config
        self.targets = [str(t) for t in targets]
        self.upload_port = upload_port
        self.jobs = jobs
        self.program_args = program_args
        self.silent = silent
        self.verbose = verbose
        self.options = config.items(env=name, as_dict=True)

    def get_build_variables(self):
        variables = dict(
            pioenv=self.name,
            project_config=self.config.path,
            program_args=self.program_args,
        )

        if CTX_META_TEST_RUNNING_NAME in self.cmd_ctx.meta:
            variables["piotest_running_name"] = self.cmd_ctx.meta[
                CTX_META_TEST_RUNNING_NAME
            ]

        if self.upload_port:
            # override upload port with a custom from CLI
            variables["upload_port"] = self.upload_port
        return variables

    def get_build_targets(self):
        return (
            self.targets
            if self.targets
            else self.config.get("env:" + self.name, "targets", [])
        )

    def process(self):
        if "platform" not in self.options:
            raise UndefinedEnvPlatformError(self.name)

        build_vars = self.get_build_variables()
        build_targets = list(self.get_build_targets())

        # skip monitor target, we call it above
        if "monitor" in build_targets:
            build_targets.remove("monitor")

        if not set(["clean", "cleanall"]) & set(build_targets):
            install_project_env_dependencies(
                self.name,
                {
                    "project_targets": build_targets,
                    "piotest_running_name": build_vars.get("piotest_running_name"),
                },
            )

        result = PlatformFactory.new(self.options["platform"], autoinstall=True).run(
            build_vars, build_targets, self.silent, self.verbose, self.jobs
        )
        return result["returncode"] == 0
