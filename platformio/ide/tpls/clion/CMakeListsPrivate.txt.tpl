set(ENV{PATH} "{{env_path}}")
set(PLATFORMIO_CMD "{{platformio_path}}")

% for include in includes:
% if include.startswith(user_home_dir):
% if "windows" in systype:
include_directories("$ENV{HOMEDRIVE}$ENV{HOMEPATH}{{include.replace(user_home_dir, '').replace("\\", "/")}}")
% else:
include_directories("$ENV{HOME}{{include.replace(user_home_dir, '').replace("\\", "/")}}")
% end
% else:
include_directories("{{include.replace("\\", "/")}}")
% end
% end