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
DEFINES += "{{define}}"
% end

OTHER_FILES += \
    platformio.ini

SOURCES += \
	% for file in src_files:
    {{file}}
    % end
