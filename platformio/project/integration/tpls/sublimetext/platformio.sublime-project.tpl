{
	"build_systems":
	[
		{
			"cmd":
			[
				"{{ platformio_path }}",
				"-c", "sublimetext",
				"run"
			],
			"file_regex": "^(..[^:\n]*):([0-9]+):?([0-9]+)?:? (.*)$",
			"name": "PlatformIO",
			"variants":
			[
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-c", "sublimetext",
						"run"
					],
					"file_regex": "^(..[^:\n]*):([0-9]+):?([0-9]+)?:? (.*)$",
					"name": "Build"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-c", "sublimetext",
						"run",
						"--target",
						"upload"
					],
					"file_regex": "^(..[^:\n]*):([0-9]+):?([0-9]+)?:? (.*)$",
					"name": "Upload"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-c", "sublimetext",
						"run",
						"--target",
						"clean"
					],
					"file_regex": "^(..[^:\n]*):([0-9]+):?([0-9]+)?:? (.*)$",
					"name": "Clean"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-c", "sublimetext",
						"test"
					],
					"file_regex": "^(..[^:\n]*):([0-9]+):?([0-9]+)?:? (.*)$",
					"name": "Test"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-c", "sublimetext",
						"run",
						"--target",
						"uploadfs"
					],
					"file_regex": "^(..[^:\n]*):([0-9]+):?([0-9]+)?:? (.*)$",
					"name": "Upload SPIFFS image"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-c", "sublimetext",
						"update"
					],
					"file_regex": "^(..[^:\n]*):([0-9]+):?([0-9]+)?:? (.*)$",
					"name": "Update platforms and libraries"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-c", "sublimetext",
						"upgrade"
					],
					"name": "Upgrade PlatformIO Core"
				}
			],
			"working_dir": "${project_path:${folder}}",
			"selector": "source.c, source.c++"
		}
	],
	"folders":
	[
		{
			"path": "."
		}
	],
    "settings":
    {
         "sublimegdb_workingdir": "{{project_dir}}",
         "sublimegdb_exec_cmd": "",
         "sublimegdb_commandline": "{{ platformio_path }} -f -c sublimetext debug --interface=gdb --interpreter=mi -x .pioinit"

    }
}
