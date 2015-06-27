win32 {
    HOMEDIR += $$(USERPROFILE)
}
else {
    HOMEDIR += $$(PWD)
}

% for include in includes:
% if include.startswith(user_home_dir):
INCLUDEPATH += "${HOME}{{include.replace(user_home_dir, "")}}"
% else:
INCLUDEPATH += "{{include}}"
% end
% end

win32:INCLUDEPATH ~= s,/,\\,g

% for define in defines:
DEFINES += "{{define}}"
% end

OTHER_FILES += \
    platformio.ini

SOURCES += \
	% for file in srcfiles:
    {{file}}
    % end
