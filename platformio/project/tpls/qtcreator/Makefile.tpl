all:
	platformio -c qtcreator run

# forward any other target (clean, build, etc.) to pio run
{{'%'}}:
	platformio -c qtcreator run --target $*
