all:
	platformio -c qtcreator run

# regenerate project files to reflect platformio.ini changes
project-update:
	@echo "This will overwrite project files and delete .pio cache.  Are you sure? [y/N] " \
	    && read ans && [ $${ans:-'N'} = 'y' ]
	rm -rf .pio/
	platformio project init --ide qtcreator

# forward any other target (clean, build, etc.) to pio run
{{'%'}}:
	platformio -c qtcreator run --target $*
