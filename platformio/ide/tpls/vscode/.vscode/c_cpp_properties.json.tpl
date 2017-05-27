{
    "configurations": [
        {
            "includePath": [
% for include in includes:
                "{{include.replace('"', '\\"').replace('\\\\', '/').replace('\\', '/')}}",
% end
                ""
            ],
            "browse": {
                "limitSymbolsToIncludedHeaders": true,
                "databaseFilename": "",
                "path": [
% for include in includes:
                    "{{include.replace('"', '\\"').replace('\\\\', '/').replace('\\', '/')}}",
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