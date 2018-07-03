{
    "!!! WARNING !!!": "PLEASE DO NOT MODIFY THIS FILE! USE http://docs.platformio.org/page/projectconf/section_env_build.html#build-flags",
    "configurations": [
        {
% import platform
% from os.path import commonprefix, dirname
%
% systype = platform.system().lower()
%
% cleaned_includes = []
% for include in includes:
%   if "toolchain-" not in dirname(commonprefix([include, cc_path])):
%       cleaned_includes.append(include)
%   end
% end
%
% if systype == "windows":
            "name": "Win32",
% elif systype == "darwin":
            "name": "Mac",
            "macFrameworkPath": [],
% else:
            "name": "Linux",
% end
            "includePath": [
% for include in cleaned_includes:
                "{{include.replace('\\\\', '/').replace('\\', '/').replace('"', '\\"')}}",
% end
                ""
            ],
            "browse": {
                "limitSymbolsToIncludedHeaders": true,
                "databaseFilename": "${workspaceRoot}/.vscode/.browse.c_cpp.db",
                "path": [
% for include in cleaned_includes:
                    "{{include.replace('\\\\', '/').replace('\\', '/').replace('"', '\\"')}}",
% end
                    ""
                ]
            },
            "defines": [
% for define in defines:
                "{{!define.replace('"', '\\"')}}",
% end
                ""
            ],
            "intelliSenseMode": "clang-x64",
% import re
% STD_RE = re.compile(r"\-std=[a-z\+]+(\d+)")
% cc_stds = STD_RE.findall(cc_flags)
% cxx_stds = STD_RE.findall(cxx_flags)
%
% if cc_stds:
            "cStandard": "c{{ cc_stds[-1] }}",
% end
% if cxx_stds:
            "cppStandard": "c++{{ cxx_stds[-1] }}",
% end
            "compilerPath": "{{ cc_path.replace('\\\\', '/').replace('\\', '/').replace('"', '\\"') }}"
        }
    ]
}