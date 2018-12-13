{
	"build_systems":
	[
		{
			"cmd":
			[
				"{{ platformio_path }}",
				"-f", "-c", "sublimetext",
				"run"
			],
			"name": "PlatformIO",
			"variants":
			[
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-f", "-c", "sublimetext",
						"run"
					],
					"name": "Build"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-f", "-c", "sublimetext",
						"run",
						"--target",
						"upload"
					],
					"name": "Upload"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-f", "-c", "sublimetext",
						"run",
						"--target",
						"clean"
					],
					"name": "Clean"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-f", "-c", "sublimetext",
						"test"
					],
					"name": "Test"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-f", "-c", "sublimetext",
						"run",
						"--target",
						"program"
					],
					"name": "Upload using Programmer"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-f", "-c", "sublimetext",
						"run",
						"--target",
						"uploadfs"
					],
					"name": "Upload SPIFFS image"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-f", "-c", "sublimetext",
						"update"
					],
					"name": "Update platforms and libraries"
				},
				{
					"cmd":
					[
						"{{ platformio_path }}",
						"-f", "-c", "sublimetext",
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
