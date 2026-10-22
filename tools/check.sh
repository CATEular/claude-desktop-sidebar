#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export PYTHONDONTWRITEBYTECODE=1
node tests/test_desktop_effects.js
/usr/bin/python3 tests/test_installer.py
/usr/bin/python3 - <<'PY'
from pathlib import Path
import json
import subprocess
for path in sorted(Path('.').rglob('*')):
    if any(name in path.parts for name in ('.git', 'dist', '__pycache__')) or not path.is_file():
        continue
    if path.suffix == '.py':
        compile(path.read_text(), str(path), 'exec')
    elif path.suffix == '.json':
        json.loads(path.read_text())
    elif path.suffix == '.sh':
        subprocess.run(['bash', '-n', str(path)], check=True)
    elif path.suffix == '.js':
        subprocess.run(['node', '--check', str(path)], check=True, capture_output=True)
print('PASS all Python/JSON/shell/JavaScript syntax')
PY
env GI_TYPELIB_PATH="/usr/lib/gnome-shell:/usr/lib/x86_64-linux-gnu/mutter-6${GI_TYPELIB_PATH:+:$GI_TYPELIB_PATH}" \
  LD_LIBRARY_PATH="/usr/lib/gnome-shell:/usr/lib/x86_64-linux-gnu/mutter-6${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
  gjs -c 'const Gio=imports.gi.Gio;const St=imports.gi.St;let dir="extensions/claude-desktop-effects@local/";for(let file of ["extension.js","logic.js","prefs.js"]){let [ok,bytes]=Gio.File.new_for_path(dir+file).load_contents(null);Reflect.parse(imports.byteArray.toString(bytes));}let theme=new St.Theme();theme.load_stylesheet(Gio.File.new_for_path(dir+"stylesheet.css"));print("PASS native GJS parsing and St stylesheet");'
echo 'Sidebar offline checks passed; actual desktop layout and hardware require desktop verification.'
