default_target: all

all:
	platformio -f -c qtcreator run

clean:
	platformio -f -c qtcreator run --target clean

