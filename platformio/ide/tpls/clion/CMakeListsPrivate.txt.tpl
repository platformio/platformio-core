set(ENV{PATH} "{{env_path}}")
set(PLATFORMIO_CMD "{{platformio_path}}")

SET(CMAKE_C_COMPILER "{{cc_path.replace("\\", "/")}}")
SET(CMAKE_CXX_COMPILER "{{cxx_path.replace("\\", "/")}}")
SET(CMAKE_CXX_FLAGS_DISTRIBUTION "{{cxx_flags}}")
SET(CMAKE_C_FLAGS_DISTRIBUTION "{{cc_flags}}")
set(CMAKE_CXX_STANDARD 11)

% for define in defines:
add_definitions(-D{{!define}})
% end

% for include in includes:
% if include.startswith(user_home_dir):
% if "windows" in systype:
include_directories("$ENV{HOMEDRIVE}$ENV{HOMEPATH}{{include.replace(user_home_dir, '').replace("\\", "/")}}")
% else:
include_directories("$ENV{HOME}{{include.replace(user_home_dir, '').replace("\\", "/")}}")
% end
% else:
include_directories("{{include.replace("\\", "/")}}")
% end
% end

FILE(GLOB_RECURSE SRC_LIST "{{project_src_dir.replace("\\", "/")}}/*.*")
