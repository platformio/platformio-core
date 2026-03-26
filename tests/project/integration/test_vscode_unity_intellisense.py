import json
import subprocess
import sys
from pathlib import Path


def _run_platformio(project_dir, *args):
    result = subprocess.run(
        [sys.executable, "-m", "platformio", *args, "-d", str(project_dir)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _create_project(project_dir, envs):
    ini_lines = []
    for env in envs:
        ini_lines.extend(
            [
                f"[env:{env}]",
                "platform = native",
                "",
            ]
        )
    (project_dir / "platformio.ini").write_text("\n".join(ini_lines), encoding="utf8")

    src_dir = project_dir / "src"
    src_dir.mkdir(parents=True)
    (src_dir / "main.cpp").write_text("int main() { return 0; }\n", encoding="utf8")

    test_dir = project_dir / "test" / "test_dummy"
    test_dir.mkdir(parents=True)
    (test_dir / "test_main.cpp").write_text(
        """
#include <unity.h>

void test_dummy(void) { TEST_ASSERT_TRUE(1); }

int main(int argc, char **argv)
{
    UNITY_BEGIN();
    RUN_TEST(test_dummy);
    return UNITY_END();
}
""".strip()
        + "\n",
        encoding="utf8",
    )


def _assert_unity_intellisense(config):
    defines = config.get("defines", [])
    assert any(item.startswith("UNITY_INCLUDE_CONFIG_H") for item in defines)

    include_paths = [item.replace("\\", "/") for item in config.get("includePath", [])]
    assert any("${workspaceFolder}/test" in item or item.endswith("/test") for item in include_paths)
    assert any("${workspaceFolder}/test/**" in item or item.endswith("/test/**") for item in include_paths)


def test_vscode_unity_intellisense_when_workspace_has_tests(tmp_path):
    project_dir = Path(tmp_path)
    _create_project(project_dir, ("native_1", "native_2"))

    _run_platformio(project_dir, "project", "init", "--ide", "vscode")

    properties_file = project_dir / ".vscode" / "c_cpp_properties.json"
    assert properties_file.is_file()

    data = json.loads(properties_file.read_text(encoding="utf8"))
    configurations = data.get("configurations", [])
    assert configurations

    for config in configurations:
        _assert_unity_intellisense(config)
