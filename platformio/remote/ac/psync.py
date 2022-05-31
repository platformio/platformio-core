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

import json
import os
import zlib
from io import BytesIO

from platformio.remote.ac.base import AsyncCommandBase
from platformio.remote.projectsync import PROJECT_SYNC_STAGE, ProjectSync


class ProjectSyncAsyncCmd(AsyncCommandBase):
    def __init__(self, *args, **kwargs):
        self.psync = None
        self._upstream = None
        super().__init__(*args, **kwargs)

    def start(self):
        project_dir = os.path.join(
            self.options["agent_working_dir"], "projects", self.options["id"]
        )
        self.psync = ProjectSync(project_dir)
        for name in self.options["items"]:
            self.psync.add_item(os.path.join(project_dir, name), name)

    def stop(self):
        self.psync = None
        self._upstream = None
        self._return_code = PROJECT_SYNC_STAGE.COMPLETED.value

    def ac_write(self, data):
        stage = PROJECT_SYNC_STAGE.lookupByValue(data.get("stage"))

        if stage is PROJECT_SYNC_STAGE.DBINDEX:
            self.psync.rebuild_dbindex()
            return zlib.compress(json.dumps(self.psync.get_dbindex()).encode())

        if stage is PROJECT_SYNC_STAGE.DELETE:
            return self.psync.delete_dbindex(
                json.loads(zlib.decompress(data["dbindex"]))
            )

        if stage is PROJECT_SYNC_STAGE.UPLOAD:
            if not self._upstream:
                self._upstream = BytesIO()
            self._upstream.write(data["chunk"])
            if self._upstream.tell() == data["total"]:
                self.psync.decompress_items(self._upstream)
                self._upstream = None
                return PROJECT_SYNC_STAGE.EXTRACTED.value

            return PROJECT_SYNC_STAGE.UPLOAD.value

        return None
