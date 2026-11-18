"""Shared paths: tools live in the repository, translation data stays private under local/.

SAKURA_OWNER_ROOT points at the checkout that holds local/ (same convention as the runtime tests),
so the tools also work from a separate worktree.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWNER = Path(os.environ.get('SAKURA_OWNER_ROOT', ROOT))
WORK = OWNER / 'local' / 'work' / 'guion-es'   # private: script, batches, builds (never committed)
MENUS = WORK / 'menus'
