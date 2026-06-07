"""Integrity gate: verify every input file in data/ against data/SHA256SUMS
before any analysis runs. Exits non-zero (and lists the offending files) if a
file is missing, altered, or unexpectedly added, so a changed input can never
silently propagate into the results. Pure standard library; no dependencies."""


import os, sys, hashlib
from _paths import DATA

SUMS = os.path.join(DATA, 'SHA256SUMS')
# Non-data helper files that live under data/ but are not pinned inputs.
IGNORE = {'SHA256SUMS', 'download_large_files.sh'}

def sha256(path, buf=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(buf), b''):
            h.update(chunk)
    return h.hexdigest()

def load_manifest():
    expected = {}
    with open(SUMS) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            digest, rel = line.split(None, 1)
            expected[rel.strip()] = digest
    return expected

def main():
    if not os.path.exists(SUMS):
        sys.exit(f'ERROR: checksum manifest not found: {SUMS}')
    expected = load_manifest()

    # Files actually present (excluding the manifest and helper scripts).
    present = set()
    for root, _, files in os.walk(DATA):
        for name in files:
            if name in IGNORE:
                continue
            present.add(os.path.relpath(os.path.join(root, name), DATA))

    missing   = sorted(set(expected) - present)
    untracked = sorted(present - set(expected))
    changed = []
    for rel in sorted(set(expected) & present):
        if sha256(os.path.join(DATA, rel)) != expected[rel]:
            changed.append(rel)

    if missing or untracked or changed:
        if missing:   print('MISSING (in manifest, not on disk):', *(['']+missing), sep='\n  ')
        if changed:   print('CHANGED (hash mismatch):',            *(['']+changed), sep='\n  ')
        if untracked: print('UNTRACKED (on disk, not in manifest):', *(['']+untracked), sep='\n  ')
        print(f'\nFAIL: data integrity check failed '
              f'({len(missing)} missing, {len(changed)} changed, {len(untracked)} untracked).')
        print('If a change is intentional, regenerate with: '
              'cd data && find . -type f ! -name SHA256SUMS | sort | sed "s|^./||" | xargs sha256sum > SHA256SUMS')
        sys.exit(1)

    print(f'OK: {len(expected)} data files match data/SHA256SUMS.')

if __name__ == '__main__':
    main()
