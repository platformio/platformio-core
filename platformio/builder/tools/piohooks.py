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

from __future__ import absolute_import


def AddActionWrapper(handler):
    def wraps(env, files, action):
        nodes = env.arg2nodes(files, env.fs.Entry)
        unknown_nodes = [node for node in nodes if not node.exists()]
        if unknown_nodes:
            env.Append(**{"_PIO_DELAYED_ACTIONS": [(handler, unknown_nodes, action)]})
        return handler([node for node in nodes if node.exists()], action)

    return wraps


def ProcessDelayedActions(env):
    for func, nodes, action in env.get("_PIO_DELAYED_ACTIONS", []):
        func(nodes, action)


def generate(env):
    env.Replace(**{"_PIO_DELAYED_ACTIONS": []})
    env.AddMethod(AddActionWrapper(env.AddPreAction), "AddPreAction")
    env.AddMethod(AddActionWrapper(env.AddPostAction), "AddPostAction")
    env.AddMethod(ProcessDelayedActions)


def exists(_):
    return True
