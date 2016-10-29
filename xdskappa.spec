# -*- mode: python -*-

block_cipher = None


full_a = Analysis(['bin/xdskappa.py'],
             pathex=['lib/', '/src/xdskappa'],
#             binaries=None,
#             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[])
  #           win_no_prefer_redirects=False,
#             win_private_assemblies=False)
#             cipher=block_cipher)
show_stat_a = Analysis(['bin/show_stat.py'],
             pathex=['lib/', '/src/xdskappa.show_stat'],
#             binaries=None,
#             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[])
 #            win_no_prefer_redirects=False,
#             win_private_assemblies=False)
#             cipher=block_cipher)
run_xds_a = Analysis(['bin/run_xds.py'],
             pathex=['lib/', '/src/xdskappa.run_xds'],
#             binaries=None,
 #            datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[])
#             win_no_prefer_redirects=False,
#             win_private_assemblies=False)
#             cipher=block_cipher)

MERGE( (full_a, 'xdskappa', 'xdskappa'),
	(show_stat_a, 'xdskappa.show_stat', 'xdskappa.show_stat'),
	(run_xds_a, 'xdskappa.run_xds', 'xdskappa.run_xds') )

full_pyz = PYZ(full_a.pure)#, full_a.zipped_data,
             #cipher=block_cipher)
show_stat_pyz = PYZ(show_stat_a.pure)#, show_stat_a.zipped_data,
#             cipher=block_cipher)
run_xds_pyz = PYZ(run_xds_a.pure)#, run_xds_a.zipped_data,
#             cipher=block_cipher)

full_exe = EXE(full_pyz,
          full_a.scripts,
          exclude_binaries=True,
          name='xdskappa',
          debug=False,
          strip=False,
          upx=True,
          console=True )
show_stat_exe = EXE(show_stat_pyz,
          show_stat_a.scripts,
          exclude_binaries=True,
          name='xdskappa.show_stat',
          debug=False,
          strip=False,
          upx=True,
          console=True )
run_xds_exe = EXE(run_xds_pyz,
          run_xds_a.scripts,
          exclude_binaries=True,
          name='xdskappa.run_xds',
          debug=False,
          strip=False,
          upx=True,
          console=True )

full_coll = COLLECT(full_exe,
               full_a.binaries,
               full_a.zipfiles,
               full_a.datas,
               strip=False,
               upx=True,
               name='xdskappa')
show_stat_coll = COLLECT(show_stat_exe,
               show_stat_a.binaries,
               show_stat_a.zipfiles,
               show_stat_a.datas,
               strip=False,
               upx=True,
               name='xdskappa.show_stat')
run_xds_coll = COLLECT(run_xds_exe,
               run_xds_a.binaries,
               run_xds_a.zipfiles,
               run_xds_a.datas,
               strip=False,
               upx=True,
               name='xdskappa.run_xds')

