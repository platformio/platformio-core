cmake_minimum_required(VERSION 3.2)
project(clion)

set(ENV{PATH} "/Volumes/SOFT/Projects/GitHub/platformio/origin/.tox/develop/bin:/usr/local/opt/pyenv/shims:/Users/ikravets/.pyenv/shims:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/sbin")
set(PLATFORMIO_CMD "/Volumes/SOFT/Projects/GitHub/platformio/origin/.tox/develop/bin/platformio")

include_directories("$ENV{HOME}/.platformio/packages/framework-arduinoavr/variants/standard")
include_directories("$ENV{HOME}/.platformio/packages/framework-arduinoavr/cores/arduino")
include_directories("$ENV{HOME}/.platformio/packages/toolchain-atmelavr/avr/include")
include_directories("$ENV{HOME}/.platformio/packages/toolchain-atmelavr/bfd/include")
include_directories("$ENV{HOME}/.platformio/packages/toolchain-atmelavr/lib/gcc/avr/4.8.1/include")
include_directories("$ENV{HOME}/.platformio/packages/toolchain-atmelavr/lib/gcc/avr/4.8.1/include-fixed")

add_definitions(-DF_CPU=16000000L)
add_definitions(-DARDUINO_ARCH_AVR)
add_definitions(-DARDUINO_AVR_UNO)
add_definitions(-DARDUINO=10605)
add_definitions(-DPLATFORMIO=020304)
add_definitions(-D__AVR_ATmega328P__)

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

add_executable(clion src/blink.cpp)
