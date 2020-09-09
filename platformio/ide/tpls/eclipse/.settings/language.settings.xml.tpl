% import re
% STD_RE = re.compile(r"(\-std=[a-z\+]+\w+)")
% cxx_stds = STD_RE.findall(cxx_flags)
% cxx_std = cxx_stds[-1] if cxx_stds else ""
%
% if cxx_path.startswith(user_home_dir):
% if "windows" in systype:
%    cxx_path = "${USERPROFILE}" + cxx_path.replace(user_home_dir, "")
% else:
%    cxx_path = "${HOME}" + cxx_path.replace(user_home_dir, "")
% end
% end
%
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<project>
	<configuration id="0.910961921" name="Default">
		<extension point="org.eclipse.cdt.core.LanguageSettingsProvider">
			<provider copy-of="extension" id="org.eclipse.cdt.ui.UserLanguageSettingsProvider"/>
			<provider-reference id="org.eclipse.cdt.core.ReferencedProjectsLanguageSettingsProvider" ref="shared-provider"/>
			<provider-reference id="org.eclipse.cdt.managedbuilder.core.MBSLanguageSettingsProvider" ref="shared-provider"/>
			<provider class="org.eclipse.cdt.internal.build.crossgcc.CrossGCCBuiltinSpecsDetector" console="false" env-hash="1291887707783033084" id="org.eclipse.cdt.build.crossgcc.CrossGCCBuiltinSpecsDetector" keep-relative-paths="false" name="CDT Cross GCC Built-in Compiler Settings" parameter="{{ cxx_path }} ${FLAGS} {{ cxx_std }} -E -P -v -dD &quot;${INPUTS}&quot;" prefer-non-shared="true">
				<language-scope id="org.eclipse.cdt.core.gcc"/>
				<language-scope id="org.eclipse.cdt.core.g++"/>
			</provider>
		</extension>
	</configuration>
	<configuration id="0.910961921.1363900502" name="Debug">
		<extension point="org.eclipse.cdt.core.LanguageSettingsProvider">
			<provider copy-of="extension" id="org.eclipse.cdt.ui.UserLanguageSettingsProvider"/>
			<provider-reference id="org.eclipse.cdt.core.ReferencedProjectsLanguageSettingsProvider" ref="shared-provider"/>
			<provider-reference id="org.eclipse.cdt.managedbuilder.core.MBSLanguageSettingsProvider" ref="shared-provider"/>
			<provider class="org.eclipse.cdt.internal.build.crossgcc.CrossGCCBuiltinSpecsDetector" console="false" env-hash="1291887707783033084" id="org.eclipse.cdt.build.crossgcc.CrossGCCBuiltinSpecsDetector" keep-relative-paths="false" name="CDT Cross GCC Built-in Compiler Settings" parameter="{{ cxx_path }} ${FLAGS} {{ cxx_std }} -E -P -v -dD &quot;${INPUTS}&quot;" prefer-non-shared="true">
				<language-scope id="org.eclipse.cdt.core.gcc"/>
				<language-scope id="org.eclipse.cdt.core.g++"/>
			</provider>
		</extension>
	</configuration>
</project>
