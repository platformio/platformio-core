% import json
% import os
%
% def _escape(text):
%   return text.replace('"', '\"')
% end
%
% def _escape_path(path):
%   return path.replace('\\\\', '/').replace('\\', '/').replace('"', '\\"')
% end
%
% def get_pio_configurations():
%  predebug = {
%    "type": "platformio-debug",
%    "request": "launch",
%    "name": "PIO Debug (skip Pre-Debug)",
%    "executable": _escape_path(prog_path),
%    "projectEnvName": env_name if forced_env_name else default_debug_env_name,
%    "toolchainBinDir": _escape_path(os.path.dirname(cc_path)),
%    "internalConsoleOptions": "openOnSessionStart",
%  }
%
%  if svd_path:
%    predebug["svdPath"] = _escape_path(svd_path)
%  end
%  debug = predebug.copy()
%  debug["name"] = "PIO Debug"
%  debug["preLaunchTask"] = {
%    "type": "PlatformIO",
%    "task": ("Pre-Debug (%s)" % env_name) if len(config.envs()) > 1 and forced_env_name else "Pre-Debug",
%  }
%  noloading = predebug.copy()
%  noloading["name"] = "PIO Debug (without uploading)"
%  noloading["loadMode"] = "manual"
%  return [debug, predebug, noloading]
% end
%
% def _remove_comments(lines):
%  data = ""
%  for line in lines:
%    line = line.strip()
%    if not line.startswith("//"):
%      data += line
%    end
%  end
%  return data
% end
%
% def _contains_custom_configurations(launch_config):
%  pio_config_names = [
%    c["name"]
%    for c in get_pio_configurations()
%  ]
%  return any(
%    c.get("type", "") != "platformio-debug"
%    or c.get("name", "") in pio_config_names
%    for c in launch_config.get("configurations", [])
%  )
% end
%
% def _remove_pio_configurations(launch_config):
%  if "configurations" not in launch_config:
%    return launch_config
%  end
%
%  pio_config_names = [
%    c["name"]
%    for c in get_pio_configurations()
%  ]
%  external_configurations = [
%    c
%    for c in launch_config["configurations"]
%    if c.get("type", "") != "platformio-debug" or c.get("name", "") not in pio_config_names
%  ]
%
%  launch_config["configurations"] = external_configurations
%  return launch_config
% end
%
% def get_launch_configuration():
%  launch_config = {"version": "0.2.0", "configurations": []}
%  launch_file = os.path.join(project_dir, ".vscode", "launch.json")
%  if os.path.isfile(launch_file):
%    with open(launch_file, "r", encoding="utf8") as fp:
%      launch_data = _remove_comments(fp.readlines())
%      try:
%        prev_config = json.loads(launch_data)
%        if _contains_custom_configurations(prev_config):
%          launch_config = _remove_pio_configurations(prev_config)
%        end
%      except:
%        pass
%      end
%    end
%  end
%  launch_config["configurations"].extend(get_pio_configurations())
%  return launch_config
% end
%
// AUTOMATICALLY GENERATED FILE. PLEASE DO NOT MODIFY IT MANUALLY
//
// PlatformIO Debugging Solution
//
// Documentation: https://docs.platformio.org/en/latest/plus/debugging.html
// Configuration: https://docs.platformio.org/en/latest/projectconf/sections/env/options/debug/index.html

{{ json.dumps(get_launch_configuration(), indent=4, ensure_ascii=False) }}
