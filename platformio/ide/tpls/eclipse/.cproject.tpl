<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?fileVersion 4.0.0?><cproject storage_type_id="org.eclipse.cdt.core.XmlProjectDescriptionStorage">
	<storageModule moduleId="org.eclipse.cdt.core.settings">
		<cconfiguration id="0.910961921">
			<storageModule buildSystemId="org.eclipse.cdt.managedbuilder.core.configurationDataProvider" id="0.910961921" moduleId="org.eclipse.cdt.core.settings" name="Default">
				<externalSettings/>
				<extensions>
					<extension id="org.eclipse.cdt.core.ELF" point="org.eclipse.cdt.core.BinaryParser"/>
					<extension id="org.eclipse.cdt.core.VCErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GmakeErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.CWDLocator" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GCCErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GASErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GLDErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
				</extensions>
			</storageModule>
			<storageModule moduleId="cdtBuildSystem" version="4.0.0">
				<configuration artifactName="{{project_name}}" buildProperties="" description="" id="0.910961921" name="Default" parent="org.eclipse.cdt.build.core.prefbase.cfg">
					<folderInfo id="0.910961921." name="/" resourcePath="">
						<toolChain id="org.eclipse.cdt.build.core.prefbase.toolchain.952979152" name="No ToolChain" resourceTypeBasedDiscovery="false" superClass="org.eclipse.cdt.build.core.prefbase.toolchain">
							<targetPlatform binaryParser="org.eclipse.cdt.core.ELF" id="org.eclipse.cdt.build.core.prefbase.toolchain.952979152.52310970" name=""/>
							<builder arguments="-f -c eclipse" cleanBuildTarget="run --target clean" command="platformio" id="org.eclipse.cdt.build.core.settings.default.builder.1519453406" incrementalBuildTarget="run" keepEnvironmentInBuildfile="false" managedBuildOn="false" name="Gnu Make Builder" superClass="org.eclipse.cdt.build.core.settings.default.builder"/>
							<tool id="org.eclipse.cdt.build.core.settings.holder.libs.1409095472" name="holder for library settings" superClass="org.eclipse.cdt.build.core.settings.holder.libs"/>
							<tool id="org.eclipse.cdt.build.core.settings.holder.1624502120" name="Assembly" superClass="org.eclipse.cdt.build.core.settings.holder">
								<option id="org.eclipse.cdt.build.core.settings.holder.incpaths.239157887" name="Include Paths" superClass="org.eclipse.cdt.build.core.settings.holder.incpaths" valueType="includePath">
									% cleaned_includes = filter_includes(includes, ["toolchain"])
									% for include in cleaned_includes:
                                    % if include.startswith(user_home_dir):
                                    % if "windows" in systype:
									<listOptionValue builtIn="false" value="${USERPROFILE}{{include.replace(user_home_dir, '')}}"/>
									% else:
									<listOptionValue builtIn="false" value="${HOME}{{include.replace(user_home_dir, '')}}"/>
									% end
                                    % else:
									<listOptionValue builtIn="false" value="{{include}}"/>
									% end
									% end
								</option>
								<option id="org.eclipse.cdt.build.core.settings.holder.symbols.922107295" name="Symbols" superClass="org.eclipse.cdt.build.core.settings.holder.symbols" valueType="definedSymbols">
									% for define in defines:
									<listOptionValue builtIn="false" value="{{define}}"/>
									% end
								</option>
								<inputType id="org.eclipse.cdt.build.core.settings.holder.inType.149990277" languageId="org.eclipse.cdt.core.assembly" languageName="Assembly" sourceContentType="org.eclipse.cdt.core.asmSource" superClass="org.eclipse.cdt.build.core.settings.holder.inType"/>
							</tool>
							<tool id="org.eclipse.cdt.build.core.settings.holder.54121539" name="GNU C++" superClass="org.eclipse.cdt.build.core.settings.holder">
								<option id="org.eclipse.cdt.build.core.settings.holder.incpaths.1096940598" name="Include Paths" superClass="org.eclipse.cdt.build.core.settings.holder.incpaths" valueType="includePath">
									% for include in cleaned_includes:
                                    % if include.startswith(user_home_dir):
                                    % if "windows" in systype:
									<listOptionValue builtIn="false" value="${USERPROFILE}{{include.replace(user_home_dir, '')}}"/>
									% else:
									<listOptionValue builtIn="false" value="${HOME}{{include.replace(user_home_dir, '')}}"/>
                                    % end
                                    % else:
									<listOptionValue builtIn="false" value="{{include}}"/>
									% end
									% end
								</option>
								<option id="org.eclipse.cdt.build.core.settings.holder.symbols.1198905600" name="Symbols" superClass="org.eclipse.cdt.build.core.settings.holder.symbols" valueType="definedSymbols">
									% for define in defines:
									<listOptionValue builtIn="false" value="{{define}}"/>
									% end
								</option>
								<inputType id="org.eclipse.cdt.build.core.settings.holder.inType.762536863" languageId="org.eclipse.cdt.core.g++" languageName="GNU C++" sourceContentType="org.eclipse.cdt.core.cxxSource,org.eclipse.cdt.core.cxxHeader" superClass="org.eclipse.cdt.build.core.settings.holder.inType"/>
							</tool>
							<tool id="org.eclipse.cdt.build.core.settings.holder.1310559623" name="GNU C" superClass="org.eclipse.cdt.build.core.settings.holder">
								<option id="org.eclipse.cdt.build.core.settings.holder.incpaths.41298875" name="Include Paths" superClass="org.eclipse.cdt.build.core.settings.holder.incpaths" valueType="includePath">
									% for include in cleaned_includes:
                                    % if include.startswith(user_home_dir):
                                    % if "windows" in systype:
									<listOptionValue builtIn="false" value="${USERPROFILE}{{include.replace(user_home_dir, '')}}"/>
									% else:
									<listOptionValue builtIn="false" value="${HOME}{{include.replace(user_home_dir, '')}}"/>
                                    % end
                                    % else:
									<listOptionValue builtIn="false" value="{{include}}"/>
									% end
									% end
								</option>
								<option id="org.eclipse.cdt.build.core.settings.holder.symbols.884639970" name="Symbols" superClass="org.eclipse.cdt.build.core.settings.holder.symbols" valueType="definedSymbols">
									% for define in defines:
									<listOptionValue builtIn="false" value="{{define}}"/>
									% end
								</option>
								<inputType id="org.eclipse.cdt.build.core.settings.holder.inType.549319812" languageId="org.eclipse.cdt.core.gcc" languageName="GNU C" sourceContentType="org.eclipse.cdt.core.cSource,org.eclipse.cdt.core.cHeader" superClass="org.eclipse.cdt.build.core.settings.holder.inType"/>
							</tool>
						</toolChain>
					</folderInfo>
				</configuration>
			</storageModule>
			<storageModule moduleId="org.eclipse.cdt.core.externalSettings"/>
		</cconfiguration>
		<cconfiguration id="0.910961921.1363900502">
			<storageModule buildSystemId="org.eclipse.cdt.managedbuilder.core.configurationDataProvider" id="0.910961921.1363900502" moduleId="org.eclipse.cdt.core.settings" name="Debug">
				<externalSettings/>
				<extensions>
					<extension id="org.eclipse.cdt.core.ELF" point="org.eclipse.cdt.core.BinaryParser"/>
					<extension id="org.eclipse.cdt.core.VCErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GmakeErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.CWDLocator" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GCCErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GASErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
					<extension id="org.eclipse.cdt.core.GLDErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
				</extensions>
			</storageModule>
			<storageModule moduleId="cdtBuildSystem" version="4.0.0">
				<configuration artifactName="mbed" buildProperties="" description="" id="0.910961921.1363900502" name="Debug" parent="org.eclipse.cdt.build.core.prefbase.cfg">
					<folderInfo id="0.910961921.1363900502." name="/" resourcePath="">
						<toolChain id="org.eclipse.cdt.build.core.prefbase.toolchain.2116690625" name="No ToolChain" resourceTypeBasedDiscovery="false" superClass="org.eclipse.cdt.build.core.prefbase.toolchain">
							<targetPlatform binaryParser="org.eclipse.cdt.core.ELF" id="org.eclipse.cdt.build.core.prefbase.toolchain.2116690625.848954921" name=""/>
							<builder arguments="-f -c eclipse debug" cleanBuildTarget="run --target clean" command="platformio" enableCleanBuild="false" id="org.eclipse.cdt.build.core.settings.default.builder.985867833" incrementalBuildTarget="" keepEnvironmentInBuildfile="false" managedBuildOn="false" name="Gnu Make Builder" superClass="org.eclipse.cdt.build.core.settings.default.builder"/>
							<tool id="org.eclipse.cdt.build.core.settings.holder.libs.1855678035" name="holder for library settings" superClass="org.eclipse.cdt.build.core.settings.holder.libs"/>
							<tool id="org.eclipse.cdt.build.core.settings.holder.30528994" name="Assembly" superClass="org.eclipse.cdt.build.core.settings.holder">
								<option id="org.eclipse.cdt.build.core.settings.holder.incpaths.794801023" name="Include Paths" superClass="org.eclipse.cdt.build.core.settings.holder.incpaths" valueType="includePath">
									% for include in cleaned_includes:
                                    % if include.startswith(user_home_dir):
                                    % if "windows" in systype:
									<listOptionValue builtIn="false" value="${USERPROFILE}{{include.replace(user_home_dir, '')}}"/>
									% else:
									<listOptionValue builtIn="false" value="${HOME}{{include.replace(user_home_dir, '')}}"/>
									% end
                                    % else:
									<listOptionValue builtIn="false" value="{{include}}"/>
									% end
									% end
								</option>
								<option id="org.eclipse.cdt.build.core.settings.holder.symbols.1743427839" name="Symbols" superClass="org.eclipse.cdt.build.core.settings.holder.symbols" valueType="definedSymbols">
									% for define in defines:
									<listOptionValue builtIn="false" value="{{define}}"/>
									% end
								</option>
								<inputType id="org.eclipse.cdt.build.core.settings.holder.inType.919136836" languageId="org.eclipse.cdt.core.assembly" languageName="Assembly" sourceContentType="org.eclipse.cdt.core.asmSource" superClass="org.eclipse.cdt.build.core.settings.holder.inType"/>
							</tool>
							<tool id="org.eclipse.cdt.build.core.settings.holder.1146422798" name="GNU C++" superClass="org.eclipse.cdt.build.core.settings.holder">
								<option id="org.eclipse.cdt.build.core.settings.holder.incpaths.650084869" name="Include Paths" superClass="org.eclipse.cdt.build.core.settings.holder.incpaths" useByScannerDiscovery="false" valueType="includePath">
									% for include in cleaned_includes:
                                    % if include.startswith(user_home_dir):
                                    % if "windows" in systype:
									<listOptionValue builtIn="false" value="${USERPROFILE}{{include.replace(user_home_dir, '')}}"/>
									% else:
									<listOptionValue builtIn="false" value="${HOME}{{include.replace(user_home_dir, '')}}"/>
									% end
                                    % else:
									<listOptionValue builtIn="false" value="{{include}}"/>
									% end
									% end
								</option>
								<option id="org.eclipse.cdt.build.core.settings.holder.symbols.2055633423" name="Symbols" superClass="org.eclipse.cdt.build.core.settings.holder.symbols" useByScannerDiscovery="false" valueType="definedSymbols">
									% for define in defines:
									<listOptionValue builtIn="false" value="{{define}}"/>
									% end
								</option>
								<inputType id="org.eclipse.cdt.build.core.settings.holder.inType.445650141" languageId="org.eclipse.cdt.core.g++" languageName="GNU C++" sourceContentType="org.eclipse.cdt.core.cxxSource,org.eclipse.cdt.core.cxxHeader" superClass="org.eclipse.cdt.build.core.settings.holder.inType"/>
							</tool>
							<tool id="org.eclipse.cdt.build.core.settings.holder.1637357529" name="GNU C" superClass="org.eclipse.cdt.build.core.settings.holder">
								<option id="org.eclipse.cdt.build.core.settings.holder.incpaths.1246337321" name="Include Paths" superClass="org.eclipse.cdt.build.core.settings.holder.incpaths" useByScannerDiscovery="false" valueType="includePath">
									% for include in cleaned_includes:
                                    % if include.startswith(user_home_dir):
                                    % if "windows" in systype:
									<listOptionValue builtIn="false" value="${USERPROFILE}{{include.replace(user_home_dir, '')}}"/>
									% else:
									<listOptionValue builtIn="false" value="${HOME}{{include.replace(user_home_dir, '')}}"/>
									% end
                                    % else:
									<listOptionValue builtIn="false" value="{{include}}"/>
									% end
									% end
								</option>
								<option id="org.eclipse.cdt.build.core.settings.holder.symbols.2122043341" name="Symbols" superClass="org.eclipse.cdt.build.core.settings.holder.symbols" useByScannerDiscovery="false" valueType="definedSymbols">
									% for define in defines:
									<listOptionValue builtIn="false" value="{{define}}"/>
									% end
								</option>
								<inputType id="org.eclipse.cdt.build.core.settings.holder.inType.207004812" languageId="org.eclipse.cdt.core.gcc" languageName="GNU C" sourceContentType="org.eclipse.cdt.core.cSource,org.eclipse.cdt.core.cHeader" superClass="org.eclipse.cdt.build.core.settings.holder.inType"/>
							</tool>
						</toolChain>
					</folderInfo>
				</configuration>
			</storageModule>
			<storageModule moduleId="org.eclipse.cdt.core.externalSettings"/>
		</cconfiguration>
	</storageModule>
	<storageModule moduleId="cdtBuildSystem" version="4.0.0">
		<project id="{{project_name}}.null.189551033" name="{{project_name}}"/>
	</storageModule>
	<storageModule moduleId="scannerConfiguration">
		<autodiscovery enabled="true" problemReportingEnabled="true" selectedProfileId=""/>
		<scannerConfigBuildInfo instanceId="0.910961921">
			<autodiscovery enabled="true" problemReportingEnabled="true" selectedProfileId=""/>
		</scannerConfigBuildInfo>
	</storageModule>
	<storageModule moduleId="org.eclipse.cdt.core.LanguageSettingsProviders"/>
	<storageModule moduleId="refreshScope" versionNumber="2">
		<configuration configurationName="Default">
			<resource resourceType="PROJECT" workspacePath="/{{env_name}}"/>
		</configuration>
	</storageModule>
	<storageModule moduleId="org.eclipse.cdt.internal.ui.text.commentOwnerProjectMappings"/>
	<storageModule moduleId="org.eclipse.cdt.make.core.buildtargets">
		<buildTargets>
			<target name="PlatformIO: Upload using Programmer" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>run --target program</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: Upload SPIFFS image" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>run --target uploadfs</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: Build" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>run</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: Verbose Build" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>run --verbose</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: Upload" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>run --target upload</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: Verbose Upload" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>run --target upload --verbose</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: Clean" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>run --target clean</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: Test" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>test</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: Remote" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>remote run --target upload</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: Rebuild C/C++ Project Index" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>init --ide eclipse</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: List Devices" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>device list</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: Update Project Libraries" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>lib update</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: Update All" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>update</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
			<target name="PlatformIO: Upgrade Core" path="" targetID="org.eclipse.cdt.build.MakeTargetBuilder">
				<buildCommand>platformio</buildCommand>
				<buildArguments>-f -c eclipse</buildArguments>
				<buildTarget>upgrade</buildTarget>
				<stopOnError>true</stopOnError>
				<useDefaultCommand>false</useDefaultCommand>
				<runAllBuilders>false</runAllBuilders>
			</target>
		</buildTargets>
	</storageModule>
</cproject>
