{
    "configurations": [
        {
% import platform
% systype = platform.system().lower()
% if systype == "windows":
            "name": "Win32",
% elif systype == "darwin":
            "name": "Mac",
% else:
            "name": "Linux",
% end
            "includePath": [
% for include in includes:
                "{{include.replace('\\\\', '/').replace('\\', '/').replace('"', '\\"')}}",
% end
                ""
            ],
            "browse": {
                "limitSymbolsToIncludedHeaders": true,
                "databaseFilename": "",
                "path": [
% for include in includes:
                    "{{include.replace('\\\\', '/').replace('\\', '/').replace('"', '\\"')}}",
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