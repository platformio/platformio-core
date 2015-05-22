win32 {
    HOMEDIR += $$(USERPROFILE)
}
else {
    HOMEDIR += $$(PWD)
}

% for include in includes:
INCLUDEPATH += "{{include}}"
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
