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

from platform import system
from subprocess import check_call
from sys import modules
from urlparse import urlsplit, urlunsplit

from platformio.exception import PlatformioException


class VCSClientFactory(object):

    @staticmethod
    def newClient(url):
        scheme, netloc, path, query, fragment = urlsplit(url)
        type_ = scheme
        if "+" in type_:
            type_, scheme = type_.split("+", 1)
        url = urlunsplit((scheme, netloc, path, query, None))
        clsname = "%sClient" % type_.title()
        obj = getattr(modules[__name__], clsname)(url, fragment)
        assert isinstance(obj, VCSClientBase)
        return obj


class VCSClientBase(object):

    command = None

    def __init__(self, url, branch=None):
        self.url = url
        self.branch = branch
        self.check_client()

    def check_client(self):
        try:
            assert self.command
            assert self.run_cmd(["--version"]) == 0
        except (AssertionError, OSError):
            raise PlatformioException(
                "VCS: `%s` client is not installed in your system" %
                self.command)
        return True

    def export(self, dst_dir):
        raise NotImplementedError

    def run_cmd(self, args):
        return check_call([self.command] + args, shell=system() == "Windows")


class GitClient(VCSClientBase):

    command = "git"

    def export(self, dst_dir):
        args = ["clone", "--recursive", "--depth", "1"]
        if self.branch:
            args.extend(["--branch", self.branch])
        args.extend([self.url, dst_dir])
        self.run_cmd(args)


class HgClient(VCSClientBase):

    command = "hg"

    def export(self, dst_dir):
        args = ["clone"]
        if self.branch:
            args.extend(["--updaterev", self.branch])
        args.extend([self.url, dst_dir])
        self.run_cmd(args)


class SvnClient(VCSClientBase):

    command = "svn"

    def export(self, dst_dir):
        args = ["export", "--force"]
        if self.branch:
            args.extend(["--revision", self.branch])
        args.extend([self.url, dst_dir])
        self.run_cmd(args)
