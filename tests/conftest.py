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
import imaplib
import os
import time

import pytest
from click.testing import CliRunner

from platformio.clients import http


def pytest_configure(config):
    config.addinivalue_line("markers", "skip_ci: mark a test that will not run in CI")


@pytest.fixture(scope="session")
def validate_cliresult():
    def decorator(result):
        assert result.exit_code == 0, "{} => {}".format(result.exception, result.output)
        assert not result.exception, "{} => {}".format(result.exception, result.output)

    return decorator


@pytest.fixture(scope="session")
def clirunner(request):
    backup_env_vars = {
        "PLATFORMIO_WORKSPACE_DIR": {"new": None},
    }
    for key, item in backup_env_vars.items():
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


@pytest.fixture(scope="module")
def isolated_pio_core(request, tmpdir_factory):
    core_dir = tmpdir_factory.mktemp(".platformio")
    os.environ["PLATFORMIO_CORE_DIR"] = str(core_dir)

    def fin():
        del os.environ["PLATFORMIO_CORE_DIR"]

    request.addfinalizer(fin)
    return core_dir


@pytest.fixture(scope="function")
def without_internet(monkeypatch):
    monkeypatch.setattr(http, "_internet_on", lambda: False)


@pytest.fixture
def receive_email():  # pylint:disable=redefined-outer-name, too-many-locals
    def _receive_email(from_who):
        test_email = os.environ.get("TEST_EMAIL_LOGIN")
        test_password = os.environ.get("TEST_EMAIL_PASSWORD")
        imap_server = os.environ.get("TEST_EMAIL_IMAP_SERVER") or "imap.gmail.com"

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
