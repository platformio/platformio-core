all:
	platformio -c qtcreator run

# regenerate project files to reflect platformio.ini changes
project-update:
	platformio project init --ide qtcreator

# forward any other target (clean, build, etc.) to pio run
{{'%'}}:
	platformio -c qtcreator run --target $*
