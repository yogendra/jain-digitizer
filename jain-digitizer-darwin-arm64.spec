# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/jain_digitizer/desktop/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src/jain_digitizer/desktop/icon.png', 'jain_digitizer/desktop'), ('src/jain_digitizer/common/prompt-html.md', 'jain_digitizer/common'), ('src/jain_digitizer/common/prompt-md.md', 'jain_digitizer/common')],
    hiddenimports=[],
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
    name='jain-digitizer-darwin-arm64',
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
    icon=['src/jain_digitizer/desktop/icon.png'],
)
app = BUNDLE(
    exe,
    name='jain-digitizer-darwin-arm64.app',
    icon='src/jain_digitizer/desktop/icon.png',
    bundle_identifier='me.yogendra.jain-digitizer',
)
