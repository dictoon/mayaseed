
import maya.mel as mel
import maya.cmds as cmds
import os

userSetup_file = None

for path in mel.eval('getenv MAYA_SCRIPT_PATH').split(':'):
    if os.path.exists(path):
        for file in os.listdir(path):
            if file == 'userSetup.mel':
                userSetup_file = os.path.join(path, file)

if not userSetup_file:
    userSetup_file = os.path.join(mel.eval('getenv MAYA_SCRIPT_PATH').split(':')[1], 'userSetup.mel')
    file = open(userSetup_file, 'w')
    file.close()

print userSetup_file
file = open(userSetup_file, 'r')
file_contents = file.read()
file.close()
file = open(userSetup_file, 'w')

inside_mayaseed_block = False
for line in file_contents.split('\n'):
    if line[:11] == '// mayaseed':
        if inside_mayaseed_block:
            inside_mayaseed_block = False
        else:
            inside_mayaseed_block = True
    if not inside_mayaseed_block:
       if not line[:11] == '// mayaseed':
           file.write(line + '\n')

file.write('\n')
file.write('\n')
file.write('// mayaseed  -------------------------------------------------------------------------------\n')
file.write('\n')
file.write('$env_script_path = `getenv MAYA_SCRIPT_PATH`;\n')
file.write('$env_plugin_path = `getenv MAYA_PLUG_IN_PATH`;\n')
file.write('putenv MAYA_SCRIPT_PATH ($env_script_path + ":' + os.path.join(os.path.split(cmds.file(query=True, sn=True))[0], 'scripts') + ':' + os.path.join(os.path.split(cmds.file(query=True, sn=True))[0], 'graphics') + '");\n')
file.write('putenv MAYA_PLUG_IN_PATH ($env_plugin_path + ":' + os.path.join(os.path.split(cmds.file(query=True, sn=True))[0], 'plugins') + '");\n')
file.write('\n')
file.write('// mayaseed  -------------------------------------------------------------------------------\n')

file.close() 

cmds.confirmDialog(title='Mayaseed', message='All done!, to enable mayaseed just restart mays then go into the plugin manager and enable mayaseed.py. enjoy! jt', button='OK')

