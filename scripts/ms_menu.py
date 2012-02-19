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


#****************************************************************************************************************************************************************************************************
# utility functions *********************************************************************************************************************************************************************************
#****************************************************************************************************************************************************************************************************

#
# addMsShadingAttribs function --
#    

def addMsShadingAttribs():
    shaderName = False
    try:
        shape = cmds.listRelatives(cmds.ls(sl=True)[0], s=True)[0]
        shadingEngine = cmds.listConnections(shape, t='shadingEngine')[0]
        shaderName = cmds.connectionInfo((shadingEngine + ".surfaceShader"),sourceFromDestination=True).split('.')[0] 
    except:
        print '# No objects with shader connectoins selectd'
    if shaderName:
        if not cmds.objExists(shaderName + '.mayaseed_bsdf'):
            cmds.addAttr(shaderName, ln='mayaseed_bsdf',  at='enum', en='Lambertian:Ashikhmin-Shirley:Kelemen:Specular_BRDF:<none>')
            cmds.addAttr(shaderName, ln='mayaseed_edf',  at='enum', en='<None>:Diffuse')
            cmds.addAttr(shaderName, ln='mayaseed_surface_shader', at='enum', en='Physical:Constant:<None>')
        else:
            print '# {0} already has Mayaseed shader attributes'.format(shaderName)

#
# removeMsShadingAttribs function --
#  

def removeMsShadingAttribs():
    shaderName = ''
    try:
        shape = cmds.listRelatives(cmds.ls(sl=True)[0], s=True)[0]
        shadingEngine = cmds.listConnections(shape, t='shadingEngine')[0]
        shaderName = cmds.connectionInfo((shadingEngine + ".surfaceShader"),sourceFromDestination=True).split('.')[0] 
    except:
        print '# No objects with shader connectoins selectd'
    if shaderName:
        if cmds.objExists(shaderName + '.mayaseed_bsdf'):
            cmds.deleteAttr(shaderName, at='mayaseed_bsdf')
            cmds.deleteAttr(shaderName, at='mayaseed_edf')
            cmds.deleteAttr(shaderName, at='mayaseed_surface_shader')
        else:
            print '# {0} has no Mayaseed shader attributes to remove'.format(shaderName)


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
    cmds.menu('ms_menu', edit=True, deleteAllItems=True, pmc=('import ms_menu\nms_menu.buildMenu()'))
    cmds.menuItem(label='Add Render Settings Node', parent='ms_menu', command='import maya.cmds\nmaya.cmds.createNode("ms_renderSettings")') #need to import maya.cmds module otehrwise cmds isnt recognised
    cmds.menuItem('menu_select_render_settings', subMenu=True, label='Select Render settings Node', to=True, parent='ms_menu')
    #list menuSettings nodes
    renderSettingss = cmds.ls(type='ms_renderSettings')
    for renderSetting in renderSettingss:
        cmds.menuItem(label=renderSetting, parent='menu_select_render_settings', command=('import maya.cmds as cmds\ncmds.select("{0}")'.format(renderSetting)))
        

    cmds.menuItem(divider=True, parent='ms_menu')
    cmds.menuItem(label='Add Environment Node', parent='ms_menu', command='import maya.cmds\nmaya.cmds.createNode("ms_environment")') #need to import maya.cmds module otehrwise cmds isnt recognised
    cmds.menuItem('menu_select_environment', subMenu=True, label='Select Environment Node', to=True, parent='ms_menu')
    #list environment nodes
    environments = cmds.ls(type='ms_environment')
    for environment in environments:
        cmds.menuItem(label=environment, parent='menu_select_environment', command=('import maya.cmds as cmds\ncmds.select("{0}")'.format(environment)))

    cmds.menuItem(divider=True, parent='ms_menu')
    cmds.menuItem(label='Add custom shader translation', parent='ms_menu', command='ms_menu.addMsShadingAttribs()') 
    cmds.menuItem(label='Remove custom shader translation', parent='ms_menu', command='ms_menu.removeMsShadingAttribs()')    
    
    cmds.menuItem(divider=True, parent='ms_menu')
    cmds.menuItem(label='Applesed Website', parent='ms_menu')
    cmds.menuItem(label='Mayaseed Website', parent='ms_menu')

def deleteMenu():
    cmds.deleteUI('ms_menu')
