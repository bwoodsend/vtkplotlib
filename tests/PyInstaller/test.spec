# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from PyInstaller.utils.hooks import collect_data_files


a = Analysis(['test.py'],
             pathex=[SPECPATH],
             binaries=[],
             # I seriously doubt anyone actually will want the rabbit in their packages so it is excluded by
             # default (in hook-vtkplotlib.py). But it is needed for testing so include it here.
             datas=collect_data_files("vtkplotlib", "**.*.stl"),
             hiddenimports=["vtkplotlib"],
             hookspath=[],
             runtime_hooks=[],
             excludes=["matplotlib.pylab", "matplotlib.backends", "matplotlib.pyplot", 'vtkmodules.all', 'scipy'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='test',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               upx_exclude=[],
               name='test')
