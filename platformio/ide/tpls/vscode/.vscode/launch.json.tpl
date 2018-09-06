// AUTOMATICALLY GENERATED FILE. PLEASE DO NOT MODIFY IT MANUALLY

// PIO Unified Debugger
//
// Documentation: https://docs.platformio.org/page/plus/debugging.html
// Configuration: https://docs.platformio.org/page/projectconf/section_env_debug.html

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
            "type": "platformio-debug",
            "request": "launch",
            "name": "PIO Debug",
            "executable": "{{ _escape_path(prog_path) }}",
            "toolchainBinDir": "{{ _escape_path(dirname(gdb_path)) }}",
% if svd_path:
            "svdPath": "{{ _escape_path(svd_path) }}",
% end
            "preLaunchTask": {
                "type": "PlatformIO",
                "task": "Pre-Debug"
            },
            "internalConsoleOptions": "openOnSessionStart"
        },
        {
            "type": "platformio-debug",
            "request": "launch",
            "name": "PIO Debug (skip Pre-Debug)",
            "executable": "{{ _escape_path(prog_path) }}",
            "toolchainBinDir": "{{ _escape_path(dirname(gdb_path)) }}",
% if svd_path:
            "svdPath": "{{ _escape_path(svd_path) }}",
% end
            "internalConsoleOptions": "openOnSessionStart"
        }
    ]
}