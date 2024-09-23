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

import hashlib
import json
import os
import zlib
from io import BytesIO

from twisted.spread import pb  # pylint: disable=import-error

from platformio import fs
from platformio.compat import hashlib_encode_data
from platformio.project.config import ProjectConfig
from platformio.remote.client.async_base import AsyncClientBase
from platformio.remote.projectsync import PROJECT_SYNC_STAGE, ProjectSync


class RunOrTestClient(AsyncClientBase):
    MAX_ARCHIVE_SIZE = 50 * 1024 * 1024  # 50Mb
    UPLOAD_CHUNK_SIZE = 256 * 1024  # 256Kb

    PSYNC_SRC_EXTS = [
        "c",
        "cpp",
        "S",
        "spp",
        "SPP",
        "sx",
        "s",
        "asm",
        "ASM",
        "h",
        "hpp",
        "ipp",
        "ino",
        "pde",
        "json",
        "properties",
    ]

    PSYNC_SKIP_DIRS = (".git", ".svn", ".hg", "example", "examples", "test", "tests")

    def __init__(self, *args, **kwargs):
        AsyncClientBase.__init__(self, *args, **kwargs)
        self.project_id = self.generate_project_id(self.options["project_dir"])
        self.psync = ProjectSync(self.options["project_dir"])

    def generate_project_id(self, path):
        h = hashlib.sha1(hashlib_encode_data(self.id))
        h.update(hashlib_encode_data(path))
        return "%s-%s" % (os.path.basename(path), h.hexdigest())

    def add_project_items(self, psync):
        with fs.cd(self.options["project_dir"]):
            cfg = ProjectConfig.get_instance(
                os.path.join(self.options["project_dir"], "platformio.ini")
            )
            psync.add_item(cfg.path, "platformio.ini")
            psync.add_item(cfg.get("platformio", "shared_dir"), "shared")
            psync.add_item(cfg.get("platformio", "boards_dir"), "boards")

            if self.options["force_remote"]:
                self._add_project_source_items(cfg, psync)
            else:
                self._add_project_binary_items(cfg, psync)

            if self.command == "test":
                psync.add_item(cfg.get("platformio", "test_dir"), "test")

    def _add_project_source_items(self, cfg, psync):
        psync.add_item(cfg.get("platformio", "lib_dir"), "lib")
        psync.add_item(
            cfg.get("platformio", "include_dir"),
            "include",
            cb_filter=self._cb_tarfile_filter,
        )
        psync.add_item(
            cfg.get("platformio", "src_dir"), "src", cb_filter=self._cb_tarfile_filter
        )
        if set(["buildfs", "uploadfs", "uploadfsota"]) & set(
            self.options.get("target", [])
        ):
            psync.add_item(cfg.get("platformio", "data_dir"), "data")

    @staticmethod
    def _add_project_binary_items(cfg, psync):
        build_dir = cfg.get("platformio", "build_dir")
        for env_name in os.listdir(build_dir):
            env_dir = os.path.join(build_dir, env_name)
            if not os.path.isdir(env_dir):
                continue
            for fname in os.listdir(env_dir):
                bin_file = os.path.join(env_dir, fname)
                bin_exts = (".elf", ".bin", ".hex", ".eep", "program")
                if os.path.isfile(bin_file) and fname.endswith(bin_exts):
                    psync.add_item(
                        bin_file, os.path.join(".pio", "build", env_name, fname)
                    )

    def _cb_tarfile_filter(self, path):
        if (
            os.path.isdir(path)
            and os.path.basename(path).lower() in self.PSYNC_SKIP_DIRS
        ):
            return None
        if os.path.isfile(path) and not self.is_file_with_exts(
            path, self.PSYNC_SRC_EXTS
        ):
            return None
        return path

    @staticmethod
    def is_file_with_exts(path, exts):
        if path.endswith(tuple(".%s" % e for e in exts)):
            return True
        return False

    def agent_pool_ready(self):
        self.psync_init()

    def psync_init(self):
        self.add_project_items(self.psync)
        d = self.agentpool.callRemote(
            "cmd",
            self.agents,
            "psync",
            dict(id=self.project_id, items=[i[1] for i in self.psync.get_items()]),
        )
        d.addCallback(self.cb_psync_init_result)
        d.addErrback(self.cb_global_error)

        # build db index while wait for result from agent
        self.psync.rebuild_dbindex()

    def cb_psync_init_result(self, result):
        self._acs_total = len(result)
        for success, value in result:
            if not success:
                raise pb.Error(value)
            agent_id, ac_id = value
            try:
                d = self.agentpool.callRemote(
                    "acwrite",
                    agent_id,
                    ac_id,
                    dict(stage=PROJECT_SYNC_STAGE.DBINDEX.value),
                )
                d.addCallback(self.cb_psync_dbindex_result, agent_id, ac_id)
                d.addErrback(self.cb_global_error)
            except (AttributeError, pb.DeadReferenceError):
                self.disconnect(exit_code=1)

    def cb_psync_dbindex_result(self, result, agent_id, ac_id):
        result = set(json.loads(zlib.decompress(result)))
        dbindex = set(self.psync.get_dbindex())
        delete = list(result - dbindex)
        delta = list(dbindex - result)

        self.log.debug(
            "PSync: stats, total={total}, delete={delete}, delta={delta}",
            total=len(dbindex),
            delete=len(delete),
            delta=len(delta),
        )

        if not delete and not delta:
            return self.psync_finalize(agent_id, ac_id)
        if not delete:
            return self.psync_upload(agent_id, ac_id, delta)

        try:
            d = self.agentpool.callRemote(
                "acwrite",
                agent_id,
                ac_id,
                dict(
                    stage=PROJECT_SYNC_STAGE.DELETE.value,
                    dbindex=zlib.compress(json.dumps(delete).encode()),
                ),
            )
            d.addCallback(self.cb_psync_delete_result, agent_id, ac_id, delta)
            d.addErrback(self.cb_global_error)
        except (AttributeError, pb.DeadReferenceError):
            self.disconnect(exit_code=1)

        return None

    def cb_psync_delete_result(self, result, agent_id, ac_id, dbindex):
        assert result
        self.psync_upload(agent_id, ac_id, dbindex)

    def psync_upload(self, agent_id, ac_id, dbindex):
        assert dbindex
        fileobj = BytesIO()
        compressed = self.psync.compress_items(fileobj, dbindex, self.MAX_ARCHIVE_SIZE)
        fileobj.seek(0)
        self.log.debug(
            "PSync: upload project, size={size}", size=len(fileobj.getvalue())
        )
        self.psync_upload_chunk(
            agent_id, ac_id, list(set(dbindex) - set(compressed)), fileobj
        )

    def psync_upload_chunk(self, agent_id, ac_id, dbindex, fileobj):
        offset = fileobj.tell()
        total = fileobj.seek(0, os.SEEK_END)
        # unwind
        fileobj.seek(offset)
        chunk = fileobj.read(self.UPLOAD_CHUNK_SIZE)
        assert chunk
        try:
            d = self.agentpool.callRemote(
                "acwrite",
                agent_id,
                ac_id,
                dict(
                    stage=PROJECT_SYNC_STAGE.UPLOAD.value,
                    chunk=chunk,
                    length=len(chunk),
                    total=total,
                ),
            )
            d.addCallback(
                self.cb_psync_upload_chunk_result, agent_id, ac_id, dbindex, fileobj
            )
            d.addErrback(self.cb_global_error)
        except (AttributeError, pb.DeadReferenceError):
            self.disconnect(exit_code=1)

    def cb_psync_upload_chunk_result(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, result, agent_id, ac_id, dbindex, fileobj
    ):
        result = PROJECT_SYNC_STAGE.lookupByValue(result)
        self.log.debug("PSync: upload chunk result {r}", r=str(result))
        assert result & (PROJECT_SYNC_STAGE.UPLOAD | PROJECT_SYNC_STAGE.EXTRACTED)
        if result is PROJECT_SYNC_STAGE.EXTRACTED:
            if dbindex:
                self.psync_upload(agent_id, ac_id, dbindex)
            else:
                self.psync_finalize(agent_id, ac_id)
        else:
            self.psync_upload_chunk(agent_id, ac_id, dbindex, fileobj)

    def psync_finalize(self, agent_id, ac_id):
        try:
            d = self.agentpool.callRemote("acclose", agent_id, ac_id)
            d.addCallback(self.cb_psync_completed_result, agent_id)
            d.addErrback(self.cb_global_error)
        except (AttributeError, pb.DeadReferenceError):
            self.disconnect(exit_code=1)

    def cb_psync_completed_result(self, result, agent_id):
        assert PROJECT_SYNC_STAGE.lookupByValue(result)
        options = self.options.copy()
        del options["project_dir"]
        options["project_id"] = self.project_id
        d = self.agentpool.callRemote("cmd", [agent_id], self.command, options)
        d.addCallback(self.cb_async_result)
        d.addErrback(self.cb_global_error)
