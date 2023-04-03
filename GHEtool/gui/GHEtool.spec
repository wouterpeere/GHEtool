# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['start_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('..\\..\\setup.cfg', '.'), ('./gui_config.ini', '.'), ('icons/', './GHEtool/gui/icons/'),('..\\Examples\\hourly_profile.csv', './GHEtool/Examples/')],
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
splash = Splash(
    'icons/icon_squared.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(5, 245),
    text_size=12,
    text_color='white',
    text_font='Lexend',
    minify_script=True,
    always_on_top=True,
    max_img_size=(250, 250)
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    [],
    exclude_binaries=True,
    name='GHEtool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icons\\Icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash.binaries,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GHEtool',
)
