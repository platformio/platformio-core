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

from twisted.internet import reactor  # pylint: disable=import-error
from twisted.web import static  # pylint: disable=import-error


class WebRoot(static.File):
    def render_GET(self, request):
        if request.args.get(b"__shutdown__", False):
            reactor.stop()
            return "Server has been stopped"

        request.setHeader("cache-control", "no-cache, no-store, must-revalidate")
        request.setHeader("pragma", "no-cache")
        request.setHeader("expires", "0")
        return static.File.render_GET(self, request)
