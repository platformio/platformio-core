{
	"build_systems":
	[
		{
			"cmd":
			[
				"platformio",
				"--force",
				"run"
			],
			"name": "PlatformIO",
			"variants":
			[
				{
					"cmd":
					[
						"platformio",
						"--force",
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
						"--force",
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
