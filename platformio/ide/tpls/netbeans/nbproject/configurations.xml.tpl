<?xml version="1.0" encoding="UTF-8"?>
<configurationDescriptor version="97">
  <logicalFolder name="root" displayName="root" projectFiles="true" kind="ROOT">
    <df root="." name="0">
      <in>platformio.ini</in>
    </df>
    <logicalFolder name="ExternalFiles"
                   displayName="Important Files"
                   projectFiles="false"
                   kind="IMPORTANT_FILES_FOLDER">
      <itemPath>nbproject/private/launcher.properties</itemPath>
    </logicalFolder>
  </logicalFolder>
  <sourceFolderFilter>^(nbproject|.pio)$</sourceFolderFilter>
  <sourceRootList>
    <Elem>.</Elem>
  </sourceRootList>
  <projectmakefile></projectmakefile>
  <confs>
    <conf name="Default" type="0">
      <toolsSet>
        <compilerSet>default</compilerSet>
        <dependencyChecking>false</dependencyChecking>
        <rebuildPropChanged>false</rebuildPropChanged>
      </toolsSet>
      <codeAssistance>
        <buildAnalyzer>true</buildAnalyzer>
        <includeAdditional>true</includeAdditional>
      </codeAssistance>
      <makefileType>
        <makeTool>
          <buildCommandWorkingDir>.</buildCommandWorkingDir>
          <buildCommand>{{platformio_path}} -f -c netbeans run</buildCommand>
          <cleanCommand>{{platformio_path}} -f -c netbeans run --target clean</cleanCommand>
          <executablePath></executablePath>
          <cTool>
            <incDir>
              <pElem>src</pElem>
              % for include in includes:
              <pElem>{{include}}</pElem>
              % end
            </incDir>
            <preprocessorList>
              % for define in defines:
                <Elem>{{define}}</Elem>
              % end
            </preprocessorList>
          </cTool>
          <ccTool>
            <incDir>
              <pElem>src</pElem>
              % for include in includes:
              <pElem>{{include}}</pElem>
              % end
            </incDir>
            <preprocessorList>
              % for define in defines:
                <Elem>{{define}}</Elem>
              % end
            </preprocessorList>
          </ccTool>
        </makeTool>
        <preBuild>
          <preBuildCommandWorkingDir>.</preBuildCommandWorkingDir>
          <preBuildCommand></preBuildCommand>
        </preBuild>
      </makefileType>
      <item path="platformio.ini" ex="false" tool="3" flavor2="0">
      </item>
    </conf>
  </confs>
</configurationDescriptor>
