% _defines = " ".join(["-D%s" % d for d in defines])
{
  "execPath": "{{ cxx_path }}",
  "gccDefaultCFlags": "-fsyntax-only {{! cc_flags.replace(' -MMD ', ' ').replace('"', '\\"') }} {{ !_defines.replace('"', '\\"') }}",
  "gccDefaultCppFlags": "-fsyntax-only {{! cxx_flags.replace(' -MMD ', ' ').replace('"', '\\"') }} {{ !_defines.replace('"', '\\"') }}",
  "gccErrorLimit": 15,
  "gccIncludePaths": "{{! ','.join("'{}'".format(inc) for inc in includes)}}",
  "gccSuppressWarnings": false
}
