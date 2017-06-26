{
    "version": "0.1.0",
    "runner": "terminal",
    "command": "{{platformio_path}}",
    "isShellCommand": false,
    "args": ["-c", "vscode"],
    "showOutput": "always",
    "echoCommand": false,
    "suppressTaskName": true,
    "tasks": [
        {
            "taskName": "PlatformIO: Build",
            "isBuildCommand": true,
            "args": ["run"],
            "problemMatcher": {
                "owner": "cpp",
                "fileLocation": ["relative", "${workspaceRoot}"],
                "pattern": {
                    "regexp": "^([^:\\n]+):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
        {
            "taskName": "PlatformIO: Clean",
            "args": ["run", "-t", "clean"]
        },
        {
            "taskName": "PlatformIO: Upload",
            "args": ["run", "-t", "upload"],
            "problemMatcher": {
                "owner": "cpp",
                "fileLocation": ["relative", "${workspaceRoot}"],
                "pattern": {
                    "regexp": "^([^:\\n]+):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
        {
            "taskName": "PlatformIO: Upload using Programmer",
            "args": ["run", "-t", "program"],
            "problemMatcher": {
                "owner": "cpp",
                "fileLocation": ["relative", "${workspaceRoot}"],
                "pattern": {
                    "regexp": "^([^:\\n]+):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
        {
            "taskName": "PlatformIO: Upload SPIFFS image",
            "args": ["run", "-t", "uploadfs"],
            "problemMatcher": {
                "owner": "cpp",
                "fileLocation": ["relative", "${workspaceRoot}"],
                "pattern": {
                    "regexp": "^([^:\\n]+):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
        {
            "taskName": "PlatformIO: Upload and Monitor",
            "args": ["run", "-t", "upload", "-t", "monitor"],
            "problemMatcher": {
                "owner": "cpp",
                "fileLocation": ["relative", "${workspaceRoot}"],
                "pattern": {
                    "regexp": "^([^:\\n]+):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
        {
            "taskName": "PlatformIO: Test",
            "args": ["test"],
            "problemMatcher": {
                "owner": "cpp",
                "fileLocation": ["relative", "${workspaceRoot}"],
                "pattern": {
                    "regexp": "^([^:\\n]+):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
        {
            "taskName": "PlatformIO: Update platforms and libraries",
            "args": ["update"]
        },
        {
            "taskName": "PlatformIO: Upgrade PIO Core",
            "args": ["upgrade"]
        }
    ]
}