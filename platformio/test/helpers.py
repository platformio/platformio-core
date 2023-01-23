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
from fnmatch import fnmatch

from platformio.test.exception import TestDirNotExistsError
from platformio.test.result import TestSuite


def list_test_names(project_config):
    test_dir = project_config.get("platformio", "test_dir")
    if not os.path.isdir(test_dir):
        raise TestDirNotExistsError(test_dir)
    names = []
    for root, _, __ in os.walk(test_dir, followlinks=True):
        if not os.path.basename(root).startswith("test_"):
            continue
        names.append(os.path.relpath(root, test_dir).replace("\\", "/"))
    if not names:
        names = ["*"]
    return names


def list_test_suites(project_config, environments, filters, ignores):
    result = []
    test_dir = project_config.get("platformio", "test_dir")
    default_envs = project_config.default_envs()
    test_names = list_test_names(project_config)
    for env_name in project_config.envs():
        for test_name in test_names:

            # filter and ignore patterns
            patterns = dict(filter=list(filters), ignore=list(ignores))
            for key, value in patterns.items():
                if value:  # overridden from CLI
                    continue
                patterns[key].extend(  # pylint: disable=unnecessary-dict-index-lookup
                    project_config.get(f"env:{env_name}", f"test_{key}", [])
                )

            skip_conditions = [
                environments and env_name not in environments,
                not environments and default_envs and env_name not in default_envs,
                test_name != "*"
                and patterns["filter"]
                and not any(fnmatch(test_name, p) for p in patterns["filter"]),
                test_name != "*"
                and any(fnmatch(test_name, p) for p in patterns["ignore"]),
            ]
            result.append(
                TestSuite(
                    env_name,
                    test_name,
                    finished=any(skip_conditions),
                    test_dir=os.path.abspath(
                        test_dir
                        if test_name == "*"
                        else os.path.join(test_dir, test_name)
                    ),
                )
            )
    return result
