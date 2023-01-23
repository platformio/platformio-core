<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="12.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup>
    <Path>{{env_path}}</Path>
  </PropertyGroup>
  <ItemGroup Label="ProjectConfigurations">
    <ProjectConfiguration Include="Debug|Win32">
      <Configuration>Debug</Configuration>
      <Platform>Win32</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|Win32">
      <Configuration>Release</Configuration>
      <Platform>Win32</Platform>
    </ProjectConfiguration>
  </ItemGroup>
  <PropertyGroup Label="Globals">
    <ProjectGuid>{0FA9C3A8-452B-41EF-A418-9102B170F49F}</ProjectGuid>
    <Keyword>MakeFileProj</Keyword>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'" Label="Configuration">
    <ConfigurationType>Makefile</ConfigurationType>
    <UseDebugLibraries>true</UseDebugLibraries>
    <PlatformToolset>v120</PlatformToolset>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="Configuration">
    <ConfigurationType>Makefile</ConfigurationType>
    <UseDebugLibraries>false</UseDebugLibraries>
    <PlatformToolset>v120</PlatformToolset>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />
  <ImportGroup Label="ExtensionSettings">
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <ImportGroup Label="PropertySheets" Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
  </ImportGroup>
  <PropertyGroup Label="UserMacros" />
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
    <NMakeBuildCommandLine>platformio -f -c visualstudio run</NMakeBuildCommandLine>
    <NMakeCleanCommandLine>platformio -f -c visualstudio run --target clean</NMakeCleanCommandLine>
    <NMakePreprocessorDefinitions>{{!";".join(defines)}}</NMakePreprocessorDefinitions>
    % cleaned_includes = filter_includes(includes)
    <NMakeIncludeSearchPath>{{";".join(["$(HOMEDRIVE)$(HOMEPATH)%s" % i.replace(user_home_dir, "") if i.startswith(user_home_dir) else i for i in cleaned_includes])}}</NMakeIncludeSearchPath>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
    <NMakeBuildCommandLine>platformio run</NMakeBuildCommandLine>
    <NMakeCleanCommandLine>platformio run --target clean</NMakeCleanCommandLine>
    <NMakePreprocessorDefinitions>{{!";".join(defines)}}</NMakePreprocessorDefinitions>
    <NMakeIncludeSearchPath>{{";".join(["$(HOMEDRIVE)$(HOMEPATH)%s" % i.replace(user_home_dir, "") if i.startswith(user_home_dir) else i for i in cleaned_includes])}}</NMakeIncludeSearchPath>
  </PropertyGroup>
  <ItemDefinitionGroup>
  </ItemDefinitionGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
  <ImportGroup Label="ExtensionTargets">
  </ImportGroup>
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
