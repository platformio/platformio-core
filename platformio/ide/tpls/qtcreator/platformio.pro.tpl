% import re
%
% cpp_standards_remap = {
%   "0x": "11",
%   "1y": "14",
%   "1z": "17",
%   "2a": "20",
%   "2b": "23"
% }

win32 {
    HOMEDIR += $$(USERPROFILE)
}
else {
    HOMEDIR += $$(HOME)
}

% for include in filter_includes(includes):
% if include.startswith(user_home_dir):
INCLUDEPATH += "$${HOMEDIR}{{include.replace(user_home_dir, "")}}"
% else:
INCLUDEPATH += "{{include}}"
% end
% end

% for define in defines:
% tokens = define.split("##", 1)
DEFINES += "{{tokens[0].strip()}}"
% end

OTHER_FILES += platformio.ini

% for file in src_files:
% if file.endswith((".h", ".hpp")):
HEADERS += {{file}}
% else:
SOURCES += {{file}}
% end
% end

% STD_RE = re.compile(r"\-std=[a-z\+]+(\w+)")
% cxx_stds = STD_RE.findall(cxx_flags)
% if cxx_stds:
CONFIG += c++{{ cpp_standards_remap.get(cxx_stds[-1], cxx_stds[-1]) }}
% end
