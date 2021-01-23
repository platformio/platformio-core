clang

{{"%c"}} {{ !cc_flags }}
{{"%cpp"}} {{ !cxx_flags }}

% for include in filter_includes(includes):
-I{{ !include }}
% end

% for define in defines:
-D{{ !define }}
% end
