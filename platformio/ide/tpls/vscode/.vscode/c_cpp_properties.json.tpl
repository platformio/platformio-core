{
    "configurations": [
        {
            "name": "!!! WARNING !!! AUTO-GENERATED FILE, PLEASE DO NOT MODIFY IT AND USE https://docs.platformio.org/page/projectconf/section_env_build.html#build-flags"
        },
        {
% import os
% import platform
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
% def _find_abs_path(inc, inc_paths):
%   for path in inc_paths:
%     if os.path.isfile(os.path.join(path, inc)):
%       return os.path.join(path, inc)
%     end
%   end
%   return inc
% end
%
% def _find_forced_includes(flags, inc_paths):
%   result = []
%   i = 0
%   length = len(flags)
%   while(i < length):
%     if flags[i].startswith("-include"):
%       i = i + 1
%       if i < length and not flags[i].startswith("-"):
%         inc = flags[i]
%         if not os.path.isabs(inc):
%           inc = _find_abs_path(inc, inc_paths)
%         end
%         result.append(to_unix_path(inc))
%       end
%     end
%     i = i + 1
%   end
%   return result
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
%   if "toolchain-" not in os.path.dirname(os.path.commonprefix(
%       [include, cc_path])) and os.path.isdir(include):
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
% cc_m_flags = _split_flags(cc_flags)
% forced_includes = _find_forced_includes(cc_m_flags, cleaned_includes)
%
% if cc_stds:
            "cStandard": "c{{ cc_stds[-1] }}",
% end
% if cxx_stds:
            "cppStandard": "c++{{ cxx_stds[-1] }}",
% end
% if forced_includes:
            "forcedInclude": [
% for include in forced_includes:
                "{{ include }}",
% end
                ""
            ],
% end
            "compilerPath": "{{ cc_path }}",
            "compilerArgs": [
% for flag in [
%     '"%s"' % _escape(f) if _escape_required(f) else f
%     for f in cc_m_flags
%     if f.startswith(("-m", "-i", "@")) and not f.startswith("-include")
% ]:
                "{{ flag }}",
% end
                ""
            ]
        }
    ],
    "version": 4
}
