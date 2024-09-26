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
from platformio.run.helpers import KNOWN_ALLCLEAN_TARGETS
from platformio.test.runners.base import CTX_META_TEST_RUNNING_NAME

# pylint: disable=too-many-instance-attributes


class EnvironmentProcessor:
    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
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
        self.targets = targets
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

    def process(self):
        if "platform" not in self.options:
            raise UndefinedEnvPlatformError(self.name)

        build_vars = self.get_build_variables()
        is_clean = set(KNOWN_ALLCLEAN_TARGETS) & set(self.targets)
        build_targets = [t for t in self.targets if t not in KNOWN_ALLCLEAN_TARGETS]

        # pre-clean
        if is_clean:
            result = PlatformFactory.from_env(
                self.name, targets=self.targets, autoinstall=True
            ).run(build_vars, self.targets, self.silent, self.verbose, self.jobs)
            if not build_targets:
                return result["returncode"] == 0

        install_project_env_dependencies(
            self.name,
            {
                "project_targets": self.targets,
                "piotest_running_name": build_vars.get("piotest_running_name"),
            },
        )
        result = PlatformFactory.from_env(
            self.name, targets=build_targets, autoinstall=True
        ).run(build_vars, build_targets, self.silent, self.verbose, self.jobs)
        return result["returncode"] == 0
