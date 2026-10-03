"""Shared content digests for screenshot provenance."""
import hashlib
from pathlib import Path

def source_digest(root, name):
    plugin=Path(root)/'mods'/name
    paths=sorted([*plugin.glob('hooks/*.js'),*plugin.glob('tests/*.ts'),plugin/'.claude-plugin/plugin.json'])
    value=hashlib.sha256()
    for path in paths:
        value.update(str(path.relative_to(plugin)).encode())
        value.update(b'\0')
        value.update(path.read_bytes())
        value.update(b'\0')
    return value.hexdigest()

def file_digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
