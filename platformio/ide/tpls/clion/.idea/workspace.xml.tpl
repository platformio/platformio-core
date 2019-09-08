<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="CMakeRunConfigurationManager" shouldGenerate="true" assignedExecutableTargets="true" buildAllGenerated="true">
    <generated>
      <config projectName="{{project_name}}" targetName="PLATFORMIO" />
      <config projectName="{{project_name}}" targetName="{{project_name}}" />
      <config projectName="{{project_name}}" targetName="PLATFORMIO_BUILD" />
      <config projectName="{{project_name}}" targetName="PLATFORMIO_UPLOAD" />
      <config projectName="{{project_name}}" targetName="PLATFORMIO_CLEAN" />
      <config projectName="{{project_name}}" targetName="PLATFORMIO_TEST" />
      <config projectName="{{project_name}}" targetName="PLATFORMIO_PROGRAM" />
      <config projectName="{{project_name}}" targetName="PLATFORMIO_UPLOADFS" />
      <config projectName="{{project_name}}" targetName="PLATFORMIO_UPDATE_ALL" />
      <config projectName="{{project_name}}" targetName="PLATFORMIO_REBUILD_PROJECT_INDEX" />
      <config projectName="{{project_name}}" targetName="DEBUG" />
    </generated>
  </component>
  <component name="CMakeSettings" AUTO_RELOAD="true">
   <configurations>
%   envs = config.envs()
%   if len(envs) > 1:
%       for env in envs:
      <configuration PROFILE_NAME="{{ env }}" CONFIG_NAME="{{ env }}" />
%       end
      <configuration PROFILE_NAME="All" CONFIG_NAME="All" />
%   else:
      <configuration PROFILE_NAME="{{ env_name }}" CONFIG_NAME="{{ env_name }}" />
