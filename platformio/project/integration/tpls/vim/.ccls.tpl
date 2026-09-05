% import shlex
%
{{ cc_path }}

{{"%c"}} {{ shlex.join(cc_flags) }}
{{"%cpp"}} {{ shlex.join(cxx_flags) }}

% for include in filter_includes(includes):
-I{{ !include }}
% end

% for define in defines:
-D{{ !define }}
% end
