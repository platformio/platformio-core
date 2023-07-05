% from platformio.compat import shlex_join
%
{{shlex_join(cc_flags).replace('-mlongcalls', '-mlong-calls')}}
