% _defines = " ".join(["-D%s" % d for d in defines])
{
  "execPath": "{{ cxx_path.replace("\\", "/") }}",
  "gccDefaultCFlags": "-fsyntax-only {{! cc_flags.replace(' -MMD ', ' ').replace('"', '\\"') }} {{ !_defines.replace('"', '\\"') }}",
  "gccDefaultCppFlags": "-fsyntax-only {{! cxx_flags.replace(' -MMD ', ' ').replace('"', '\\"') }} {{ !_defines.replace('"', '\\"') }}",
  "gccErrorLimit": 15,
  "gccIncludePaths": "{{ ','.join(includes).replace("\\", "/") }}",
  "gccSuppressWarnings": false
}
