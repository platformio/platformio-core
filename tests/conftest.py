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

import email
import functools
import imaplib
import os
import time

import pytest
from click.testing import CliRunner

from platformio import http
from platformio.package.meta import PackageSpec, PackageType
from platformio.registry.client import RegistryClient


def pytest_configure(config):
    config.addinivalue_line("markers", "skip_ci: mark a test that will not run in CI")


@pytest.fixture(scope="session")
def validate_cliresult():
    def decorator(result):
        assert result.exit_code == 0, "{} => {}".format(result.exception, result.output)
        assert not result.exception, "{} => {}".format(result.exception, result.output)

    return decorator


@pytest.fixture(scope="session")
def clirunner(request, tmpdir_factory):
    cache_dir = tmpdir_factory.mktemp(".cache")
    backup_env_vars = {
        "PLATFORMIO_CACHE_DIR": {"new": str(cache_dir)},
        "PLATFORMIO_WORKSPACE_DIR": {"new": None},
    }
    for key, item in backup_env_vars.items():
        # pylint: disable=unnecessary-dict-index-lookup
        backup_env_vars[key]["old"] = os.environ.get(key)
        if item["new"] is not None:
            os.environ[key] = item["new"]
        elif key in os.environ:
            del os.environ[key]

    def fin():
        for key, item in backup_env_vars.items():
            if item["old"] is not None:
                os.environ[key] = item["old"]
            elif key in os.environ:
                del os.environ[key]

    request.addfinalizer(fin)

    return CliRunner()


def _isolated_pio_core(request, tmpdir_factory):
    core_dir = tmpdir_factory.mktemp(".platformio")
    os.environ["PLATFORMIO_CORE_DIR"] = str(core_dir)

    def fin():
        if "PLATFORMIO_CORE_DIR" in os.environ:
            del os.environ["PLATFORMIO_CORE_DIR"]

    request.addfinalizer(fin)
    return core_dir


@pytest.fixture(scope="module")
def isolated_pio_core(request, tmpdir_factory):
    return _isolated_pio_core(request, tmpdir_factory)


@pytest.fixture(scope="function")
def func_isolated_pio_core(request, tmpdir_factory):
    return _isolated_pio_core(request, tmpdir_factory)


@pytest.fixture(scope="function")
def without_internet(monkeypatch):
    monkeypatch.setattr(http, "_internet_on", lambda: False)


@pytest.fixture
def receive_email():  # pylint:disable=redefined-outer-name, too-many-locals
    def _receive_email(from_who):
        test_email = os.environ["TEST_EMAIL_LOGIN"]
        test_password = os.environ["TEST_EMAIL_PASSWORD"]
        imap_server = os.environ["TEST_EMAIL_IMAP_SERVER"]

        def get_body(msg):
            if msg.is_multipart():
                return get_body(msg.get_payload(0))
            return msg.get_payload(None, True)

        result = None
        start_time = time.time()
        while not result:
            time.sleep(5)
            server = imaplib.IMAP4_SSL(imap_server)
            server.login(test_email, test_password)
            server.select("INBOX")
            _, mails = server.search(None, "ALL")
            for index in mails[0].split():
                status, data = server.fetch(index, "(RFC822)")
                if status != "OK" or not data or not isinstance(data[0], tuple):
                    continue
                msg = email.message_from_string(
                    data[0][1].decode("ASCII", errors="surrogateescape")
                )
                if from_who not in msg.get("To"):
                    continue
                if "gmail" in imap_server:
                    server.store(index, "+X-GM-LABELS", "\\Trash")
                server.store(index, "+FLAGS", "\\Deleted")
                server.expunge()
                result = get_body(msg).decode()
            if time.time() - start_time > 120:
                break
            server.close()
            server.logout()
        return result

    return _receive_email


@pytest.fixture(scope="session")
def get_pkg_latest_version():
    @functools.lru_cache()
    def wrap(spec, pkg_type=None):
        if not isinstance(spec, PackageSpec):
            spec = PackageSpec(spec)
        pkg_type = pkg_type or PackageType.LIBRARY
        client = RegistryClient()
        pkg = client.get_package(pkg_type, spec.owner, spec.name)
        return pkg["version"]["name"]

    return wrap
