"""Shared paths: tools live in the repository, translation data stays private under local/.

SAKURA_OWNER_ROOT points at the checkout that holds local/ (same convention as the runtime tests),
so the tools also work from a separate worktree.
"""
import os
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWNER = Path(os.environ.get('SAKURA_OWNER_ROOT', ROOT))
WORK = OWNER / 'local' / 'work' / 'guion-es'   # private: script, batches, builds (never committed)
MENUS = WORK / 'menus'



def private_path(path: Path, owner: Path = OWNER) -> Path:
    resolved = path.resolve()
    local = owner.resolve() / 'local'
    if resolved == local or not resolved.is_relative_to(local):
        raise ValueError(f'la salida debe estar bajo {local}: {path}')
    return path.absolute()


def distinct_output(output: Path, *inputs: Path) -> None:
    if output.is_symlink():
        raise ValueError(f'la salida no puede ser un enlace simbólico: {output}')
    for source in inputs:
        if output.resolve() == source.resolve() or (
            output.exists() and source.exists() and output.samefile(source)
        ):
            raise ValueError(f'la salida coincide con una entrada: {output}')


@contextmanager
def atomic_output(destination: Path):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destination.parent, prefix=f'.{destination.name}.', delete=False) as stream:
        temporary = Path(stream.name)
    try:
        yield temporary
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def write_bytes(destination: Path, data: bytes) -> None:
    with atomic_output(destination) as output:
        output.write_bytes(data)
