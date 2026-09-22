# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/rodia/Desktop/ScholarDesk-V2-R1-FSDP/desktop/run_cathedra.py'],
    pathex=['C:/Users/rodia/Desktop/ScholarDesk-V2-R1-FSDP/backend'],
    binaries=[],
    datas=[('C:/Users/rodia/Desktop/ScholarDesk-V2-R1-FSDP/frontend/dist', 'frontend/dist'), ('C:/Users/rodia/Desktop/ScholarDesk-V2-R1-FSDP/backend/scholardesk_v2_dev.db', 'backend')],
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
    [],
    exclude_binaries=True,
    name='Cathedra',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Cathedra',
)
