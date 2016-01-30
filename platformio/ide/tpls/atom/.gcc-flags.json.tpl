{
  "execPath": "{{ cxx_path.replace("\\", "/") }}",
  "gccDefaultCFlags": "-fsyntax-only {{ cc_flags.replace(' -MMD ', ' ') }}",
  "gccDefaultCppFlags": "-fsyntax-only {{ cxx_flags.replace(' -MMD ', ' ')  }}",
  "gccErrorLimit": 15,
  "gccIncludePaths": "{{ ','.join(includes).replace("\\", "/") }}",
  "gccSuppressWarnings": false
}
