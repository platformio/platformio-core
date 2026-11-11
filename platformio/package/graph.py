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


def iter_package_dependencies(manager, package):
    """Yield each declared dependency spec and its installed package, if any."""
    for dependency in manager.get_pkg_dependencies(package) or ():
        spec = manager.dependency_to_spec(dependency)
        yield spec, manager.get_package(spec)


def walk_package_dependencies(manager, root):
    """Visit the root and each reachable installed package once."""
    visited = set()
    pending = [root]
    while pending:
        package = pending.pop()
        if package in visited:
            continue
        visited.add(package)
        yield package
        pending.extend(
            child
            for _, child in iter_package_dependencies(manager, package)
            if child is not None
        )
