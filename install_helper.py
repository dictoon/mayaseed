import sys
import os
import maya.cmds as cmds

def install(userSetup_file, install_dir):
    installation_name = 'mayaseed'

    print 'adding paths for {0} to {1}'.format(installation_name, install_dir)

    file = open(userSetup_file, 'r')
    file_contents = file.read()
    file.close()

    file = open(userSetup_file, 'w')

    inside_block = False
    for line in file_contents.split('\n'):
      is_block_delimiter = line[:len(installation_name) + 3] == '// ' + installation_name
      if is_block_delimiter:
        inside_block = not inside_block
      if not inside_block and not is_block_delimiter:
        file.write(line + '\n')

    separator = ';' if sys.platform == 'win32' or sys.platform == 'win64' else ':'

    file.write('// ' + installation_name + '  -------------------------------------------------------------------------------\n')
    file.write('\n')
    file.write('putenv "MAYA_SCRIPT_PATH" (`getenv "MAYA_SCRIPT_PATH"` + \"{0}{1}\");\n'.format(separator, os.path.join(install_dir, 'scripts')))
    file.write('putenv "MAYA_SCRIPT_PATH" (`getenv "MAYA_SCRIPT_PATH"` + \"{0}{1}\");\n'.format(separator, os.path.join(install_dir, 'graphics')))
    file.write('putenv "MAYA_PLUG_IN_PATH" (`getenv "MAYA_PLUG_IN_PATH"` + \"{0}{1}\");\n'.format(separator, os.path.join(install_dir, 'plugins')))
    file.write('\n')
    file.write('// ' + installation_name + '  -------------------------------------------------------------------------------\n')

    file.close()

    cmds.confirmDialog(title=installation_name + ' install', message='All done! Just restart Maya and enable any plugins not already enabled in the plugin manager.', button='OK')
