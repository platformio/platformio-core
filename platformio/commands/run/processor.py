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

from platformio import exception, telemetry
from platformio.commands.platform import platform_install as cmd_platform_install
from platformio.commands.test.processor import CTX_META_TEST_RUNNING_NAME
from platformio.managers.platform import PlatformFactory
from platformio.project.exception import UndefinedEnvPlatformError

# pylint: disable=too-many-instance-attributes


class EnvironmentProcessor(object):
    def __init__(  # pylint: disable=too-many-arguments
        self, cmd_ctx, name, config, targets, upload_port, silent, verbose, jobs
    ):
        self.cmd_ctx = cmd_ctx
        self.name = name
        self.config = config
        self.targets = [str(t) for t in targets]
        self.upload_port = upload_port
        self.silent = silent
        self.verbose = verbose
        self.jobs = jobs
        self.options = config.items(env=name, as_dict=True)

    def get_build_variables(self):
        variables = {"pioenv": self.name, "project_config": self.config.path}

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

        telemetry.send_run_environment(self.options, build_targets)

        # skip monitor target, we call it above
        if "monitor" in build_targets:
            build_targets.remove("monitor")

        try:
            p = PlatformFactory.newPlatform(self.options["platform"])
        except exception.UnknownPlatform:
            self.cmd_ctx.invoke(
                cmd_platform_install,
                platforms=[self.options["platform"]],
                skip_default_package=True,
            )
            p = PlatformFactory.newPlatform(self.options["platform"])

        result = p.run(build_vars, build_targets, self.silent, self.verbose, self.jobs)
        return result["returncode"] == 0
