import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'archive'

EXCLUDES = {
    (ROOT / 'IMPLEMENTATION_PLAN.md').resolve(),
    (ROOT / 'frontend' / 'README.md').resolve(),
}
SKIP_DIR_NAMES = {'.git', '.github', '.vite', 'archive', 'node_modules', '.pytest_cache'}


def is_md(path: Path) -> bool:
    return path.suffix.lower() == '.md'


def restore_frontend_node_modules():
    src_nm = ARCHIVE / 'frontend' / 'node_modules'
    dst_nm = ROOT / 'frontend' / 'node_modules'
    if src_nm.exists():
        dst_nm.parent.mkdir(parents=True, exist_ok=True)
        # If destination exists, skip restore to avoid clobber
        if not dst_nm.exists():
            shutil.move(str(src_nm), str(dst_nm))
            print('Restored frontend/node_modules from archive.')


def main():
    ARCHIVE.mkdir(parents=True, exist_ok=True)

    # Restore any accidental moves of node_modules
    restore_frontend_node_modules()

    moved = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Prune directories in-place to avoid walking them
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]

        dirpath = Path(dirpath)
        # Skip processing inside archive
        if ARCHIVE in dirpath.parents or dirpath == ARCHIVE:
            continue

        for fname in filenames:
            src = dirpath / fname
            if not is_md(src):
                continue
            if src.resolve() in EXCLUDES:
                continue
            # Skip any md files under node_modules just in case
            if 'node_modules' in src.parts:
                continue
            rel = src.relative_to(ROOT)
            dest = ARCHIVE / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            moved.append((str(rel), str(dest.relative_to(ROOT))))

    print(f"Moved {len(moved)} markdown files to archive/")
    for rel, dest in moved:
        print(f" - {rel} -> {dest}")


if __name__ == '__main__':
    main()
