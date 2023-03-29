# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['start_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('..//..//setup.cfg', '.'), ('icons/', './GHEtool/gui/icons/'),('..//Examples//hourly_profile.csv', './GHEtool/Examples/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GHEtool',
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
    icon=['GHEtool/gui/icons/Icon.icns'],
)

app = BUNDLE(
    exe,
    name='GHEtool.app',
    icon='./icons/Icon.icns',
    bundle_identifier=None,
)