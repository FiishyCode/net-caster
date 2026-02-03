# -*- mode: python ; coding: utf-8 -*-
import os
import pydivert

# Get paths relative to the spec file location
spec_root = os.path.dirname(os.path.abspath(SPECPATH))
pydivert_path = os.path.dirname(pydivert.__file__)

a = Analysis(
    [os.path.join(spec_root, 'src', 'main.py')],
    pathex=[],
    binaries=[
        (os.path.join(spec_root, 'dependencies', 'windivert', 'WinDivert.dll'), '.'),
        (os.path.join(spec_root, 'dependencies', 'windivert', 'WinDivert64.sys'), '.')
    ],
    datas=[
        (os.path.join(spec_root, 'assets', 'icons', 'icon.ico'), '.'),
        (os.path.join(spec_root, 'assets', 'icons', 'icon.png'), '.'),
        (pydivert_path, 'pydivert'),
        (os.path.join(spec_root, 'assets', 'screenshots', 'NONE.png'), '.'),
        (os.path.join(spec_root, 'assets', 'screenshots', 'N.png'), '.'),
        (os.path.join(spec_root, 'assets', 'screenshots', 'NE.png'), '.'),
        (os.path.join(spec_root, 'assets', 'screenshots', 'E.png'), '.'),
        (os.path.join(spec_root, 'assets', 'screenshots', 'SE.png'), '.'),
        (os.path.join(spec_root, 'assets', 'screenshots', 'S.png'), '.'),
        (os.path.join(spec_root, 'assets', 'screenshots', 'SW.png'), '.')
    ],
    hiddenimports=['pynput', 'pynput.keyboard', 'pynput.mouse', 'pynput.keyboard._win32', 'pynput.mouse._win32', 'pynput._util', 'pynput._util.win32', 'pydivert'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Application',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon=[os.path.join(spec_root, 'assets', 'icons', 'icon.ico')],
)
