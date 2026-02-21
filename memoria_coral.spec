# memoria_coral.spec
import os

block_cipher = None

a = Analysis(
    ['memoria_coral.py'],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub"), "huggingface_cache"),
        (os.path.join(os.path.dirname(__import__('customtkinter').__file__), 'assets'), 'customtkinter/assets'),
    ],
    hiddenimports=[
        'sentence_transformers',
        'transformers',
        'torch',
        'customtkinter',
        'github',
        'cryptography',
        'sklearn',
        'scipy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy.testing', 'unittest'],
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
    name='MemoriaCoralApp',
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
    icon=r'C:\Users\Oscar Fernandez\Desktop\Memoria Coral\Memoria Coral\MemoriaCoral.ico',
