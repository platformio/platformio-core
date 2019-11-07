% _defines = " ".join(["-D%s" % d.replace(" ", "\\\\ ") for d in defines])
{
  "execPath": "{{ cxx_path }}",
  "gccDefaultCFlags": "-fsyntax-only {{! cc_flags.replace(' -MMD ', ' ').replace('"', '\\"') }} {{ !_defines.replace('"', '\\"') }}",
  "gccDefaultCppFlags": "-fsyntax-only {{! cxx_flags.replace(' -MMD ', ' ').replace('"', '\\"') }} {{ !_defines.replace('"', '\\"') }}",
  "gccErrorLimit": 15,
  "gccIncludePaths": "{{ ','.join(includes) }}",
  "gccSuppressWarnings": false
}
