"""Verify the sidebar installer against temporary homes without a desktop."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sidebar_manager', ROOT / 'tools/manage.py')
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)


class InstallerTests(unittest.TestCase):
    def test_fresh_sidebar_only_install_and_restore(self):
        with tempfile.TemporaryDirectory(prefix='sidebar-home-') as temporary:
            home = Path(temporary)
            plan = manager.build_plan(home, home)
            self.assertFalse(list(home.iterdir()))
            self.assertTrue(all('cream-island' not in name and 'terminal' not in name and 'gtk.css' not in name for name in plan))
            backup = manager.write_plan(home, plan)
            config = json.loads((home / '.config/claude-desktop-effects/settings.json').read_text())
            self.assertEqual(config['sidebarWorkspaces'], [2])
            self.assertFalse(config['workspaceWallpapersEnabled'])
            self.assertFalse(config['topbarHoverEnabled'])
            self.assertTrue((home / '.local/share/gnome-shell/extensions/claude-desktop-effects@local/logic.js').is_file())
            self.assertNotIn('@DATA_MOUNT@', (home / '.config/conky/minimal/system.conf').read_text())
            notes = home / '.config/conky/minimal/data/notes.json'
            notes.write_text('[{"key":"keep","val":"new note"}]')
            manager.restore_files(home, backup)
            self.assertEqual(json.loads(notes.read_text())[0]['val'], 'new note')
            self.assertFalse((home / '.local/bin/desktop-effects').exists())

    def test_existing_notes_config_and_permissions_preserved(self):
        with tempfile.TemporaryDirectory(prefix='sidebar-home-') as temporary:
            home = Path(temporary)
            data = home / '.config/conky/minimal/data/todo.json'
            data.parent.mkdir(parents=True)
            data.write_text('[{"text":"keep","done":false}]')
            config = home / '.config/claude-desktop-effects/settings.json'
            config.parent.mkdir(parents=True)
            config.write_text('{"wallpapers":["file:///existing.jpg"],"sidebarWorkspaces":[1,3]}')
            widget = home / '.config/conky/minimal/scripts/widget_service.py'
            widget.parent.mkdir(parents=True)
            widget.write_text('# previous service\n')
            widget.chmod(0o600)
            originals = {p: p.read_bytes() for p in (data, config, widget)}
            backup = manager.write_plan(home, manager.build_plan(home, home))
            self.assertEqual(data.read_bytes(), originals[data])
            self.assertEqual(config.read_bytes(), originals[config])
            manager.restore_files(home, backup)
            for path in originals:
                self.assertEqual(path.read_bytes(), originals[path])
            self.assertEqual(widget.stat().st_mode & 0o777, 0o600)

    def test_path_safety_and_symlink_restore(self):
        with tempfile.TemporaryDirectory(prefix='sidebar-home-') as temporary:
            home = Path(temporary)
            with self.assertRaises(ValueError):
                manager.safe_target(home, '../outside')
            original = home / 'original'
            original.write_text('original')
            link = home / 'link'
            link.symlink_to(original)
            backup = manager.write_plan(home, {'link': {'data': b'new', 'mode': 0o644}})
            self.assertFalse(link.is_symlink())
            self.assertEqual(original.read_text(), 'original')
            manager.restore_files(home, backup)
            self.assertTrue(link.is_symlink())


if __name__ == '__main__':
    unittest.main()
