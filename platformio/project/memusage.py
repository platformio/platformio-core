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

import gzip
import json
import os
import time

from platformio import fs
from platformio.project.config import ProjectConfig


def get_report_dir(project_dir, env):
    with fs.cd(project_dir):
        return os.path.join(
            ProjectConfig.get_instance().get("platformio", "memusage_dir"), env
        )


def list_reports(project_dir, env):
    report_dir = get_report_dir(project_dir, env)
    if not os.path.isdir(report_dir):
        return []
    return [os.path.join(report_dir, item) for item in sorted(os.listdir(report_dir))]


def read_report(path):
    with gzip.open(path, mode="rt", encoding="utf8") as fp:
        return json.load(fp)


def save_report(project_dir, env, data):
    report_dir = get_report_dir(project_dir, env)
    if not os.path.isdir(report_dir):
        os.makedirs(report_dir)
    report_path = os.path.join(report_dir, f"{int(time.time())}.json.gz")
    with gzip.open(report_path, mode="wt", encoding="utf8") as fp:
        json.dump(data, fp)
    rotate_reports(report_dir)
    return report_path


def rotate_reports(report_dir, max_reports=100):
    reports = os.listdir(report_dir)
    if len(reports) < max_reports:
        return
    for fname in sorted(reports)[0 : len(reports) - max_reports]:
        os.remove(os.path.join(report_dir, fname))
