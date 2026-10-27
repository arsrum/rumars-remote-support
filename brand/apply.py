#!/usr/bin/env python3
"""Apply Rumars branding to pinned RustDesk 1.4.9 checkout."""
from __future__ import annotations
import base64
import io
import re
import sys
from pathlib import Path
from PIL import Image, ImageOps

BASE = Path(__file__).resolve().parent

def once(src, old, new, where):
    if src.count(old) != 1:
        raise RuntimeError(f'{where}: expected one occurrence of {old!r}, found {src.count(old)}')
    return src.replace(old, new, 1)

def apply(root):
    root = Path(root).resolve()
    if not (root / 'Cargo.toml').is_file() or not (root / 'build.py').is_file():
        raise RuntimeError('Not a RustDesk checkout')
    home = root / 'flutter/lib/desktop/pages/desktop_home_page.dart'
    rc = root / 'flutter/windows/runner/Runner.rc'
    cpp = root / 'flutter/windows/runner/main.cpp'
    pub = root / 'flutter/pubspec.yaml'
    for p in (home, rc, cpp, pub):
        if not p.exists():
            raise RuntimeError(f'Missing {p}')
    if not re.search(r'(?m)^\s*assets:\s*\n\s*- assets/', pub.read_text('utf8')):
        raise RuntimeError('Missing Flutter assets registration')
    new_home = once(home.read_text('utf8'), "import '../widgets/button.dart';",
                    "import '../widgets/button.dart';\nimport '../widgets/rumars_support_branding.dart';", str(home))
    new_home = once(new_home, 'child: loadLogo(),',
                    'child: const RumarsBrandingPanel(),', str(home))
    new_rc = rc.read_text('utf8')
    for key, old, new in [
        ('CompanyName', 'Purslane Tech Pte. Ltd.', 'Rumars Solution'),
        ('FileDescription', 'RustDesk Remote Desktop', 'Rumars Solution Remote Support'),
        ('ProductName', 'RustDesk', 'Rumars Solution Remote Support'),
    ]:
        new_rc = once(new_rc, f'VALUE "{key}", "{old}"', f'VALUE "{key}", "{new}"', str(rc))
    new_cpp = once(cpp.read_text('utf8'), '  // Uri links dispatch\n',
                   '  app_name = L"Rumars Solution Remote Support"; // UI title only\n  // Uri links dispatch\n', str(cpp))
    widget = root / 'flutter/lib/desktop/widgets/rumars_support_branding.dart'
    if widget.exists():
        raise RuntimeError('Already patched')
    for p in ['res/icon.png', 'res/32x32.png', 'res/64x64.png', 'res/128x128.png',
              'res/128x128@2x.png', 'flutter/windows/runner/resources/app_icon.ico']:
        if not (root/p).exists():
            raise RuntimeError(f'Unexpected upstream layout: {p}')
    data = base64.b64decode((BASE/'logo.b64').read_text('ascii').strip(), validate=True)
    image = Image.open(io.BytesIO(data)).convert('RGBA')
    if image.width < 64 or image.height < 64:
        raise RuntimeError('Bad logo resolution')
    home.write_text(new_home, encoding='utf8')
    rc.write_text(new_rc, encoding='utf8')
    cpp.write_text(new_cpp, encoding='utf8')
    widget.parent.mkdir(parents=True, exist_ok=True)
    widget.write_bytes((BASE/'panel.dart').read_bytes())
    logo_path = root/'flutter/assets/rumars_logo.png'
    logo_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(logo_path, optimize=True)
    contained = ImageOps.contain(image, (256,256), Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA',(256,256),(0,0,0,0))
    canvas.alpha_composite(contained, ((256-contained.width)//2,(256-contained.height)//2))
    for name, size in [('res/icon.png',256),('res/32x32.png',32),
                       ('res/64x64.png',64),('res/128x128.png',128),
                       ('res/128x128@2x.png',256)]:
        canvas.resize((size,size), Image.Resampling.LANCZOS).save(root/name, optimize=True)
    ico = root/'flutter/windows/runner/resources/app_icon.ico'
    canvas.save(ico, format='ICO', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
    for opt in ['res/icon.ico','res/tray-icon.ico','flutter/assets/icon.ico']:
        if (root/opt).exists():
            (root/opt).write_bytes(ico.read_bytes())
    print('Rumars branded source ready; original RustDesk installation logic and servers preserved')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: apply.py RUSTDESK_SOURCE_DIRECTORY')
    apply(sys.argv[1])
