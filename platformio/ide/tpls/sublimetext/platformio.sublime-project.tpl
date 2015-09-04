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
			"path": "{{env_path}}"
			"name": "PlatformIO",
			"variants":
			[
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
				}
			],
			"working_dir": "${project_path:${folder}}"
		}
	],
	"folders":
	[
		{
			"path": "."
		}
	]
}
