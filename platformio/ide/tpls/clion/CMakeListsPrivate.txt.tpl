# !!! WARNING !!! AUTO-GENERATED FILE, PLEASE DO NOT MODIFY IT AND USE
# https://docs.platformio.org/page/projectconf/section_env_build.html#build-flags
#
# If you need to override existing CMake configuration or add extra,
# please create `CMakeListsUser.txt` in the root of project.
# The `CMakeListsUser.txt` will not be overwritten by PlatformIO.

%from platformio.project.helpers import (get_project_dir,load_project_ide_data)
%
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
%   return path
% end
%
% envs = config.envs()

% if len(envs) > 1:
set(CMAKE_CONFIGURATION_TYPES "{{ ";".join(envs) }}" CACHE STRING "" FORCE)
% else:
set(CMAKE_CONFIGURATION_TYPES "{{ env_name }}" CACHE STRING "" FORCE)
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

% for env in envs:
if (CMAKE_BUILD_TYPE MATCHES {{ env }})
%   items = load_project_ide_data(get_project_dir(),env)
%   for define in items["defines"]:
    add_definitions(-D'{{!re.sub(r"([\"\(\)#])", r"\\\1", define)}}')
%   end

%   for include in items["includes"]:
    include_directories("{{ _normalize_path(include) }}")
%   end
endif()
% end
FILE(GLOB_RECURSE SRC_LIST "{{ _normalize_path(project_src_dir) }}/*.*" "{{ _normalize_path(project_lib_dir) }}/*.*" "{{ _normalize_path(project_libdeps_dir) }}/*.*")
