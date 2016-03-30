<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<CodeBlocks_project_file>
	<FileVersion major="1" minor="6" />
	<Project>
		<Option title="{{project_name}}" />
		<Option makefile_is_custom="1" />
		<Option pch_mode="2" />
		<Option compiler="gcc" />
		<MakeCommands>
			<Build command="{{platformio_path}} -f -c codeblocks run" />
			<CompileFile command="{{platformio_path}} -f -c codeblocks run" />
			<Clean command="{{platformio_path}} -f -c codeblocks run -t clean" />
			<DistClean command="{{platformio_path}} -f -c codeblocks run -t clean" />
			<AskRebuildNeeded command="1" />
			<SilentBuild command="{{platformio_path}} -f -c codeblocks run &gt; $(CMD_NULL)" />
		</MakeCommands>
		<Build>
			<Target title="Debug">
				<Option type="1" />
				<Option compiler="gcc" />
				<Option use_console_runner="0" />
				<MakeCommands>
					<Build command="{{platformio_path}} -f -c codeblocks run" />
					<CompileFile command="{{platformio_path}} -f -c codeblocks run" />
					<Clean command="{{platformio_path}} -f -c codeblocks run -t clean" />
					<DistClean command="{{platformio_path}} -f -c codeblocks run -t clean" />
					<AskRebuildNeeded command="1" />
					<SilentBuild command="{{platformio_path}} -f -c codeblocks run &gt; $(CMD_NULL)" />
				</MakeCommands>
			</Target>
			<Target title="Release">
				<Option type="1" />
				<Option compiler="gcc" />
				<Option use_console_runner="0" />
				<MakeCommands>
					<Build command="{{platformio_path}} -f -c codeblocks run" />
					<CompileFile command="{{platformio_path}} -f -c codeblocks run" />
					<Clean command="{{platformio_path}} -f -c codeblocks run -t clean" />
					<DistClean command="{{platformio_path}} -f -c codeblocks run -t clean" />
					<AskRebuildNeeded command="1" />
					<SilentBuild command="{{platformio_path}} -f -c codeblocks run &gt; $(CMD_NULL)" />
				</MakeCommands>
			</Target>
		</Build>
		<Compiler>
			% for define in defines:
			<Add option="-D{{define}}"/>
			% end
			% for include in includes:
			<Add directory="{{include.replace("\\", "/")}}"/>
			% end		
		</Compiler>
		<Unit filename="platformio.ini" />
		% for file in src_files:
		<Unit filename="{{file.replace("\\", "/")}}"></Unit>
		% end
	</Project>
</CodeBlocks_project_file>
