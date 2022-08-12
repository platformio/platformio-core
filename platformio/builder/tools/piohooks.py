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


def AddActionWrapper(handler):
    def wraps(env, files, action):
        if not isinstance(files, (list, tuple, set)):
            files = [files]
        known_nodes = []
        unknown_files = []
        for item in files:
            nodes = env.arg2nodes(item, env.fs.Entry)
            if nodes and nodes[0].exists():
                known_nodes.extend(nodes)
            else:
                unknown_files.append(item)
        if unknown_files:
            env.Append(**{"_PIO_DELAYED_ACTIONS": [(handler, unknown_files, action)]})
        if known_nodes:
            return handler(known_nodes, action)
        return []

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
