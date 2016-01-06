{
	"build_systems":
	[
		{
			"cmd":
			[
				"platformio",
				"-f", "-c", "sublimetext",
				"run"
			],
			"name": "PlatformIO",
			"variants":
			[
				{
					"cmd":
					[
						"platformio",
						"-f", "-c", "sublimetext",
						"run"
					],
					"name": "Build"
				},
				{
					"cmd":
					[
						"platformio",
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
						"platformio",
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
						"platformio",
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
						"platformio",
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
						"platformio",
						"-f", "-c", "sublimetext",
						"update"
					],
					"name": "Update platforms and libraries"
				}
			],
			"working_dir": "${project_path:${folder}}",
			"selector": "source.c, source.c++",
			"path": "{{env_path}}"
		}
	],
	"folders":
	[
		{
			"path": "."
		}
	]
}
