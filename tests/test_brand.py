import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'brand' / 'apply.py'
spec = importlib.util.spec_from_file_location('rumars_branding', SCRIPT)
branding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(branding)

class RumarsBrandingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        files = {
            'Cargo.toml': '[package]\nname = "rustdesk"\n',
            'build.py': '# RustDesk builder\n',
            'flutter/pubspec.yaml': 'flutter:\n  assets:\n    - assets/\n',
            'flutter/lib/desktop/pages/desktop_home_page.dart':
                "import '../widgets/button.dart';\n"
                "Widget logo() => Align(child: loadLogo(),);\n"
                "Widget installer() => bind.mainGotoInstall();\n",
            'flutter/windows/runner/Runner.rc':
                'VALUE "CompanyName", "Purslane Tech Pte. Ltd." "\\0"\n'
                'VALUE "FileDescription", "RustDesk Remote Desktop" "\\0"\n'
                'VALUE "ProductName", "RustDesk" "\\0"\n',
            'flutter/windows/runner/main.cpp':
                'std::wstring app_name = L"RustDesk";\n  // Uri links dispatch\n',
            'flutter/windows/runner/resources/app_icon.ico': 'original',
            'res/icon.png': 'original',
            'res/32x32.png': 'original',
            'res/64x64.png': 'original',
            'res/128x128.png': 'original',
            'res/128x128@2x.png': 'original',
        }
        for name, value in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding='utf8')

    def tearDown(self):
        self.temp.cleanup()

    def test_brand_and_original_install_action(self):
        branding.apply(self.root)
        home = (self.root/'flutter/lib/desktop/pages/desktop_home_page.dart').read_text('utf8')
        self.assertIn('RumarsBrandingPanel()', home)
        self.assertIn('bind.mainGotoInstall()', home)
        self.assertIn('Rumars Solution Remote Support',
                      (self.root/'flutter/windows/runner/Runner.rc').read_text('utf8'))
        self.assertTrue((self.root/'flutter/assets/rumars_logo.png').stat().st_size > 1000)
        self.assertTrue((self.root/'flutter/windows/runner/resources/app_icon.ico').stat().st_size > 1000)
        with self.assertRaises(RuntimeError):
            branding.apply(self.root)

    def test_incompatible_source_fails_before_modifications(self):
        path = self.root/'flutter/lib/desktop/pages/desktop_home_page.dart'
        path.write_text('unexpected upstream version')
        with self.assertRaises(RuntimeError):
            branding.apply(self.root)
        self.assertEqual(path.read_text(), 'unexpected upstream version')

if __name__ == '__main__':
    unittest.main()
