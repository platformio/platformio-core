# !!! WARNING !!! AUTO-GENERATED FILE, PLEASE DO NOT MODIFY IT AND USE
# https://docs.platformio.org/page/projectconf/section_env_build.html#build-flags
#
# If you need to override existing CMake configuration or add extra,
# please create `CMakeListsUser.txt` in the root of project.
# The `CMakeListsUser.txt` will not be overwritten by PlatformIO.

% import os
% import re
%
% from platformio.project.helpers import load_build_metadata
%
% def _normalize_path(path):
%   if project_dir in path:
%     path = path.replace(project_dir, "${CMAKE_CURRENT_LIST_DIR}")
%   elif user_home_dir in path:
%     if "windows" in systype:
%       path = path.replace(user_home_dir, "${ENV_HOME_PATH}")
%     else:
%       path = path.replace(user_home_dir, "$ENV{HOME}")
%     end
%   end
%   return path
% end
%
% def _fix_lib_dirs(lib_dirs):
%   result = []
%   for lib_dir in lib_dirs:
%     if not os.path.isabs(lib_dir):
%       lib_dir = os.path.join(project_dir, lib_dir)
%     end
%     result.append(to_unix_path(os.path.normpath(lib_dir)))
%   end
%   return result
% end
%
% def _escape(text):
%   return to_unix_path(text).replace('"', '\\"')
% end
%
% def _get_lib_dirs(envname):
%   env_libdeps_dir = os.path.join(config.get("platformio", "libdeps_dir"), envname)
%   env_lib_extra_dirs = config.get("env:" + envname, "lib_extra_dirs", [])
%   return _fix_lib_dirs([env_libdeps_dir] + env_lib_extra_dirs)
% end
%
% envs = config.envs()


% if len(envs) > 1:
set(CMAKE_CONFIGURATION_TYPES "{{ ";".join(envs) }};" CACHE STRING "Build Types reflect PlatformIO Environments" FORCE)
% else:
set(CMAKE_CONFIGURATION_TYPES "{{ env_name }}" CACHE STRING "Build Types reflect PlatformIO Environments" FORCE)
% end

# Convert "Home Directory" that may contain unescaped backslashes on Windows
% if "windows" in systype:
file(TO_CMAKE_PATH $ENV{HOMEDRIVE}$ENV{HOMEPATH} ENV_HOME_PATH)
% end

% if svd_path:
set(CLION_SVD_FILE_PATH "{{ _normalize_path(svd_path) }}" CACHE FILEPATH "Peripheral Registers Definitions File" FORCE)
% end

SET(CMAKE_C_COMPILER "{{ _normalize_path(cc_path) }}")
SET(CMAKE_CXX_COMPILER "{{ _normalize_path(cxx_path) }}")
SET(CMAKE_CXX_FLAGS "{{ _normalize_path(to_unix_path(cxx_flags)) }}")
SET(CMAKE_C_FLAGS "{{ _normalize_path(to_unix_path(cc_flags)) }}")

% STD_RE = re.compile(r"\-std=[a-z\+]+(\w+)")
% cc_stds = STD_RE.findall(cc_flags)
% cxx_stds = STD_RE.findall(cxx_flags)
% if cc_stds:
SET(CMAKE_C_STANDARD {{ cc_stds[-1] }})
% end
% if cxx_stds:
set(CMAKE_CXX_STANDARD {{ cxx_stds[-1] }})
% end

if (CMAKE_BUILD_TYPE MATCHES "{{ env_name }}")
% for define in defines:
    add_definitions(-D{{!re.sub(r"([\"\(\)\ #])", r"\\\1", define)}})
% end

% for include in filter_includes(includes):
    include_directories("{{ _normalize_path(include) }}")
% end

    FILE(GLOB_RECURSE EXTRA_LIB_SOURCES
% for dir in _get_lib_dirs(env_name):
        {{  _normalize_path(dir) + "/*.*" }}
% end
    )
endif()

% leftover_envs = list(set(envs) ^ set([env_name]))
%
% ide_data = {}
% if leftover_envs:
%   ide_data = load_build_metadata(project_dir, leftover_envs)
% end
%
% for env, data in ide_data.items():
if (CMAKE_BUILD_TYPE MATCHES "{{ env }}")
%   for define in data["defines"]:
    add_definitions(-D{{!re.sub(r"([\"\(\)\ #])", r"\\\1", define)}})
%   end

%   for include in filter_includes(data["includes"]):
    include_directories("{{ _normalize_path(to_unix_path(include)) }}")
%   end

    FILE(GLOB_RECURSE EXTRA_LIB_SOURCES
%   for dir in _get_lib_dirs(env):
        {{  _normalize_path(dir) + "/*.*" }}
%   end
    )
endif()
% end

FILE(GLOB_RECURSE SRC_LIST
%   for path in (project_src_dir, project_lib_dir, project_test_dir):
    {{  _normalize_path(path) + "/*.*" }}
%   end
)

list(APPEND SRC_LIST ${EXTRA_LIB_SOURCES})
