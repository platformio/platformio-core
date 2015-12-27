cmake_minimum_required(VERSION 3.2)
project({{project_name}})

set(ENV{PATH} "{{env_path}}")
set(PLATFORMIO_CMD "{{platformio_path}}")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

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

% for define in defines:
add_definitions(-D{{!define}})
% end

add_custom_target(
    platformio_build ALL
    COMMAND ${PLATFORMIO_CMD} -f -c emacs run
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_custom_target(
    platformio_upload ALL
    COMMAND ${PLATFORMIO_CMD} -f -c emacs run --target upload
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_custom_target(
    platformio_clean ALL
    COMMAND ${PLATFORMIO_CMD} -f -c emacs run --target clean
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_custom_target(
    platformio_update ALL
    COMMAND ${PLATFORMIO_CMD} -f -c emacs update
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

% if main_src_file:
add_executable({{project_name}} {{main_src_file.replace("\\", "/")}})
% else:
#
# To enable code auto-completion, please specify path
# to main source file (*.c, *.cpp) and uncomment line below
#
# add_executable({{project_name}} src/main_change_me.cpp)
% end
