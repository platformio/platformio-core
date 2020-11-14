% import os
% import platform
% import re
%
% import click
%
% systype = platform.system().lower()
%
% cpp_standards_remap = {
%   "0x": "11",
%   "1y": "14",
%   "1z": "17",
%   "2a": "20",
%   "2b": "23"
% }
%
% def _escape(text):
%   return to_unix_path(text).replace('"', '\\"')
% end
%
% def split_args(args_string):
%   return click.parser.split_arg_string(to_unix_path(args_string))
% end
%
% def filter_args(args, allowed, ignore=None):
%   if not allowed:
%     return []
%   end
%
%   ignore = ignore or []
%   result = []
%   i = 0
%   length = len(args)
%     while(i < length):
%      if any(args[i].startswith(f) for f in allowed) and not any(
%        args[i].startswith(f) for f in ignore):
%        result.append(args[i])
%        if i + 1 < length and not args[i + 1].startswith("-"):
%          i += 1
%          result.append(args[i])
%        end
%       end
%      i += 1
%    end
%    return result
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
%   include_args = ("-include", "-imacros")
%   for f in filter_args(flags, include_args):
%     for arg in include_args:
%       inc = ""
%       if f.startswith(arg) and f.split(arg)[1].strip():
%         inc = f.split(arg)[1].strip()
%       elif not f.startswith("-"):
%         inc = f
%       end
%       if inc:
%         result.append(_find_abs_path(inc, inc_paths))
%         break
%       end
%     end
%   end
%   return result
% end
%
% cleaned_includes = filter_includes(includes, ["toolchain"])
%
% STD_RE = re.compile(r"\-std=[a-z\+]+(\w+)")
% cc_stds = STD_RE.findall(cc_flags)
% cxx_stds = STD_RE.findall(cxx_flags)
% cc_m_flags = split_args(cc_flags)
% forced_includes = _find_forced_includes(
%   filter_args(cc_m_flags, ["-include", "-imacros"]), cleaned_includes)
%
//
// !!! WARNING !!! AUTO-GENERATED FILE!
// PLEASE DO NOT MODIFY IT AND USE "platformio.ini":
// https://docs.platformio.org/page/projectconf/section_env_build.html#build-flags
//
{
    "configurations": [
        {
            "name": "PlatformIO",
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
% if cc_stds:
            "cStandard": "c{{ cc_stds[-1] }}",
% end
% if cxx_stds:
            "cppStandard": "c++{{ cpp_standards_remap.get(cxx_stds[-1], cxx_stds[-1]) }}",
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
%     f for f in filter_args(cc_m_flags, ["-m", "-i", "@"], ["-include", "-imacros"])
% ]:
                "{{ flag }}",
% end
                ""
            ]
        }
    ],
    "version": 4
}
