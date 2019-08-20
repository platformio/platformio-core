{
    "configurations": [
        {
            "name": "!!! WARNING !!! AUTO-GENERATED FILE, PLEASE DO NOT MODIFY IT AND USE https://docs.platformio.org/page/projectconf/section_env_build.html#build-flags"
        },
        {
% import platform
% from os.path import commonprefix, dirname, isdir
%
% systype = platform.system().lower()
%
% def _escape(text):
%   return to_unix_path(text).replace('"', '\\"')
% end
%
% cleaned_includes = []
% for include in includes:
%   if "toolchain-" not in dirname(commonprefix([include, cc_path])) and isdir(include):
%     cleaned_includes.append(include)
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
                "{{ include }}",
% end
                ""
            ],
            "browse": {
                "limitSymbolsToIncludedHeaders": true,
                "path": [
% for include in cleaned_includes:
                    "{{ include }}",
% end
                    ""
                ]
            },
            "defines": [
% for define in defines:
                "{{! _escape(define) }}",
% end
                ""
            ],
            "intelliSenseMode": "clang-x64",
% import re
% STD_RE = re.compile(r"\-std=[a-z\+]+(\d+)")
% cc_stds = STD_RE.findall(cc_flags)
% cxx_stds = STD_RE.findall(cxx_flags)
%
% # pass only architecture specific flags
% cc_m_flags = " ".join([f.strip() for f in cc_flags.split(" ") if f.strip().startswith("-m")])
%
% if cc_stds:
            "cStandard": "c{{ cc_stds[-1] }}",
% end
% if cxx_stds:
            "cppStandard": "c++{{ cxx_stds[-1] }}",
% end
            "compilerPath": "\"{{cc_path}}\" {{! _escape(cc_m_flags) }}"
        }
    ],
    "version": 4
}