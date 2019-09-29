% for define in defines:
% tokens = define.split("=", 1)
% if len(tokens) > 1:
#DEFINE {{tokens[0].strip()}} {{tokens[1].strip()}}
% else:
#DEFINE {{tokens[0].strip()}}
% end
% end
