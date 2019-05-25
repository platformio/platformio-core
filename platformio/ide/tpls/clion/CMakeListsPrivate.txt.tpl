# !!! WARNING !!! AUTO-GENERATED FILE, PLEASE DO NOT MODIFY IT AND USE
# https://docs.platformio.org/page/projectconf/section_env_build.html#build-flags
#
# If you need to override existing CMake configuration or add extra,
# please create `CMakeListsUser.txt` in the root of project.
# The `CMakeListsUser.txt` will not be overwritten by PlatformIO.

% import re
%
% def _normalize_path(path):
%   if project_dir in path:
%     path = path.replace(project_dir, "${CMAKE_CURRENT_LIST_DIR}")
%   elif user_home_dir in path:
%     if "windows" in systype:
%       path = path.replace(user_home_dir, "$ENV{HOMEDRIVE}$ENV{HOMEPATH}")
%     else:
%       path = path.replace(user_home_dir, "$ENV{HOME}")
%     end
%   end
%   return path.replace("\\", "/")
% end

set(PLATFORMIO_CMD "{{ _normalize_path(platformio_path) }}")

SET(CMAKE_C_COMPILER "{{ _normalize_path(cc_path) }}")
SET(CMAKE_CXX_COMPILER "{{ _normalize_path(cxx_path) }}")
SET(CMAKE_CXX_FLAGS_DISTRIBUTION "{{cxx_flags}}")
SET(CMAKE_C_FLAGS_DISTRIBUTION "{{cc_flags}}")

% STD_RE = re.compile(r"\-std=[a-z\+]+(\d+)")
% cc_stds = STD_RE.findall(cc_flags)
% cxx_stds = STD_RE.findall(cxx_flags)
% if cc_stds:
SET(CMAKE_C_STANDARD {{ cc_stds[-1] }})
% end
% if cxx_stds:
set(CMAKE_CXX_STANDARD {{ cxx_stds[-1] }})
% end

% for define in defines:
add_definitions(-D'{{!re.sub(r"([\"\(\)#])", r"\\\1", define)}}')
% end

% for include in includes:
include_directories("{{ _normalize_path(include) }}")
% end

FILE(GLOB_RECURSE SRC_LIST "{{ _normalize_path(project_src_dir) }}/*.*" "{{ _normalize_path(project_lib_dir) }}/*.*" "{{ _normalize_path(project_libdeps_dir) }}/*.*")
