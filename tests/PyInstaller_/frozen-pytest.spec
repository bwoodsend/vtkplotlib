# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_entry_point

# Collect all available pytest plugins.
datas, hidden = collect_entry_point("pytest11")

a = Analysis(['frozen-pytest.py'], datas=datas, hiddenimports=hidden)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='frozen-pytest')
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name='frozen-pytest')
