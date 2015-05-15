win32 {
    HOMEDIR += $$(USERPROFILE)
}
else {
    HOMEDIR += $$(PWD)
}

INCLUDEPATH += "$$HOMEDIR/.platformio/packages/framework-arduinoavr/cores/arduino"
INCLUDEPATH += "$$HOMEDIR/.platformio/packages/toolchain-atmelavr/avr/include"

win32:INCLUDEPATH ~= s,/,\\,g

# DEFINES += __AVR_ATmega328__

OTHER_FILES += \
    platformio.ini

SOURCES += \
    src/main.c
