# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['honehone_clock.py'],
    pathex=[],
    binaries=[],
    datas=[('config.json', '.'), ('theme', 'theme'), ('attest', 'attest')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['split_characters'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='honehone_clock',
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
    version='version_info.txt',
    icon='attest\\logo.ico',
)
