{
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
    "version": "0.1.0",
    "tasks": [
        {
            "taskName": "PlatformIo build",
            "command": "platformio",
            "args": [
                "run"
            ],
            "isBuildCommand": true,
            "isShellCommand": true,
            "echoCommand": true,
            "problemMatcher": {
                "owner": "cpp",
                "fileLocation": [
                    "relative",
                    "${workspaceRoot}"
                ],
                "pattern": {
                    "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            },
            "showOutput": "always"
        },
        {
            "taskName": "PlatformIo clean",
            "command": "platformio",
            "args": [
                "run",
                "--target",
                "clean"
            ],
            "isShellCommand": true,
            "echoCommand": true,
            "showOutput": "always"
        },
        {
            "taskName": "PlatformIo rebuild project index",
            "command": "platformio",
            "args": [
                "init",
                "--ide",
                "vscode"
            ],
            "isShellCommand": true,
            "echoCommand": true,
            "showOutput": "always"
        },
        {
            "taskName": "PlatformIo update",
            "command": "platformio",
            "args": [
                "update"
            ],
            "isShellCommand": true,
            "echoCommand": true,
            "showOutput": "always"
        },
        {
            "taskName": "PlatformIo upgrade",
            "command": "platformio",
            "args": [
                "upgrade"
            ],
            "isShellCommand": true,
            "echoCommand": true,
            "showOutput": "always"
        },
        {
            "taskName": "PlatformIo upload",
            "command": "platformio",
            "args": [
                "run",
                "--target",
                "upload"
            ],
            "isShellCommand": true,
            "echoCommand": true,
            "problemMatcher": {
                "owner": "cpp",
                "fileLocation": [
                    "relative",
                    "${workspaceRoot}"
                ],
                "pattern": {
                    "regexp": "^(.*):(\\d+):(\\d+):\\s+(warning|error):\\s+(.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            },
            "showOutput": "always"
        }
    ]
}