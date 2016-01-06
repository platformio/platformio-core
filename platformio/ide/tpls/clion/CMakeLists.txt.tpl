cmake_minimum_required(VERSION 3.2)
project({{project_name}})

set(ENV{PATH} "{{env_path}}")
set(PLATFORMIO_CMD "{{platformio_path}}")

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
    PLATFORMIO_BUILD ALL
    COMMAND ${PLATFORMIO_CMD} -f -c clion run
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_custom_target(
    PLATFORMIO_UPLOAD ALL
    COMMAND ${PLATFORMIO_CMD} -f -c clion run --target upload
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_custom_target(
    PLATFORMIO_CLEAN ALL
    COMMAND ${PLATFORMIO_CMD} -f -c clion run --target clean
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_custom_target(
    PLATFORMIO_PROGRAM ALL
    COMMAND ${PLATFORMIO_CMD} -f -c clion run --target program
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_custom_target(
    PLATFORMIO_UPLOADFS ALL
    COMMAND ${PLATFORMIO_CMD} -f -c clion run --target uploadfs
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

add_custom_target(
    PLATFORMIO_UPDATE_ALL ALL
    COMMAND ${PLATFORMIO_CMD} -f -c clion update
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

% if src_files and any([f.endswith((".c", ".cpp")) for f in src_files]):
add_executable({{project_name}}
% for f in src_files:
% if f.endswith((".c", ".cpp")):
    {{f.replace("\\", "/")}}
% end
% end
)
% else:
#
# To enable code auto-completion, please specify path
# to main source file (*.c, *.cpp) and uncomment line below
#
# add_executable({{project_name}} src/main_change_me.cpp)
% end
