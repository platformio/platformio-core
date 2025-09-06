from pathlib import Path
import sys
from platformio.project._ini_preserve import save_ini_preserving_comments

def main():
    if len(sys.argv) < 4 or len(sys.argv) % 2 != 0:
        print("Usage: python scripts/ini_preserve_demo.py <ini_path> <section.key> <value> [<section.key> <value> ...]")
        sys.exit(2)

    ini = Path(sys.argv[1])
    pairs = sys.argv[2:]
    changes = {}
    for i in range(0, len(pairs), 2):
        k = pairs[i]
        v = pairs[i+1]
        changes[k] = v

    ok = save_ini_preserving_comments(ini, changes)
    print("OK" if ok else "FAILED")

if __name__ == "__main__":
    main()
