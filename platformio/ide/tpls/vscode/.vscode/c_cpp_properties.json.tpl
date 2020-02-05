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
% def _escape_required(flag):
%   return " " in flag and systype == "windows"
% end
%
% def _split_flags(flags):
%   result = []
%   i = 0
%   flags = flags.strip()
%   while i < len(flags):
%       current_arg = []
%       while i < len(flags) and flags[i] != " ":
%         if flags[i] == '"':
%           quotes_idx = flags.find('"', i + 1)
%           current_arg.extend(flags[i + 1:quotes_idx])
%           i = quotes_idx + 1
%         else:
%           current_arg.append(flags[i])
%           i = i + 1
%         end
%       end
%       arg = "".join(current_arg)
%       if arg.strip():
%         result.append(arg.strip())
%       end
%       i = i + 1
%   end
%   return result
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
% if cc_stds:
            "cStandard": "c{{ cc_stds[-1] }}",
% end
% if cxx_stds:
            "cppStandard": "c++{{ cxx_stds[-1] }}",
% end
            "compilerPath": "{{ cc_path }}",
            "compilerArgs": [
% for flag in [ '"%s"' % _escape(f) if _escape_required(f) else f for f in _split_flags(
%       cc_flags) if f.startswith(("-m", "-i", "@"))]:
                "{{ flag }}",
% end
                ""
            ]
        }
    ],
    "version": 4
}
