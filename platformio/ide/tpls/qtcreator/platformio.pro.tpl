win32 {
    HOMEDIR += $$(USERPROFILE)
}
else {
    HOMEDIR += $$(HOME)
}

% for include in includes:
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
