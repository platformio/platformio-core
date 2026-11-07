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

# pylint: disable=protected-access

import gc
import os
from pathlib import Path

import pytest

from platformio.package import lockfile
from platformio.package.lockfile import LOCKFILE_DELAY, LockFile, LockFileTimeoutError


def test_failed_acquire_keeps_holders_lock(tmp_path: Path) -> None:
    path = str(tmp_path / "artifact")
    holder = LockFile(path)
    holder.acquire()
    contender = LockFile(path, timeout=LOCKFILE_DELAY)
    with pytest.raises(LockFileTimeoutError):
        contender.acquire()
    # neither releasing nor collecting a lock that was never acquired may
    # remove the lock file held by another owner
    contender.release()
    del contender
    gc.collect()
    assert os.path.exists(path + ".lock")
    holder.release()
    assert not os.path.exists(path + ".lock")


@pytest.mark.skipif(
    lockfile.LOCKFILE_CURRENT_INTERFACE != lockfile.LOCKFILE_INTERFACE_FCNTL,
    reason="POSIX-only race: Windows cannot delete a file that is open",
)
def test_lock_on_unlinked_file_is_retried(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = str(tmp_path / "artifact")
    lock_path = path + ".lock"
    real_flock = lockfile.fcntl.flock
    unlinked = []

    def flock_then_holder_unlinks(fd: int, operation: int) -> None:
        real_flock(fd, operation)
        # the previous holder removes the lock file right after we locked
        # the inode it was still pointing to
        if operation & lockfile.fcntl.LOCK_EX and not unlinked:
            unlinked.append(True)
            os.remove(lock_path)

    monkeypatch.setattr(lockfile.fcntl, "flock", flock_then_holder_unlinks)
    lock = LockFile(path, timeout=5)
    lock.acquire()
    assert unlinked
    # the lock must be held on the file that is at the path now
    assert os.path.exists(lock_path)
    assert os.path.samestat(os.fstat(lock._fp.fileno()), os.stat(lock_path))
    lock.release()


@pytest.mark.skipif(
    lockfile.LOCKFILE_CURRENT_INTERFACE != lockfile.LOCKFILE_INTERFACE_FCNTL,
    reason="POSIX-only race: Windows cannot delete a file that is open",
)
def test_release_never_hands_out_a_doomed_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = str(tmp_path / "artifact")
    holder = LockFile(path)
    holder.acquire()
    holder_fd = holder._fp.fileno()
    contender = LockFile(path)
    real_flock = lockfile.fcntl.flock
    raced = []

    def flock(fd: int, operation: int) -> None:
        real_flock(fd, operation)
        # a waiting process takes the lock right after the holder unlocks
        if operation == lockfile.fcntl.LOCK_UN and fd == holder_fd and not raced:
            raced.append(contender._lock())

    monkeypatch.setattr(lockfile.fcntl, "flock", flock)
    holder.release()
    assert raced == [True]
    # whoever holds the lock now, no third process may also acquire it
    with pytest.raises(LockFileTimeoutError):
        LockFile(path, timeout=LOCKFILE_DELAY).acquire()
    contender.release()
