% import json
% import os
% import re
%
% recommendations = set(["platformio.platformio-ide"])
% previous_json = os.path.join(project_dir, ".vscode", "extensions.json")
% if os.path.isfile(previous_json):
%   fp = open(previous_json)
%   contents = re.sub(r"^\s*//.*$", "", fp.read(), flags=re.M).strip()
%   fp.close()
%   if contents:
%       recommendations |= set(json.loads(contents).get("recommendations", []))
%   end
% end
{
    // See http://go.microsoft.com/fwlink/?LinkId=827846
    // for the documentation about the extensions.json format
    "recommendations": [
% for i, item in enumerate(sorted(recommendations)):
        "{{ item }}"{{ ("," if (i + 1) < len(recommendations) else "") }}
% end
    ]
}
