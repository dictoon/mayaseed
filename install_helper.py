import sys
import os
import maya.cmds as cmds

def append_env(variable, path):
    separator = ';' if sys.platform == 'win32' or sys.platform == 'win64' else ':'
    return 'putenv "{0}" (`getenv "{0}"` + \"{1}{2}\");'.format(variable, separator, path.replace('\\', '/'))

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

    file.write('// ' + installation_name + '  -------------------------------------------------------------------------------\n')
    file.write('\n')
    file.write(append_env("MAYA_SCRIPT_PATH", os.path.join(install_dir, 'scripts')) + '\n')
    file.write(append_env("MAYA_SCRIPT_PATH", os.path.join(install_dir, 'graphics')) + '\n')
    file.write(append_env("MAYA_PLUG_IN_PATH", os.path.join(install_dir, 'plugins')) + '\n')
    file.write('\n')
    file.write('// ' + installation_name + '  -------------------------------------------------------------------------------\n')

    file.close()

    cmds.confirmDialog(title=installation_name + ' installation', message='All done! Just restart Maya and enable any plugins not already enabled in the plugin manager.', button='OK')
