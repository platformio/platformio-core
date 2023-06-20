% from platformio.compat import shlex_join
%
{{shlex_join(cxx_flags).replace('-mlongcalls', '-mlong-calls')}}
