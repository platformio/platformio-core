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
from time import sleep, time

from platformio.exception import PlatformioException

LOCKFILE_TIMEOUT = 3600  # in seconds, 1 hour
LOCKFILE_DELAY = 0.2

LOCKFILE_INTERFACE_FCNTL = 1
LOCKFILE_INTERFACE_MSVCRT = 2

try:
    import fcntl

    LOCKFILE_CURRENT_INTERFACE = LOCKFILE_INTERFACE_FCNTL
except ImportError:
    try:
        import msvcrt

        LOCKFILE_CURRENT_INTERFACE = LOCKFILE_INTERFACE_MSVCRT
    except ImportError:
        LOCKFILE_CURRENT_INTERFACE = None


class LockFileExists(PlatformioException):
    pass


class LockFileTimeoutError(PlatformioException):
    pass


class LockFile:
    def __init__(self, path, timeout=LOCKFILE_TIMEOUT, delay=LOCKFILE_DELAY):
        self.timeout = timeout
        self.delay = delay
        self._lock_path = os.path.abspath(path) + ".lock"
        self._fp = None

    def _lock(self):
        if not LOCKFILE_CURRENT_INTERFACE and os.path.exists(self._lock_path):
            # remove stale lock
            if time() - os.path.getmtime(self._lock_path) > 10:
                try:
                    os.remove(self._lock_path)
                except:  # pylint: disable=bare-except
                    pass
            else:
                raise LockFileExists

        self._fp = open(  # pylint: disable=consider-using-with
            self._lock_path, mode="w", encoding="utf8"
        )
        try:
            if LOCKFILE_CURRENT_INTERFACE == LOCKFILE_INTERFACE_FCNTL:
                fcntl.flock(self._fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            elif LOCKFILE_CURRENT_INTERFACE == LOCKFILE_INTERFACE_MSVCRT:
                msvcrt.locking(  # pylint: disable=used-before-assignment
                    self._fp.fileno(), msvcrt.LK_NBLCK, 1
                )
        except (BlockingIOError, IOError) as exc:
            self._fp.close()
            self._fp = None
            raise LockFileExists from exc
        return True

    def _unlock(self):
        if not self._fp:
            return
        if LOCKFILE_CURRENT_INTERFACE == LOCKFILE_INTERFACE_FCNTL:
            fcntl.flock(self._fp.fileno(), fcntl.LOCK_UN)
        elif LOCKFILE_CURRENT_INTERFACE == LOCKFILE_INTERFACE_MSVCRT:
            msvcrt.locking(self._fp.fileno(), msvcrt.LK_UNLCK, 1)
        self._fp.close()
        self._fp = None

    def acquire(self):
        elapsed = 0
        while elapsed < self.timeout:
            try:
                return self._lock()
            except LockFileExists:
                sleep(self.delay)
                elapsed += self.delay

        raise LockFileTimeoutError()

    def release(self):
        self._unlock()
        if os.path.exists(self._lock_path):
            try:
                os.remove(self._lock_path)
            except:  # pylint: disable=bare-except
                pass

    def __enter__(self):
        self.acquire()

    def __exit__(self, type_, value, traceback):
        self.release()

    def __del__(self):
        self.release()
