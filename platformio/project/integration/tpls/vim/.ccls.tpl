% from platformio.compat import shlex_join
%
clang

{{"%c"}} {{ shlex_join(cc_flags) }}
{{"%cpp"}} {{ shlex_join(cxx_flags) }}

% for include in filter_includes(includes):
-I{{ !include }}
% end

% for define in defines:
-D{{ !define }}
% end
