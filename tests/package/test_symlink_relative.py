import os
from platformio.package.manager.library import LibraryPackageManager
from platformio.project.config import ProjectConfig

def test_install_symlink_relative_parent(tmp_path):
    # project-like layout
    project_dir = tmp_path / "proj"
    lib_root = tmp_path / "common_libs" / "DemoLibSymlink"
    (lib_root / "src").mkdir(parents=True)
    (lib_root / "library.json").write_text('{"name":"DemoLibSymlink","version":"1.0.0"}')

    # .pio/libdeps/<env> storage
    storage_dir = project_dir / ".pio" / "libdeps" / "env"
    storage_dir.mkdir(parents=True)

    # reset singleton + set project_dir
    ProjectConfig._instances = {}
    cfg = ProjectConfig.get_instance()
    cfg.enable_warnings = False
    if not cfg.has_section("platformio"):
        cfg.add_section("platformio")
    cfg.set("platformio", "project_dir", str(project_dir))

    # act: install via relative symlink
    lm = LibraryPackageManager(str(storage_dir))
    spec = "DemoLibSymlink=symlink://../common_libs/DemoLibSymlink"
    pkg = lm.install_from_uri(spec.split("=", 1)[1], spec)

    # assert: resolved to absolute real path of the lib folder
    assert os.path.realpath(pkg.path) == os.path.realpath(str(lib_root))
