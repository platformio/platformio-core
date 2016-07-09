set(ENV{PATH} "{{env_path}}")
set(PLATFORMIO_CMD "{{platformio_path}}")

SET(CMAKE_C_COMPILER "{{cc_path}}")
SET(CMAKE_CXX_COMPILER "{{cxx_path}}")
SET(CMAKE_CXX_FLAGS_DISTRIBUTION "{{cxx_flags}}")
SET(CMAKE_C_FLAGS_DISTRIBUTION "{{cc_flags}}")

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

aux_source_directory({{project_src_dir}} SRC_LIST)