%   end
    </configurations>
  </component>
  <component name="ChangeListManager">
    <list default="true" id="ec922180-b3d3-40f1-af0b-2568113a9075" name="Default" comment="" />
    <ignored path="platformio.iws" />
    <ignored path=".idea/workspace.xml" />
    <option name="EXCLUDED_CONVERTED_TO_IGNORED" value="true" />
    <option name="TRACKING_ENABLED" value="true" />
    <option name="SHOW_DIALOG" value="false" />
    <option name="HIGHLIGHT_CONFLICTS" value="true" />
    <option name="HIGHLIGHT_NON_ACTIVE_CHANGELIST" value="false" />
    <option name="LAST_RESOLUTION" value="IGNORE" />
  </component>
  <component name="ChangesViewManager" flattened_view="true" show_ignored="false" />
  <component name="CreatePatchCommitExecutor">
    <option name="PATCH_PATH" value="" />
  </component>
  <component name="ExecutionTargetManager" SELECTED_TARGET="default_target" />
  <component name="FavoritesManager">
    <favorites_list name="{{project_name}}" />
  </component>
  <component name="FileEditorManager">
    <leaf>
      <file leaf-file-name="platformio.ini" pinned="false" current-in-tab="true">
        <entry file="file://$PROJECT_DIR$/platformio.ini"></entry>
      </file>
      % for file in src_files:
      <file leaf-file-name="file://$PROJECT_DIR$/{{file}}" pinned="false" current-in-tab="false">
        <entry file="file://$PROJECT_DIR/${{file}}"></entry>
      </file>
      % end
    </leaf>
  </component>
  <component name="JsBuildToolGruntFileManager" detection-done="true" />
  <component name="JsGulpfileManager">
    <detection-done>true</detection-done>
  </component>
  <component name="NamedScopeManager">
    <order />
  </component>
  <component name="ProjectFrameBounds">
    <option name="x" value="252" />
    <option name="y" value="21" />
    <option name="width" value="1400" />
    <option name="height" value="1000" />
  </component>
  <component name="ProjectInspectionProfilesVisibleTreeState">
    <entry key="Project Default">
      <profile-state>
        <expanded-state>
          <State>
            <id />
          </State>
        </expanded-state>
        <selected-state>
          <State>
            <id>C/C++</id>
          </State>
        </selected-state>
      </profile-state>
    </entry>
  </component>
  <component name="ProjectLevelVcsManager" settingsEditedManually="false">
    <OptionsSetting value="true" id="Add" />
    <OptionsSetting value="true" id="Remove" />
    <OptionsSetting value="true" id="Checkout" />
    <OptionsSetting value="true" id="Update" />
    <OptionsSetting value="true" id="Status" />
    <OptionsSetting value="true" id="Edit" />
    <ConfirmationsSetting value="0" id="Add" />
    <ConfirmationsSetting value="0" id="Remove" />
  </component>
  <component name="ProjectView">
    <navigator currentView="ProjectPane" proportions="" version="1">
      <flattenPackages />
      <showMembers />
      <showModules />
      <showLibraryContents />
      <hideEmptyPackages />
      <abbreviatePackageNames />
      <autoscrollToSource />
      <autoscrollFromSource />
      <sortByType />
      <manualOrder />
      <foldersAlwaysOnTop value="true" />
    </navigator>
    <panes>
      <pane id="ProjectPane">
        <subPane>
          <PATH>
            <PATH_ELEMENT>
              <option name="myItemId" value="{{project_name}}" />
              <option name="myItemType" value="com.jetbrains.cidr.projectView.CidrFilesViewHelper$MyProjectTreeStructure$1" />
            </PATH_ELEMENT>
          </PATH>
          <PATH>
            <PATH_ELEMENT>
              <option name="myItemId" value="{{project_name}}" />
              <option name="myItemType" value="com.jetbrains.cidr.projectView.CidrFilesViewHelper$MyProjectTreeStructure$1" />
            </PATH_ELEMENT>
            <PATH_ELEMENT>
              <option name="myItemId" value="{{project_name}}" />
              <option name="myItemType" value="com.intellij.ide.projectView.impl.nodes.PsiDirectoryNode" />
            </PATH_ELEMENT>
          </PATH>
          <PATH>
            <PATH_ELEMENT>
              <option name="myItemId" value="{{project_name}}" />
              <option name="myItemType" value="com.jetbrains.cidr.projectView.CidrFilesViewHelper$MyProjectTreeStructure$1" />
            </PATH_ELEMENT>
            <PATH_ELEMENT>
              <option name="myItemId" value="{{project_name}}" />
              <option name="myItemType" value="com.intellij.ide.projectView.impl.nodes.PsiDirectoryNode" />
            </PATH_ELEMENT>
            <PATH_ELEMENT>
              <option name="myItemId" value="src" />
              <option name="myItemType" value="com.intellij.ide.projectView.impl.nodes.PsiDirectoryNode" />
            </PATH_ELEMENT>
          </PATH>
        </subPane>
      </pane>
    </panes>
  </component>
  <component name="PropertiesComponent">
    <property name="recentsLimit" value="5" />
    <property name="settings.editor.selected.configurable" value="CPPToolchains" />
    <property name="settings.editor.splitter.proportion" value="0.2" />
    <property name="last_opened_file_path" value="$PROJECT_DIR$/platformio.ini" />
    <property name="restartRequiresConfirmation" value="true" />
    <property name="FullScreen" value="false" />
  </component>
  <component name="RunManager" selected="Application.PLATFORMIO_BUILD">
    <configuration default="true" type="CMakeRunConfiguration" factoryName="Application" PASS_PARENT_ENVS="FALSE" PROJECT_NAME="{{project_name}}" TARGET_NAME="{{project_name}}" CONFIG_NAME="Debug">
      <envs />
      <method />
    </configuration>
    <configuration default="true" type="js.build_tools.gulp" factoryName="Gulp.js">
      <node-options />
      <gulpfile />
      <tasks />
      <arguments />
      <pass-parent-envs>true</pass-parent-envs>
      <envs />
      <method />
    </configuration>
    <configuration default="false" name="PLATFORMIO_BUILD" type="CMakeRunConfiguration" factoryName="Application" WORKING_DIR="" PASS_PARENT_ENVS="FALSE" PROJECT_NAME="{{project_name}}" TARGET_NAME="PLATFORMIO_BUILD" CONFIG_NAME="Debug">
      <envs />
      <method />
    </configuration>
    <configuration default="false" name="PLATFORMIO_CLEAN" type="CMakeRunConfiguration" factoryName="Application" WORKING_DIR="" PASS_PARENT_ENVS="FALSE" PROJECT_NAME="{{project_name}}" TARGET_NAME="PLATFORMIO_CLEAN" CONFIG_NAME="Debug">
      <envs />
      <method />
    </configuration>
    <configuration default="false" name="PLATFORMIO_TEST" type="CMakeRunConfiguration" factoryName="Application" WORKING_DIR="" PASS_PARENT_ENVS="FALSE" PROJECT_NAME="{{project_name}}" TARGET_NAME="PLATFORMIO_TEST" CONFIG_NAME="Debug">
      <envs />
      <method />
    </configuration>
    <configuration default="false" name="PLATFORMIO_UPLOAD" type="CMakeRunConfiguration" factoryName="Application" WORKING_DIR="" PASS_PARENT_ENVS="FALSE" PROJECT_NAME="{{project_name}}" TARGET_NAME="PLATFORMIO_UPLOAD" CONFIG_NAME="Debug">
      <envs />
      <method />
    </configuration>
    <configuration default="false" name="PLATFORMIO_UPLOADFS" type="CMakeRunConfiguration" factoryName="Application" WORKING_DIR="" PASS_PARENT_ENVS="FALSE" PROJECT_NAME="{{project_name}}" TARGET_NAME="PLATFORMIO_UPLOADFS" CONFIG_NAME="Debug">
      <envs />
      <method />
    </configuration>
    <configuration default="false" name="PLATFORMIO_PROGRAM" type="CMakeRunConfiguration" factoryName="Application" WORKING_DIR="" PASS_PARENT_ENVS="FALSE" PROJECT_NAME="{{project_name}}" TARGET_NAME="PLATFORMIO_PROGRAM" CONFIG_NAME="Debug">
      <envs />
      <method />
    </configuration>
    <configuration default="false" name="PLATFORMIO_UPDATE" type="CMakeRunConfiguration" factoryName="Application" WORKING_DIR="" PASS_PARENT_ENVS="FALSE" PROJECT_NAME="{{project_name}}" TARGET_NAME="PLATFORMIO_UPDATE_ALL" CONFIG_NAME="Debug">
      <envs />
      <method />
    </configuration>
    <configuration default="false" name="PLATFORMIO_REBUILD_PROJECT_INDEX" type="CMakeRunConfiguration" factoryName="Application" WORKING_DIR="" PASS_PARENT_ENVS="FALSE" PROJECT_NAME="{{project_name}}" TARGET_NAME="PLATFORMIO_REBUILD_PROJECT_INDEX" CONFIG_NAME="Debug">
      <envs />
      <method />
    </configuration>
  </component>
  <component name="ShelveChangesManager" show_recycled="false" />
  <component name="SvnConfiguration">
    <configuration />
  </component>
  <component name="TaskManager">
    <task active="true" id="Default" summary="Default task">
      <changelist id="ec922180-b3d3-40f1-af0b-2568113a9075" name="Default" comment="" />
      <created>1435919971910</created>
      <option name="number" value="Default" />
      <updated>1435919971910</updated>
    </task>
    <servers />
  </component>
  <component name="ToolWindowManager">
    <frame x="181" y="23" width="1400" height="1000" extended-state="0" />
    <editor active="true" />
    <layout>
      <window_info id="Project" active="false" anchor="left" auto_hide="false" internal_type="DOCKED" type="DOCKED" visible="true" show_stripe_button="true" weight="0.24945612" sideWeight="0.5" order="0" side_tool="false" content_ui="tabs" />
    </layout>
  </component>
  <component name="Vcs.Log.UiProperties">
    <option name="RECENTLY_FILTERED_USER_GROUPS">
      <collection />
    </option>
    <option name="RECENTLY_FILTERED_BRANCH_GROUPS">
      <collection />
    </option>
  </component>
  <component name="VcsContentAnnotationSettings">
    <option name="myLimit" value="2678400000" />
  </component>
  <component name="XDebuggerManager">
    <breakpoint-manager>
      <option name="time" value="4" />
    </breakpoint-manager>
    <watches-manager />
  </component>
  <component name="masterDetails">
    <states>
      <state key="ScopeChooserConfigurable.UI">
        <settings>
          <splitter-proportions>
            <option name="proportions">
              <list>
                <option value="0.2" />
              </list>
            </option>
          </splitter-proportions>
        </settings>
      </state>
    </states>
  </component>
</project>
