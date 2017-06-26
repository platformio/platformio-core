% from os.path import dirname, join
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "gdb",
            "request": "launch",
            "cwd": "${workspaceRoot}",
            "name": "PlatformIO Debugger",
            "target": "{{prog_path.replace('\\\\', '/').replace('\\', '/').replace('"', '\\"')}}",
            "gdbpath": "{{join(dirname(platformio_path), "piodebuggdb").replace('\\\\', '/').replace('\\', '/').replace('"', '\\"')}}",
            "autorun": [ "source .pioinit" ]
        }
    ]
}