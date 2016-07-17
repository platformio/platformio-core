# Copyright 2014-present Ivan Kravets <me@ikravets.com>
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

from os import listdir
from os.path import isdir, join
from platform import system
from subprocess import check_call
from sys import modules
from urlparse import urlsplit, urlunsplit

from platformio import util
from platformio.exception import PlatformioException


class VCSClientFactory(object):

    @staticmethod
    def newClient(src_dir, remote_url=None, branch=None):
        clsnametpl = "%sClient"
        vcscls = None
        type_ = None
        if remote_url:
            scheme, netloc, path, query, branch = urlsplit(remote_url)
            type_ = scheme
            if "+" in type_:
                type_, scheme = type_.split("+", 1)
            remote_url = urlunsplit((scheme, netloc, path, query, None))
            vcscls = getattr(modules[__name__], clsnametpl % type_.title())
        elif isdir(src_dir):
            for item in listdir(src_dir):
                if not isdir(join(src_dir, item)) or not item.startswith("."):
                    continue
                try:
                    vcscls = getattr(
                        modules[__name__], clsnametpl % item[1:].title())
                except AttributeError:
                    pass
        assert vcscls
        obj = vcscls(src_dir, remote_url, branch)
        assert isinstance(obj, VCSClientBase)
        return obj


class VCSClientBase(object):

    command = None

    def __init__(self, src_dir, remote_url=None, branch=None):
        self.src_dir = src_dir
        self.remote_url = remote_url
        self.branch = branch
        self.check_client()

    def check_client(self):
        try:
            assert self.command
            assert self.run_cmd(["--version"])
        except (AssertionError, OSError):
            raise PlatformioException(
                "VCS: `%s` client is not installed in your system" %
                self.command)
        return True

    @property
    def storage_dir(self):
        return join(self.src_dir, "." + self.command)

    def export(self):
        raise NotImplementedError

    def get_latest_revision(self):
        raise NotImplementedError

    def run_cmd(self, args, **kwargs):
        args = [self.command] + args
        kwargs['shell'] = system() == "Windows"
        return check_call(args, **kwargs) == 0

    def get_cmd_output(self, args, **kwargs):
        args = [self.command] + args
        result = util.exec_command(args, **kwargs)
        if result['returncode'] == 0:
            return result['out']
        raise PlatformioException(
            "VCS: Could not receive an output from `%s` command (%s)" % (
                args, result))


class GitClient(VCSClientBase):

    command = "git"

    def export(self):
        args = ["clone", "--recursive", "--depth", "1"]
        if self.branch:
            args.extend(["--branch", self.branch])
        args.extend([self.remote_url, self.src_dir])
        return self.run_cmd(args)

    def get_latest_revision(self):
        return self.get_cmd_output(["rev-parse", "--short", "HEAD"],
                                   cwd=self.src_dir).strip()


class HgClient(VCSClientBase):

    command = "hg"

    def export(self):
        args = ["clone"]
        if self.branch:
            args.extend(["--updaterev", self.branch])
        args.extend([self.remote_url, self.src_dir])
        return self.run_cmd(args)

    def get_latest_revision(self):
        return self.get_cmd_output(["identify", "--id"],
                                   cwd=self.src_dir).strip()


class SvnClient(VCSClientBase):

    command = "svn"

    def export(self):
        args = ["export", "--force"]
        if self.branch:
            args.extend(["--revision", self.branch])
        args.extend([self.remote_url, self.src_dir])
        return self.run_cmd(args)

    def get_latest_revision(self):
        return self.get_cmd_output(["info", "-r", "HEAD"],
                                   cwd=self.src_dir).strip()
