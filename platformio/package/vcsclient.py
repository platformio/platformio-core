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

import re
from os.path import join
from subprocess import CalledProcessError, check_call
from sys import modules

from platformio.exception import PlatformioException, UserSideException
from platformio.proc import exec_command

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class VCSClientFactory(object):
    @staticmethod
    def newClient(src_dir, remote_url, silent=False):
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
            raise PlatformioException("VCS: Unknown repository type %s" % remote_url)
        obj = getattr(modules[__name__], "%sClient" % type_.title())(
            src_dir, remote_url, tag, silent
        )
        assert isinstance(obj, VCSClientBase)
        return obj


class VCSClientBase(object):

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
        except (AssertionError, OSError, PlatformioException):
            raise UserSideException(
                "VCS: `%s` client is not installed in your system" % self.command
            )
        return True

    @property
    def storage_dir(self):
        return join(self.src_dir, "." + self.command)

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
        try:
            check_call(args, **kwargs)
            return True
        except CalledProcessError as e:
            raise PlatformioException("VCS: Could not process command %s" % e.cmd)

    def get_cmd_output(self, args, **kwargs):
        args = [self.command] + args
        if "cwd" not in kwargs:
            kwargs["cwd"] = self.src_dir
        result = exec_command(args, **kwargs)
        if result["returncode"] == 0:
            return result["out"].strip()
        raise PlatformioException(
            "VCS: Could not receive an output from `%s` command (%s)" % (args, result)
        )


class GitClient(VCSClientBase):

    command = "git"

    def check_client(self):
        try:
            return VCSClientBase.check_client(self)
        except UserSideException:
            raise UserSideException(
                "Please install Git client from https://git-scm.com/downloads"
            )

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
        assert self.run_cmd(args)
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
            return self.get_current_revision()
        result = self.get_cmd_output(["ls-remote"])
        for line in result.split("\n"):
            ref_pos = line.strip().find("refs/heads/" + branch)
            if ref_pos > 0:
                return line[:ref_pos].strip()[:7]
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
        raise PlatformioException("Could not detect current SVN revision")
