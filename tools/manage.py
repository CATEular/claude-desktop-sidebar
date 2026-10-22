#!/usr/bin/python3
"""Install, enable and restore the right-side desktop cards."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
UUIDS = ('claude-desktop-effects@local',)
STATE = Path('.local/state/claude-desktop-sidebar')


def run(argv, **kwargs):
    return subprocess.run(argv, check=True, text=True, capture_output=True, **kwargs).stdout.strip()


def safe_target(home, relative):
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Invalid managed path: ' + str(relative))
    target = home / relative
    if os.path.commonpath((str(home.resolve()), str(target.resolve()))) != str(home.resolve()):
        raise ValueError('Managed path escapes the home directory: ' + str(relative))
    return target



def write_plan(home, plan):
    """Back up both existing and previously absent files for exact restoration."""
    backup = home / STATE / 'backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True)
    manifest = []
    for relative in plan:
        target = safe_target(home, relative)
        record = {'path': relative, 'kind': 'absent'}
        if relative in ('.config/conky/minimal/data/todo.json', '.config/conky/minimal/data/notes.json'):
            record['preserve'] = True
        if target.is_symlink():
            record.update(kind='symlink', link=os.readlink(target))
        elif target.exists():
            if not target.is_file():
                raise ValueError('Expected a file: ' + str(target))
            record.update(kind='file', mode=target.stat().st_mode & 0o777)
            stored = backup / 'files' / relative
            stored.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, stored)
        manifest.append(record)
    (backup / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    try:
        for relative, entry in plan.items():
            target = safe_target(home, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.is_symlink():
                target.unlink()
            target.write_bytes(entry['data'])
            target.chmod(entry['mode'])
    except Exception:
        restore_files(home, backup)
        raise
    (home / STATE / 'latest-backup').write_text(str(backup))
    return backup


def restore_files(home, backup):
    for record in reversed(json.loads((backup / 'manifest.json').read_text())):
        target = safe_target(home, record['path'])
        if record.get('preserve') and target.exists():
            continue
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.exists():
            raise ValueError('Refusing to replace a directory: ' + str(target))
        if record['kind'] != 'absent':
            target.parent.mkdir(parents=True, exist_ok=True)
        if record['kind'] == 'file':
            shutil.copy2(backup / 'files' / record['path'], target)
            target.chmod(record['mode'])
        elif record['kind'] == 'symlink':
            target.symlink_to(record['link'])


def desktop_session():
    if not shutil.which('gnome-extensions'):
        raise RuntimeError('缺少 gnome-extensions。请在 GNOME 3.36 桌面终端运行。')
    version = run(['gnome-shell', '--version'])
    if not re.search(r'\b3\.36\.', version):
        raise RuntimeError('本套件只支持 GNOME Shell 3.36，当前为：' + version)
    return set(run(['gnome-extensions', 'list', '--enabled']).splitlines())


def disable_ours():
    enabled = desktop_session()
    for uuid in UUIDS:
        if uuid in enabled:
            run(['gnome-extensions', 'disable', uuid])


def latest_backup(home):
    return Path((home / STATE / 'latest-backup').read_text().strip())


def build_plan(home, data_mount):
    """Prepare sidebar files only; preserve any existing notes and settings."""
    home = Path(home)
    data_mount = str(Path(data_mount).expanduser().resolve())
    if any(character in data_mount for character in '\n\r{}'):
        raise ValueError('Data mount contains unsupported Conky syntax.')
    plan = {}

    def add(relative, data, mode=0o644):
        safe_target(home, relative)
        plan[str(relative)] = {'data': data.encode() if isinstance(data, str) else data, 'mode': mode}

    source = ROOT / 'extensions/claude-desktop-effects@local'
    destination = Path('.local/share/gnome-shell/extensions/claude-desktop-effects@local')
    for name in ('metadata.json', 'extension.js', 'logic.js', 'prefs.js', 'stylesheet.css', 'settings.py'):
        add(destination / name, (source / name).read_bytes())
    source = ROOT / 'desktop/conky/minimal'
    for path in source.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            data = path.read_bytes()
            if path.suffix == '.conf':
                data = data.decode().replace('@DATA_MOUNT@', data_mount).encode()
            add(Path('.config/conky/minimal') / path.relative_to(source), data,
                0o755 if path.suffix == '.sh' else 0o644)
    for name in ('todo', 'notes'):
        relative = f'.config/conky/minimal/data/{name}.json'
        if not safe_target(home, relative).exists():
            add(relative, '[]\n')
    relative = '.config/claude-desktop-effects/settings.json'
    if not safe_target(home, relative).exists():
        add(relative, (ROOT / 'examples/desktop-effects.json').read_bytes())
    settings = str(home / destination / 'settings.py')
    add('.local/bin/desktop-effects', '#!/usr/bin/python3\nimport runpy\nrunpy.run_path(' + repr(settings) + ',run_name="__main__")\n', 0o755)
    add('.local/share/applications/claude-desktop-effects.desktop',
        '[Desktop Entry]\nName=侧边栏设置\nType=Application\nTerminal=false\nIcon=preferences-desktop\n'
        'Categories=Settings;DesktopSettings;\nExec=/usr/bin/python3 "' + settings.replace('"', '\\"') + '"\n')
    start = str(home / '.config/conky/minimal/start.sh')
    add('.config/autostart/conky-sys-card.desktop',
        '[Desktop Entry]\nType=Application\nName=Claude Desktop Sidebar\nNoDisplay=true\n'
        'X-GNOME-Autostart-enabled=true\nX-GNOME-Autostart-Delay=5\nExec="' + start.replace('"', '\\"') + '"\n')
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'enable', 'disable', 'restore', 'status'))
    parser.add_argument('--dry-run', action='store_true', help='仅预览写入计划，不连接桌面或修改设置')
    parser.add_argument('--data-mount', default=str(Path.home()), help='第二块存储监控路径')
    parser.add_argument('--backup', type=Path, help='恢复指定备份，默认最近一次安装')
    args = parser.parse_args()
    home = Path.home()
    service = home / '.config/conky/minimal/scripts/widget_service.py'
    if args.dry_run and args.action != 'install':
        parser.error('--dry-run 只适用于 install')
    if args.action == 'install':
        plan = build_plan(home, args.data_mount)
        if args.dry_run:
            print('\n'.join(sorted(plan)))
            print(f'计划写入 {len(plan)} 个侧边栏文件；未改动桌面。')
            return
        disable_ours()
        backup = write_plan(home, plan)
        print('侧边栏已安装，已有笔记与设置保留。备份：' + str(backup))
        print('请在 X11 按 Alt+F2 → r 重载 Shell，再运行 enable。')
    elif args.action == 'enable':
        desktop_session()
        run(['/usr/bin/python3', str(home / '.local/share/gnome-shell/extensions/claude-desktop-effects@local/settings.py'), '--apply'])
        run(['/usr/bin/python3', str(service), 'start'])
        print('侧边栏已启用。设置：~/.local/bin/desktop-effects → 右侧卡片')
    elif args.action == 'disable':
        disable_ours()
        run(['/usr/bin/python3', str(service), 'stop'])
        print('侧边栏已停用，笔记数据保留。')
    elif args.action == 'restore':
        backup = (args.backup or latest_backup(home)).resolve()
        if not (backup / 'manifest.json').is_file():
            raise RuntimeError('备份目录缺少 manifest.json。')
        disable_ours()
        if service.is_file():
            run(['/usr/bin/python3', str(service), 'stop'])
        restore_files(home, backup)
        print('已恢复安装前的侧边栏文件，待办和笔记保留；请重载 Shell。')
    else:
        print(run(['gnome-extensions', 'info', UUIDS[0]]))
        if service.is_file():
            print(run(['/usr/bin/python3', str(service), 'status']))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
