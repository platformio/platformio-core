{
    "configurations": [
        {
            "includePath": [
% for include in includes:
                "{{include.replace('"', '\\"')}}",
% end
                ""
            ],
            "browse": {
                "limitSymbolsToIncludedHeaders": true,
                "databaseFilename": "",
                "path": [
% for include in includes:
                    "{{include.replace('"', '\\"')}}",
% end
                    ""
                ]
            },
            "defines": [
% for define in defines:
                "{{!define.replace('"', '\\"')}}",
% end
                ""
            ]
        }
    ]
}