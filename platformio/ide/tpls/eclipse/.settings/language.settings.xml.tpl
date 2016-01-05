<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<project>
	<configuration id="0.910961921" name="Default">
		<extension point="org.eclipse.cdt.core.LanguageSettingsProvider">
			<provider copy-of="extension" id="org.eclipse.cdt.ui.UserLanguageSettingsProvider"/>
			<provider-reference id="org.eclipse.cdt.core.ReferencedProjectsLanguageSettingsProvider" ref="shared-provider"/>
			<provider-reference id="org.eclipse.cdt.managedbuilder.core.MBSLanguageSettingsProvider" ref="shared-provider"/>
			% if "windows" in systype:
			<provider class="org.eclipse.cdt.internal.build.crossgcc.CrossGCCBuiltinSpecsDetector" console="false" env-hash="1291887707783033084" id="org.eclipse.cdt.build.crossgcc.CrossGCCBuiltinSpecsDetector" keep-relative-paths="false" name="CDT Cross GCC Built-in Compiler Settings" parameter="${USERPROFILE}{{cxx_path.replace(user_home_dir, '')}} ${FLAGS} -E -P -v -dD &quot;${INPUTS}&quot;" prefer-non-shared="true">
			% else:
			<provider class="org.eclipse.cdt.internal.build.crossgcc.CrossGCCBuiltinSpecsDetector" console="false" env-hash="-869785120007741010" id="org.eclipse.cdt.build.crossgcc.CrossGCCBuiltinSpecsDetector" keep-relative-paths="false" name="CDT Cross GCC Built-in Compiler Settings" parameter="${HOME}{{cxx_path.replace(user_home_dir, '')}} ${FLAGS} -E -P -v -dD &quot;${INPUTS}&quot;" prefer-non-shared="true">
			% end
				<language-scope id="org.eclipse.cdt.core.gcc"/>
				<language-scope id="org.eclipse.cdt.core.g++"/>
			</provider>
		</extension>
	</configuration>
</project>
