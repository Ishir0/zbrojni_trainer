#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/release"
PACKAGE="$OUT/Zbrojni-Trainer-Mac"

cd "$ROOT"
npm run build
mkdir -p "$OUT"
python3 - "$PACKAGE" "$ROOT/dist" <<'PY'
from pathlib import Path
import shutil, sys

package, built = map(Path, sys.argv[1:])
if package.exists():
    shutil.rmtree(package)
package.mkdir(parents=True)
shutil.copytree(built, package / "dist")
PY
cp "$ROOT/portable-mac/Start.command" "$PACKAGE/Start.command"
cp "$ROOT/portable-mac/server.py" "$PACKAGE/server.py"
cp "$ROOT/portable-mac/README.txt" "$PACKAGE/README.txt"
chmod +x "$PACKAGE/Start.command"
rm -f "$OUT/Zbrojni-Trainer-Mac.zip"
cd "$OUT"
zip -qr "Zbrojni-Trainer-Mac.zip" "Zbrojni-Trainer-Mac"
echo "Package ready: $OUT/Zbrojni-Trainer-Mac.zip"
