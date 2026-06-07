#!/usr/bin/env bash

# Fetch the two ICIJ Offshore Leaks inputs that exceed GitHub's 100 MB per-file
# limit and are therefore excluded from the repository (see ../.gitignore):
#
#   offshore_leaks/relationships.csv   (~248 MB)
#   offshore_leaks/nodes-entities.csv  (~190 MB)
#
# Both are public and immutable (ICIJ snapshot generated 2025-03-31). This
# script obtains them, extracts just those two files, and verifies each against
# the SHA-256 digests pinned in data/SHA256SUMS, so a wrong or truncated
# download fails loudly instead of silently corrupting the results.
#
# Usage (run from anywhere):
#   # A) point at an already-downloaded ICIJ full-CSV zip:
#   ICIJ_ZIP=/path/to/icij-offshoreleaks.zip ./data/download_large_files.sh
#
#   # B) download from a URL (the ICIJ archive; get the link from
#   #    https://offshoreleaks.icij.org/pages/database):
#   ICIJ_URL='https://.../full-oldb.LATEST.zip' ./data/download_large_files.sh
#
# Re-running is safe: files already present and matching their hash are skipped.


set -euo pipefail

DATA="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUMS="$DATA/SHA256SUMS"
TARGETS=(offshore_leaks/relationships.csv offshore_leaks/nodes-entities.csv)

# --- sha256 helper (coreutils, busybox, or python fallback) ------------------
sha256() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  elif command -v shasum  >/dev/null 2>&1; then shasum -a 256 "$1" | cut -d' ' -f1
  else python3 -c "import hashlib,sys;h=hashlib.sha256();f=open(sys.argv[1],'rb')
while (b:=f.read(1<<20)): h.update(b)
print(h.hexdigest())" "$1"
  fi
}

expected_hash() { grep -E "  $1\$" "$SUMS" | cut -d' ' -f1; }

verify() {  # rel-path -> 0 if present and hash matches
  local rel="$1" want got
  [ -f "$DATA/$rel" ] || return 1
  want="$(expected_hash "$rel")"
  got="$(sha256 "$DATA/$rel")"
  [ "$got" = "$want" ]
}

# --- already done? -----------------------------------------------------------
need=()
for rel in "${TARGETS[@]}"; do
  if verify "$rel"; then echo "OK (already present): $rel"; else need+=("$rel"); fi
done
if [ ${#need[@]} -eq 0 ]; then
  echo "Both large inputs are present and verified. Nothing to do."
  exit 0
fi
echo "Need to fetch: ${need[*]}"

# --- obtain the ICIJ zip -----------------------------------------------------
ZIP="${ICIJ_ZIP:-}"
cleanup_zip=""
if [ -z "$ZIP" ]; then
  if [ -z "${ICIJ_URL:-}" ]; then
    cat >&2 <<'EOF'
ERROR: no source given.
  Set ICIJ_ZIP=/path/to/already-downloaded.zip, or
  set ICIJ_URL=<download link> (from https://offshoreleaks.icij.org/pages/database).
EOF
    exit 2
  fi
  ZIP="$(mktemp --suffix=.zip)"; cleanup_zip="$ZIP"
  echo "Downloading ICIJ archive from \$ICIJ_URL ..."
  if command -v curl >/dev/null 2>&1; then curl -fL --retry 3 -o "$ZIP" "$ICIJ_URL"
  elif command -v wget >/dev/null 2>&1; then wget -O "$ZIP" "$ICIJ_URL"
  else echo "ERROR: need curl or wget to download." >&2; exit 2; fi
fi
[ -f "$ZIP" ] || { echo "ERROR: zip not found: $ZIP" >&2; exit 2; }

# --- extract just the two files (basename match, any folder inside the zip) --
command -v unzip >/dev/null 2>&1 || { echo "ERROR: 'unzip' is required." >&2; exit 2; }
mkdir -p "$DATA/offshore_leaks"
for rel in "${need[@]}"; do
  base="$(basename "$rel")"
  member="$(unzip -Z1 "$ZIP" | grep -E "(^|/)$base\$" | head -n1 || true)"
  [ -n "$member" ] || { echo "ERROR: '$base' not found inside the zip." >&2; exit 3; }
  echo "Extracting $member -> $rel"
  unzip -p "$ZIP" "$member" > "$DATA/$rel"
done
[ -n "$cleanup_zip" ] && rm -f "$cleanup_zip"

# --- verify ------------------------------------------------------------------
fail=0
for rel in "${need[@]}"; do
  if verify "$rel"; then echo "VERIFIED: $rel"
  else echo "HASH MISMATCH: $rel (expected $(expected_hash "$rel"), got $(sha256 "$DATA/$rel"))" >&2; fail=1; fi
done
[ $fail -eq 0 ] || { echo "FAIL: one or more files did not match SHA256SUMS." >&2; exit 4; }

echo "Done. Run 'python3 scripts/check_data.py' to confirm the full data set."
