{
    "configurations": [
% for osidx, os in enumerate(['Mac', 'Linux', 'Win32']):
        {
            "name": "{{os}}",
            "includePath": [
% for idx, include in enumerate(includes):
                "{{include.replace("\\", "/")}}"\\
% if idx < len(includes) - 1:
,
% end
% end

            ],
            "defines": [
% for idx, define in enumerate(defines):
                "{{define}}"\\
% if idx < len(defines) - 1:
,
% end
% end

            ],
            "browse": {
                "path": [
% for idx, include in enumerate(includes):
                    "{{include.replace("\\", "/")}}"\\
% if idx < len(includes) - 1:
,
% end
% end

                ],
                "limitSymbolsToIncludedHeaders": true,
                "databaseFilename": "${workspaceRoot}/.vscode/browse.vc.db"
            }
        }\\
% if osidx < 2:
,
% end
% end

    ]
}