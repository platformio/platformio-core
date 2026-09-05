% import shlex
%
{{shlex.join(cxx_flags).replace('-mlongcalls', '-mlong-calls')}}
