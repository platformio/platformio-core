<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    <Filter Include="Source Files">
      <UniqueIdentifier>{4FC737F1-C7A5-4376-A066-2A32D752A2FF}</UniqueIdentifier>
      <Extensions>cpp;c;cc;cxx;def;odl;idl;hpj;bat;asm;asmx;ino;pde</Extensions>
    </Filter>
    <Filter Include="Header Files">
      <UniqueIdentifier>{93995380-89BD-4b04-88EB-625FBE52EBFB}</UniqueIdentifier>
      <Extensions>h;hh;hpp;hxx;hm;inl;inc;xsd</Extensions>
    </Filter>
  </ItemGroup>
  <ItemGroup>
    <None Include="platformio.ini" />
  </ItemGroup>
  % for file in src_files:
  <ItemGroup>
    % if any(file.endswith(".%s" % e) for e in ("h", "hh", "hpp", "inc")):
    <ClInclude Include="{{file}}">
      <Filter>Header Files</Filter>
    </ClInclude>
    % else:
    <ClCompile Include="{{file}}">
      <Filter>Source Files</Filter>
    </ClCompile>
    %end
  </ItemGroup>
  % end
</Project>
