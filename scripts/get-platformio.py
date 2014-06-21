# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import os
import sys
from subprocess import check_output
from tempfile import NamedTemporaryFile


CURINTERPRETER_PATH = os.path.normpath(sys.executable)
IS_WINDOWS = sys.platform.startswith("win")


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


def exec_python_cmd(args):
    return check_output([CURINTERPRETER_PATH] + args, shell=IS_WINDOWS).strip()


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
        print (exec_python_cmd([f.name]))
    finally:
        os.unlink(f.name)


def install_pypi_packages(packages):
    for p in packages:
        print (exec_python_cmd(["-m", "pip", "install", "-U"] + p.split()))


def main():
    steps = [
        ("Fixing Windows %PATH% Environment", fix_winpython_pathenv, []),
        ("Installing Python Package Manager", install_pip, []),
        ("Installing PlatformIO and dependencies", install_pypi_packages,
         (["platformio", "--egg scons"],)),
    ]

    if not IS_WINDOWS:
        del steps[0]

    is_error = False
    for s in steps:
        print ("\n==> %s ..." % s[0])
        try:
            s[1](*s[2])
            print ("[SUCCESS]")
        except Exception, e:
            is_error = True
            print (e)
            print ("[FAILURE]")

    if is_error:
        print ("The installation process has been FAILED!\n"
               "Please report about this problem here\n"
               "< https://github.com/ivankravets/platformio/issues >")
        return
    else:
        print ("\n ==> Installation process has been "
               "successfully FINISHED! <==\n")

    try:
        print (check_output("platformio", shell=IS_WINDOWS))
    except:
        try:
            print (exec_python_cmd(["-m", "platformio"]))
        finally:
            print ("\n Please RESTART your Terminal Application and run "
                   "`platformio --help` command.")


if __name__ == "__main__":
    sys.exit(main())
