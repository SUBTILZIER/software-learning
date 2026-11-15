#!/usr/bin/env bash
set -euo pipefail
EXPECTED="FAE4131C66753F22D9F92C668D856AE6482FAFB043348F978681E6606048C743"

hash_file() {
  python - "$1" <<'PY'
from pathlib import Path
import hashlib, sys
h=hashlib.sha256()
with Path(sys.argv[1]).open('rb') as f:
    for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
print(h.hexdigest().upper())
PY
}

case "${1:-}" in
  --test-copy)
    [[ $# -eq 3 ]] || { echo "usage: $0 --test-copy PREVIOUS_APK TARGET_APK" >&2; exit 64; }
    previous="$2"; target="$3"
    [[ "$(hash_file "$previous")" == "$EXPECTED" ]] || { echo "previous APK hash mismatch" >&2; exit 65; }
    mkdir -p "$(dirname "$target")"
    cp -f "$previous" "$target"
    echo "ROLLBACK_BEFORE_SHA256=D2226C697643BF01B44DA36DADC034005BA69F47AD9BB9A6B301025A0857F60C"
    echo "ROLLBACK_AFTER_SHA256=$(hash_file "$target")"
    echo "ROLLBACK_RESULT=PASS"
    ;;
  --device)
    [[ $# -eq 5 ]] || { echo "usage: $0 --device PREVIOUS_APK ADB_EXE PORT SERIAL" >&2; exit 64; }
    previous="$2"
    [[ "$(hash_file "$previous")" == "$EXPECTED" ]] || { echo "previous APK hash mismatch" >&2; exit 65; }
    "$3" -P "$4" -s "$5" install -r --no-streaming "$previous"
    ;;
  *)
    echo "usage: $0 --test-copy PREVIOUS_APK TARGET_APK | --device PREVIOUS_APK ADB_EXE PORT SERIAL" >&2
    exit 64
    ;;
esac
