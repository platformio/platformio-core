% for define in defines:
% tokens = define.split("=", 1)
% if len(tokens) > 1:
#define {{tokens[0].strip()}} {{!tokens[1].strip()}}
% else:
#define {{define}}
% end
% end
