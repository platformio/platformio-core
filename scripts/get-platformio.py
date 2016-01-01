# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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
import subprocess
import sys
from platform import system
from tempfile import NamedTemporaryFile


CURINTERPRETER_PATH = os.path.normpath(sys.executable)
IS_WINDOWS = system().lower() == "windows"


def fix_winpython_pathenv():
    """
    Add Python & Python Scripts to the search path on Windows
    """
    import ctypes
    from ctypes.wintypes import HWND, UINT, WPARAM, LPARAM, LPVOID
    try:
        import _winreg as winreg
    except ImportError:
        import winreg

    # took these lines from the native "win_add2path.py"
    pythonpath = os.path.dirname(CURINTERPRETER_PATH)
    scripts = os.path.join(pythonpath, "Scripts")
    if not os.path.isdir(scripts):
        os.makedirs(scripts)

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, u"Environment") as key:
        try:
            envpath = winreg.QueryValueEx(key, u"PATH")[0]
        except WindowsError:
            envpath = u"%PATH%"

        paths = [envpath]
        for path in (pythonpath, scripts):
            if path and path not in envpath and os.path.isdir(path):
                paths.append(path)

        envpath = os.pathsep.join(paths)
        winreg.SetValueEx(key, u"PATH", 0, winreg.REG_EXPAND_SZ, envpath)
    winreg.ExpandEnvironmentStrings(envpath)

    # notify the system about the changes
    SendMessage = ctypes.windll.user32.SendMessageW
    SendMessage.argtypes = HWND, UINT, WPARAM, LPVOID
    SendMessage.restype = LPARAM
    SendMessage(0xFFFF, 0x1A, 0, u"Environment")
    return True


def exec_command(*args, **kwargs):
    result = {
        "out": None,
        "err": None,
        "returncode": None
    }

    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.PIPE
    kwargs['shell'] = IS_WINDOWS

    p = subprocess.Popen(*args, **kwargs)
    result['out'], result['err'] = p.communicate()
    result['returncode'] = p.returncode

    for k, v in result.iteritems():
        if v and isinstance(v, basestring):
            result[k].strip()

    return result


def print_exec_result(result):
    if result['returncode'] == 0:
        print(result['out'])
    else:
        raise Exception("\n".join([result['out'], result['err']]))


def exec_python_cmd(args):
    return exec_command([CURINTERPRETER_PATH] + args)


def install_pip():
    try:
        from urllib2 import urlopen
    except ImportError:
        from urllib.request import urlopen

    f = NamedTemporaryFile(delete=False)
    response = urlopen("https://bootstrap.pypa.io/get-pip.py")
    f.write(response.read())
    f.close()

    try:
        r = exec_python_cmd([f.name])
    finally:
        os.unlink(f.name)

    print_exec_result(r)


def install_platformio():
    r = None
    cmd = ["-m", "pip.__main__" if sys.version_info < (2, 7, 0) else "pip"]
    try:
        r = exec_python_cmd(cmd + ["install", "-U", "platformio"])
        assert r['returncode'] == 0
    except AssertionError:
        r = exec_python_cmd(
            cmd + ["--no-cache-dir", "install", "-U", "platformio"])
    if r:
        print_exec_result(r)


def main():
    steps = [
        ("Fixing Windows %PATH% Environment", fix_winpython_pathenv),
        ("Installing Python Package Manager", install_pip),
        ("Installing PlatformIO and dependencies", install_platformio)
    ]

    if not IS_WINDOWS:
        del steps[0]

    is_error = False
    for s in steps:
        if is_error:
            break
        print("\n==> %s ..." % s[0])
        try:
            s[1]()
            print("[SUCCESS]")
        except Exception, e:
            is_error = True
            print(str(e))
            print("[FAILURE]")

            permission_errors = (
                "permission denied",
                "not permitted"
            )
            if (any([m in str(e).lower() for m in permission_errors]) and not
                    IS_WINDOWS):
                print ("""
-----------------
Permission denied
-----------------

You need the `sudo` permission to install Python packages. Try

$ sudo python -c "$(curl -fsSL
https://raw.githubusercontent.com/platformio/platformio/master/scripts/get-platformio.py)"
""")

    if is_error:
        print("The installation process has been FAILED!\n"
              "Please report about this problem here\n"
              "< https://github.com/platformio/platformio/issues >")
        return
    else:
        print("\n ==> Installation process has been "
              "successfully FINISHED! <==\n")

    try:
        print_exec_result(exec_command("platformio"))
    except:
        try:
            print_exec_result(exec_python_cmd([
                "-m",
                "platformio.__main__" if sys.version_info < (2, 7, 0) else
                "platformio"]))
        except:
            pass
    finally:
        print ("""

----------------------------------------
Please RESTART your Terminal Application
----------------------------------------

Then run `platformio --help` command.

""")


if __name__ == "__main__":
    sys.exit(main())
