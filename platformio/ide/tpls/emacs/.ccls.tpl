% import re
% STD_RE = re.compile(r"\-std=[a-z\+]+(\d+)")
% cc_stds = STD_RE.findall(cc_flags)
% cxx_stds = STD_RE.findall(cxx_flags)
%
%
clang

% if cc_stds:
{{"%c"}} -std=c{{ cc_stds[-1] }}
% end
% if cxx_stds:
{{"%cpp"}} -std=c++{{ cxx_stds[-1] }}
% end

% for include in includes:
-I{{ include }}
% end

% for define in defines:
-D{{ define }}
% end
