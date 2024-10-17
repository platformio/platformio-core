# Blackmagic Probe improvements

I needed SRST under reset feature, this command has to be issued before scan, but this is currently impossible with current variables.

By changing the gdb init a bit this or even target power is possible

See: "Embedded Debugging with the Black Magic Probe", pp. 28

```
upload_protocol = blackmagic
upload_port = /dev/ttyBmpGdb
debug_tool = blackmagic
debug_port = ${this.upload_port} connect_srst
monitor_port = /dev/ttyBmpTarg
monitor_speed = 115200

```

debug_port = port [monitor_cmd]

debug_port can be /dev/ttyACM0 (/dev/ttyBmpGdb if you use the udev rules) or a Windows COM port, I use `${this.upload_port}` to use the same.

An optional param can be used to enable eg:

- tpwr (Target Power)
- connect_srst (Assert SRST during connect)

Currently it's not possibe to enable both, but this can easily be changed (iterate over args)
