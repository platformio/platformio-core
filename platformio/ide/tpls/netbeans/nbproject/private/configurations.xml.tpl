<?xml version="1.0" encoding="UTF-8"?>
<configurationDescriptor version="97">
  <logicalFolder name="root" displayName="root" projectFiles="true" kind="ROOT">
    <df root="." name="0">
      <df name="lib">
      </df>
      <df name="src">
      </df>
      <in>platformio.ini</in>
    </df>
  </logicalFolder>
  <projectmakefile></projectmakefile>
  <confs>
    <conf name="Default" type="0">
      <toolsSet>
        <developmentServer>localhost</developmentServer>
        <platform>{{4 if "darwin" in systype else 2 if "linux" in systype else 3}}</platform>
      </toolsSet>
      <compile>
        <compiledirpicklist>
          <compiledirpicklistitem>.</compiledirpicklistitem>
          <compiledirpicklistitem>${AUTO_FOLDER}</compiledirpicklistitem>
        </compiledirpicklist>
        <compiledir>${AUTO_FOLDER}</compiledir>
        <compilecommandpicklist>
          <compilecommandpicklistitem>${MAKE} ${ITEM_NAME}.o</compilecommandpicklistitem>
          <compilecommandpicklistitem>${AUTO_COMPILE}</compilecommandpicklistitem>
        </compilecommandpicklist>
        <compilecommand>${AUTO_COMPILE}</compilecommand>
      </compile>
      <dbx_gdbdebugger version="1">
        <gdb_pathmaps>
        </gdb_pathmaps>
        <gdb_interceptlist>
          <gdbinterceptoptions gdb_all="false" gdb_unhandled="true" gdb_unexpected="true"/>
        </gdb_interceptlist>
        <gdb_options>
          <DebugOptions>
          </DebugOptions>
        </gdb_options>
        <gdb_buildfirst gdb_buildfirst_overriden="false" gdb_buildfirst_old="false"/>
      </dbx_gdbdebugger>
      <nativedebugger version="1">
        <engine>gdb</engine>
      </nativedebugger>
      <runprofile version="9">
        <runcommandpicklist>
          <runcommandpicklistitem>"${OUTPUT_PATH}"</runcommandpicklistitem>
          <runcommandpicklistitem>{{platformio_path}} -f -c netbeans run --target upload</runcommandpicklistitem>
        </runcommandpicklist>
        <runcommand>{{platformio_path}} -f -c netbeans run --target upload</runcommand>
        <rundir>.</rundir>
        <buildfirst>false</buildfirst>
        <terminal-type>0</terminal-type>
        <remove-instrumentation>0</remove-instrumentation>
        <environment>
        </environment>
      </runprofile>
    </conf>
  </confs>
</configurationDescriptor>
