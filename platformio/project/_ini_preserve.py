from __future__ import annotations
from pathlib import Path
from typing import Dict, Tuple

def _normalize_changes(changes: Dict[Tuple[str, str], str]):
    # accept {("section","key"): "value"} or {"section.key": "value"}
    norm = {}
    for k, v in changes.items():
        if isinstance(k, tuple) and len(k) == 2:
            sec, key = k
        else:
            parts = str(k).split(".", 1)
            if len(parts) != 2:
                raise ValueError(f"invalid change key: {k!r}")
            sec, key = parts
        norm[(str(sec), str(key))] = v
    return norm

def save_ini_preserving_comments(path: str | Path, changes: Dict, encoding: str = "utf-8") -> bool:
    """
    Try to apply key/value 'changes' to INI at 'path' while preserving comments
    and formatting. Returns True on success. If anything goes wrong, returns
    False so callers can fall back to the legacy writer.
    """
    path = Path(path)
    changes = _normalize_changes(changes)

    # Attempt preferred path: ConfigUpdater (preserves comments/ordering)
    try:
        from configupdater import ConfigUpdater  # type: ignore
        upd = ConfigUpdater()
        upd.read(path, encoding=encoding)

        for (sec, key), value in changes.items():
            if not upd.has_section(sec):
                upd.add_section(sec)
            # Only touch the exact key; do not rewrite entire section.
            if key in upd[sec]:
                if upd[sec][key].value != str(value):
                    upd[sec][key].value = str(value)
            else:
                # Insert at the end of the section so we don't disturb existing lines.
                upd[sec].add_after(upd[sec][-1].key if len(upd[sec]) else None, key, str(value))

        with path.open("w", encoding=encoding, newline="\n") as f:
            upd.write(f)
        return True
    except Exception:
        # Any error here should fall through to legacy path
        pass

    # Fallback: standard configparser (will lose comments)
    try:
        import configparser
        parser = configparser.ConfigParser(interpolation=None)
        # Read existing values but comments will be lost on write
        with path.open("r", encoding=encoding, newline="") as f:
            parser.read_file(f)
        for (sec, key), value in changes.items():
            if not parser.has_section(sec) and sec.lower() != "default":
                parser.add_section(sec)
            if sec.lower() == "default":
                parser.set("DEFAULT", key, str(value))
            else:
                parser.set(sec, key, str(value))
        with path.open("w", encoding=encoding, newline="\n") as f:
            parser.write(f)
        return True
    except Exception:
        return False
