% import os
% import platform
%
% systype = platform.system().lower()
%
% cpp_standards_remap = {
%   "c++0x": "c++11",
%   "c++1y": "c++14",
%   "c++1z": "c++17",
%   "c++2a": "c++20",
%   "c++2b": "c++23",
%   "gnu++0x": "gnu++11",
%   "gnu++1y": "gnu++14",
%   "gnu++1z": "gnu++17",
%   "gnu++2a": "gnu++20",
%   "gnu++2b": "gnu++23"
% }
%
% def _escape(text):
%   return to_unix_path(text).replace('"', '\\"')
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
%   while(i < length):
%     if any(args[i].startswith(f) for f in allowed) and not any(
%           args[i].startswith(f) for f in ignore):
%       result.append(args[i])
%       if i + 1 < length and not args[i + 1].startswith("-"):
%         i += 1
%         result.append(args[i])
%       end
%     end
%     i += 1
%   end
%   return result
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
% cc_stds = [arg[5:] for arg in cc_flags if arg.startswith("-std=")]
% cxx_stds = [arg[5:] for arg in cxx_flags if arg.startswith("-std=")]
% forced_includes = _find_forced_includes(
%   filter_args(cc_flags, ["-include", "-imacros"]), cleaned_includes)
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
            "cStandard": "{{ cc_stds[-1] }}",
% end
% if cxx_stds:
            "cppStandard": "{{ cpp_standards_remap.get(cxx_stds[-1], cxx_stds[-1]) }}",
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
%     f for f in filter_args(cc_flags, ["-m", "-i", "@"], ["-include", "-imacros"])
% ]:
                "{{ flag }}",
% end
                ""
            ]
        }
    ],
    "version": 4
}
