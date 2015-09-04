cmake_minimum_required(VERSION 3.2)
project({{project_name}})

set(ENV{PATH} "{{env_path}}")
set(PLATFORMIO_CMD "{{platformio_path}}")

% for include in includes:
% if include.startswith(user_home_dir):
include_directories("$ENV{HOME}{{include.replace(user_home_dir, '').replace("\\", "/")}}")
% else:
include_directories("{{include}}")
% end
% end

% for define in defines:
add_definitions(-D{{define}})
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