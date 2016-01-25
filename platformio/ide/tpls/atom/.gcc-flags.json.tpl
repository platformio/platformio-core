{
  "execPath": "{{ cxx_path.replace("\\", "/") }}",
  "gccDefaultCFlags": "-Wall -Wno-cpp -fsyntax-only -D{{ ' -D'.join(defines) }}",
  "gccDefaultCppFlags": "-Wall -Wno-cpp -fsyntax-only -D{{ ' -D'.join(defines) }}",
  "gccErrorLimit": 15,
  "gccIncludePaths": "{{ ','.join(includes).replace("\\", "/") }}",
  "gccSuppressWarnings": false
}
