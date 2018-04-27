// AUTOMATICALLY GENERATED FILE. PLEASE DO NOT MODIFY IT MANUALLY

// PIO Unified Debugger
//
// http://docs.platformio.org/page/plus/debugging.html
// http://docs.platformio.org/page/section_env_debug.html#projectconf-debug-tool

% from os.path import dirname, join
%
% def _escape_path(path):
%   return path.replace('\\\\', '/').replace('\\', '/').replace('"', '\\"')
% end
%
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "gdb",
            "request": "launch",
            "cwd": "${workspaceRoot}",
            "name": "PlatformIO Debugger",
            "target": "{{ _escape_path(prog_path) }}",
            "gdbpath": "{{ _escape_path(join(dirname(platformio_path), "piodebuggdb")) }}",
            "autorun": [ "source .pioinit" ],
            "preLaunchTask": "PlatformIO: Pre-Debug",
            "internalConsoleOptions": "openOnSessionStart"
        },
        {
            "type": "platformio-debug",
            "request": "launch",
            "name": "PlatformIO Debugger (Beta)",
            "executable": "{{ _escape_path(prog_path) }}",
            "toolchainBinDir": "{{ _escape_path(dirname(gdb_path)) }}",
            "preLaunchTask": "PlatformIO: Pre-Debug",
            "internalConsoleOptions": "openOnSessionStart"
        },
        {
            "type": "platformio-debug",
            "request": "launch",
            "name": "PlatformIO Debugger (Beta) (Quick)",
            "executable": "{{ _escape_path(prog_path) }}",
            "toolchainBinDir": "{{ _escape_path(dirname(gdb_path)) }}",
            "internalConsoleOptions": "openOnSessionStart"
        }
    ]
}