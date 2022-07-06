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
import re
import subprocess
from urllib.parse import urlparse

from platformio import proc
from platformio.package.exception import (
    PackageException,
    PlatformioException,
    UserSideException,
)


class VCSBaseException(PackageException):
    pass


class VCSClientFactory:
    @staticmethod
    def new(src_dir, remote_url, silent=False):
        result = urlparse(remote_url)
        type_ = result.scheme
        tag = None
        if not type_ and remote_url.startswith("git+"):
            type_ = "git"
            remote_url = remote_url[4:]
        elif "+" in result.scheme:
            type_, _ = result.scheme.split("+", 1)
            remote_url = remote_url[len(type_) + 1 :]
        if "#" in remote_url:
            remote_url, tag = remote_url.rsplit("#", 1)
        if not type_:
            raise VCSBaseException("VCS: Unknown repository type %s" % remote_url)
        try:
            obj = globals()["%sClient" % type_.capitalize()](
                src_dir, remote_url, tag, silent
            )
            assert isinstance(obj, VCSClientBase)
            return obj
        except (KeyError, AssertionError) as exc:
            raise VCSBaseException(
                "VCS: Unknown repository type %s" % remote_url
            ) from exc


class VCSClientBase:

    command = None

    def __init__(self, src_dir, remote_url=None, tag=None, silent=False):
        self.src_dir = src_dir
        self.remote_url = remote_url
        self.tag = tag
        self.silent = silent
        self.check_client()

    def check_client(self):
        try:
            assert self.command
            if self.silent:
                self.get_cmd_output(["--version"])
            else:
                assert self.run_cmd(["--version"])
        except (AssertionError, OSError, PlatformioException) as exc:
            raise UserSideException(
                "VCS: `%s` client is not installed in your system" % self.command
            ) from exc
        return True

    @property
    def storage_dir(self):
        return os.path.join(self.src_dir, "." + self.command)

    def export(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    @property
    def can_be_updated(self):
        return not self.tag

    def get_current_revision(self):
        raise NotImplementedError

    def get_latest_revision(self):
        return None if self.can_be_updated else self.get_current_revision()

    def run_cmd(self, args, **kwargs):
        args = [self.command] + args
        if "cwd" not in kwargs:
            kwargs["cwd"] = self.src_dir
        if "env" not in kwargs:
            kwargs["env"] = os.environ
        try:
            subprocess.check_call(args, **kwargs)
            return True
        except subprocess.CalledProcessError as exc:
            raise VCSBaseException(
                "VCS: Could not process command %s" % exc.cmd
            ) from exc

    def get_cmd_output(self, args, **kwargs):
        args = [self.command] + args
        if "cwd" not in kwargs:
            kwargs["cwd"] = self.src_dir
        result = proc.exec_command(args, **kwargs)
        if result["returncode"] == 0:
            return result["out"].strip()
        raise VCSBaseException(
            "VCS: Could not receive an output from `%s` command (%s)" % (args, result)
        )


class GitClient(VCSClientBase):

    command = "git"
    _configured = False

    def __init__(self, *args, **kwargs):
        self.configure()
        super().__init__(*args, **kwargs)

    @classmethod
    def configure(cls):
        if cls._configured:
            return True
        cls._configured = True
        try:
            result = proc.exec_command([cls.command, "--exec-path"])
            if result["returncode"] != 0:
                return False
            path = result["out"].strip()
            if path:
                proc.append_env_path("PATH", path)
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return False

    def check_client(self):
        try:
            return VCSClientBase.check_client(self)
        except UserSideException as exc:
            raise UserSideException(
                "Please install Git client from https://git-scm.com/downloads"
            ) from exc

    def get_branches(self):
        output = self.get_cmd_output(["branch"])
        output = output.replace("*", "")  # fix active branch
        return [b.strip() for b in output.split("\n")]

    def get_current_branch(self):
        output = self.get_cmd_output(["branch"])
        for line in output.split("\n"):
            line = line.strip()
            if line.startswith("*"):
                branch = line[1:].strip()
                if branch != "(no branch)":
                    return branch
        return None

    def get_tags(self):
        output = self.get_cmd_output(["tag", "-l"])
        return [t.strip() for t in output.split("\n")]

    @staticmethod
    def is_commit_id(text):
        return text and re.match(r"[0-9a-f]{7,}$", text) is not None

    @property
    def can_be_updated(self):
        return not self.tag or not self.is_commit_id(self.tag)

    def export(self):
        is_commit = self.is_commit_id(self.tag)
        args = ["clone", "--recursive"]
        if not self.tag or not is_commit:
            args += ["--depth", "1"]
            if self.tag:
                args += ["--branch", self.tag]
        args += [self.remote_url, self.src_dir]
        assert self.run_cmd(args, cwd=os.getcwd())
        if is_commit:
            assert self.run_cmd(["reset", "--hard", self.tag])
            return self.run_cmd(
                ["submodule", "update", "--init", "--recursive", "--force"]
            )
        return True

    def update(self):
        args = ["pull", "--recurse-submodules"]
        return self.run_cmd(args)

    def get_current_revision(self):
        return self.get_cmd_output(["rev-parse", "--short", "HEAD"])

    def get_latest_revision(self):
        if not self.can_be_updated:
            return self.get_current_revision()
        branch = self.get_current_branch()
        if not branch:
            return None

        branch_ref = f"refs/heads/{branch}"
        result = self.get_cmd_output(["ls-remote", self.remote_url, branch_ref])
        if not result:
            return None

        for line in result.split("\n"):
            sha, ref = line.strip().split("\t")
            if ref == branch_ref:
                return sha[:7]

        return None


class HgClient(VCSClientBase):

    command = "hg"

    def export(self):
        args = ["clone"]
        if self.tag:
            args.extend(["--updaterev", self.tag])
        args.extend([self.remote_url, self.src_dir])
        return self.run_cmd(args)

    def update(self):
        args = ["pull", "--update"]
        return self.run_cmd(args)

    def get_current_revision(self):
        return self.get_cmd_output(["identify", "--id"])

    def get_latest_revision(self):
        if not self.can_be_updated:
            return self.get_latest_revision()
        return self.get_cmd_output(["identify", "--id", self.remote_url])


class SvnClient(VCSClientBase):

    command = "svn"

    def export(self):
        args = ["checkout"]
        if self.tag:
            args.extend(["--revision", self.tag])
        args.extend([self.remote_url, self.src_dir])
        return self.run_cmd(args)

    def update(self):
        args = ["update"]
        return self.run_cmd(args)

    def get_current_revision(self):
        output = self.get_cmd_output(
            ["info", "--non-interactive", "--trust-server-cert", "-r", "HEAD"]
        )
        for line in output.split("\n"):
            line = line.strip()
            if line.startswith("Revision:"):
                return line.split(":", 1)[1].strip()
        raise VCSBaseException("Could not detect current SVN revision")
