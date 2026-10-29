#!/usr/bin/env python3
"""Install or verify this reviewed Humanizer revision without agent-specific tools."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parent.parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def package_files():
    if (ROOT / '.git').exists():
        names = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-z'], text=True).split('\0')
        files = [ROOT / name for name in names if name]
    else:
        files = [p for p in ROOT.rglob('*') if p.is_file() and not {'.git', '.codex', '__pycache__'}.intersection(p.relative_to(ROOT).parts) and p.name != '.humanizer-install.json']
    for path in files:
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise SystemExit('Package files must stay inside the source directory.')
    return {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in sorted(files)}

def verify(destination, files, revision):
    marker = destination / '.humanizer-install.json'
    if not marker.exists():
        return False
    state = json.loads(marker.read_text(encoding='utf-8'))
    return state.get('commit') == revision and state.get('files') == files and all((destination / name).is_file() and sha(destination / name) == value for name, value in files.items())

def install(destination, files, revision, expected):
    if destination.name != 'humanizer' or destination.is_symlink():
        raise SystemExit('Use an explicit, non-symlink directory named humanizer.')
    if verify(destination, files, revision):
        return {'destination': str(destination), 'commit': revision, 'status': 'verified, unchanged'}
    if destination.exists():
        existing = destination / 'SKILL.md'
        if not existing.is_file() or 'name: humanizer' not in existing.read_text(encoding='utf-8'):
            raise SystemExit('Existing destination is not a Humanizer skill.')
        if expected and sha(existing) != expected:
            raise SystemExit('Installed skill changed after inspection; review before replacing it.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.humanizer-stage-', dir=destination.parent))
    backup_root = destination.parent.parent / '.humanizer-backups'
    backup_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    backup = backup_root / stamp if destination.exists() else None
    owner = destination.stat() if destination.exists() else destination.parent.stat()
    for name in files:
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
    (stage / '.humanizer-install.json').write_text(json.dumps({'repository': 'sam2kb/humanizer', 'commit': revision, 'files': files}, indent=2) + '\n', encoding='utf-8')
    subprocess.run([sys.executable, str(stage / 'scripts/validate-package.py')], check=True)
    if hasattr(os, 'geteuid') and os.geteuid() == 0:
        for path in [stage, *stage.rglob('*')]:
            os.chown(path, owner.st_uid, owner.st_gid)
    stage.chmod(0o755)
    if backup:
        os.replace(destination, backup)
    try:
        os.replace(stage, destination)
        if not verify(destination, files, revision):
            raise RuntimeError('Post-install hash verification failed.')
    except Exception:
        if destination.exists():
            os.replace(destination, backup_root / ('failed-' + stamp))
        if backup:
            os.replace(backup, destination)
        raise
    return {'destination': str(destination), 'commit': revision, 'status': 'installed and verified', 'backup': str(backup) if backup else None}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', required=True, action='append', type=Path)
    parser.add_argument('--revision', required=True, help='Reviewed full Git commit SHA')
    parser.add_argument('--expected-skill-sha256', help='Fail if an existing skill differs from the inspected hash')
    parser.add_argument('--check', action='store_true', help='Verify without changing installed files')
    args = parser.parse_args()
    if not re.fullmatch('[0-9a-f]{40}', args.revision):
        parser.error('--revision must be a full commit SHA')
    if (ROOT / '.git').exists():
        actual = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != args.revision:
            parser.error('Requested revision does not match the source checkout')
        dirty = subprocess.check_output(['git', '-C', str(ROOT), 'diff', '--name-only', 'HEAD'], text=True)
        if dirty.strip():
            parser.error('Commit source changes before installing a revision')
    files = package_files()
    for path in args.dest:
        destination = path.expanduser().absolute()
        if args.check:
            valid = verify(destination, files, args.revision)
            print(json.dumps({'destination': str(destination), 'commit': args.revision, 'verified': valid}))
            if not valid:
                return 1
        else:
            print(json.dumps(install(destination, files, args.revision, args.expected_skill_sha256)))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
