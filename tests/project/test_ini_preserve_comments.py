from pathlib import Path
from platformio.project._ini_preserve import save_ini_preserving_comments

SAMPLE = """\
; header comment
# second comment
[platformio]
description = Demo ; keep inline

[env:demo]
platform = espressif32
framework = arduino  ; inline stays
lib_deps =
    ; a list kept as comments
    ; me-no-dev/AsyncTCP @ ^1.1.1
; tail comment
"""

def test_preserve_comments(tmp_path: Path):
    ini = tmp_path / "platformio.ini"
    ini.write_text(SAMPLE, encoding="utf-8", newline="\n")

    ok = save_ini_preserving_comments(
        ini,
        {("env:demo", "platform"): "espressif32@6.7.0"}
    )
    assert ok, "helper should succeed"

    out = ini.read_text(encoding="utf-8")
    assert "platform = espressif32@6.7.0" in out
    assert "; header comment" in out
    assert "# second comment" in out
    assert "description = Demo ; keep inline" in out
    assert "framework = arduino  ; inline stays" in out
    assert "; me-no-dev/AsyncTCP @ ^1.1.1" in out
    assert "; tail comment" in out
