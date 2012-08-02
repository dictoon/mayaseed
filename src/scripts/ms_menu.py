# Copyright (c) 2012 Jonathan Topf

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import maya.cmds as cmds
import maya.mel
import maya.utils as mu
import __main__ 
import ms_commands
import os

#****************************************************************************************************************************************************************************************************
# create ms_menu ************************************************************************************************************************************************************************************
#****************************************************************************************************************************************************************************************************

def createMenu():
    try:
        cmds.deleteUI(mayaseed_menu)
    except:
        pass

    gMainWindow = maya.mel.eval('$temp1=$gMainWindow')
    mayaseed_menu = cmds.menu('ms_menu', parent=gMainWindow, label='Mayaseed', tearOff=True )
    __main__.mayaseed_menu = mayaseed_menu #add the menu to the main namespace

#****************************************************************************************************************************************************************************************************
# build ms_menu function ****************************************************************************************************************************************************************************
#****************************************************************************************************************************************************************************************************


def buildMenu():

    #create list of render setting nodes
    render_settings_nodes = cmds.ls(type='ms_renderSettings')

    cmds.menu('ms_menu', edit=True, deleteAllItems=True, pmc=('import ms_menu\nms_menu.buildMenu()'))
    
    cmds.menuItem('menu_export', subMenu=True, label='Export', to=True, parent='ms_menu')        
    #create sub menu of render setings nodes
    for render_settings_node in render_settings_nodes:
        cmds.menuItem(label=render_settings_node, parent='menu_export', command=('import ms_export \nms_export.export("{0}")'.format(render_settings_node)))

    cmds.menuItem(divider=True, parent='ms_menu')

    cmds.menuItem(label='Add Render Settings Node', parent='ms_menu', command='import maya.cmds\nmaya.cmds.createNode("ms_renderSettings")') #need to import maya.cmds module otehrwise cmds isnt recognised
    cmds.menuItem('menu_select_render_settings', subMenu=True, label='Select Render settings Node', to=True, parent='ms_menu')
    #create sub menu of render setings nodes
    for render_settings_node in render_settings_nodes:
        cmds.menuItem(label=render_settings_node, parent='menu_select_render_settings', command=('import maya.cmds as cmds\ncmds.select("{0}")'.format(render_settings_node)))
    

    cmds.menuItem(divider=True, parent='ms_menu')
    cmds.menuItem(label='Add Environment Node', parent='ms_menu', command='import maya.cmds\nmaya.cmds.createNode("ms_environment")') #need to import maya.cmds module otehrwise cmds isnt recognised
    cmds.menuItem('menu_select_environment', subMenu=True, label='Select Environment Node', to=True, parent='ms_menu')
    #list environment nodes
    environments = cmds.ls(type='ms_environment')
    for environment in environments:
        cmds.menuItem(label=environment, parent='menu_select_environment', command=('import maya.cmds as cmds\ncmds.select("{0}")'.format(environment)))

    cmds.menuItem(divider=True, parent='ms_menu')

    cmds.menuItem(label='Create appleseed material', parent='ms_menu', command=('import maya.cmds as cmds\ncmds.shadingNode("ms_appleseed_material", asShader=True)'))


   # load shader types
    entity_defs = ms_commands.getEntityDefs(os.path.join(ms_commands.ROOT_DIRECTORY, 'scripts', 'appleseedEntityDefs.xml'))
 
    # create BSDFs
    cmds.menuItem('menu_create_BSDF', subMenu=True, label='Create BSDF', to=True, parent='ms_menu')
    for entity_key in entity_defs.keys():
        if (entity_defs[entity_key].type == 'bsdf'):
            command = 'import ms_commands\nms_commands.createShadingNode("' + entity_key + '")'
            cmds.menuItem(label=entity_key, parent='menu_create_BSDF', command=command)

    # create EDFs
    cmds.menuItem('menu_create_EDF', subMenu=True, label='Create EDF', to=True, parent='ms_menu')
    for entity_key in entity_defs.keys():
        if (entity_defs[entity_key].type == 'edf'):
            command = 'import ms_commands\nms_commands.createShadingNode("' + entity_key + '")'
            cmds.menuItem(label=entity_key, parent='menu_create_EDF', command=command)

    # create surface_shaders
    cmds.menuItem('menu_create_surface_shader', subMenu=True, label='Create Surface Shader', to=True, parent='ms_menu')
    for entity_key in entity_defs.keys():
        if (entity_defs[entity_key].type == 'surface_shader'):
            command = 'import ms_commands\nms_commands.createShadingNode("' + entity_key + '")'
            cmds.menuItem(label=entity_key, parent='menu_create_surface_shader', command=command)


    cmds.menuItem(divider=True, parent='ms_menu')
    cmds.menuItem(label='Add custom shader translation', parent='ms_menu', command='import ms_commands\nms_commands.addShadingAttribs()') 
    cmds.menuItem(label='Remove custom shader translation', parent='ms_menu', command='import ms_commands\nms_commands.removeShadingAttribs()')    
    
    cmds.menuItem(divider=True, parent='ms_menu')
    cmds.menuItem(label='About', parent='ms_menu', command='import ms_commands\nms_commands.msInfoDial()')

def deleteMenu():
    cmds.deleteUI('ms_menu')























