#!/usr/bin/env python3
"""Bundle this project's sources and artifacts; never include Git or tool caches."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    paths=[]
    for name in ('composition','docs','engine','tests','tools','reports','deliverables'):
        paths.extend(p for p in (ROOT/name).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.zip'))
    paths.extend(ROOT/name for name in ('README.md','.gitignore','requirements-dev.txt'))
    archive=ROOT/'deliverables/nes_master_composer.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(paths): z.write(p,'nes_master_composer/'+str(p.relative_to(ROOT)))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(paths)
        # Verify every embedded byte against the delivered filesystem artifact.
        for p in paths:
            assert hashlib.sha256(z.read('nes_master_composer/'+str(p.relative_to(ROOT)))).digest()==hashlib.sha256(p.read_bytes()).digest()
    print(f'Bundle verified: {archive.relative_to(ROOT)}, {len(paths)} files, {archive.stat().st_size} bytes')

if __name__=='__main__': main()
