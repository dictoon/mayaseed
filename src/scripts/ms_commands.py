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
import os
import sys
import inspect

#****************************************************************************************************************************************************************************************************
# constant vars *************************************************************************************************************************************************************************************
#****************************************************************************************************************************************************************************************************

MAYASEED_VERSION = '0.1.4'
MAYASEED_URL = 'https://github.com/jonathantopf/mayaseed'
APPLESEED_URL = 'http://appleseedhq.net/'
ROOT_DIRECTORY = os.path.split((os.path.dirname(inspect.getfile(inspect.currentframe()))))[0]

#****************************************************************************************************************************************************************************************************
# utility functions *********************************************************************************************************************************************************************************
#****************************************************************************************************************************************************************************************************

#
# addMsShadingAttribs function ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
#    

def addShadingAttribs():
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
# removeMsShadingAttribs function -------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  

def removeShadingAttribs():
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

#
# show info dialogue -------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 

class MsInfoDial():
    def __init__(self):
        if cmds.window('ms_info_window', query=True, exists=True):
            cmds.deleteUI('ms_info_window')
        window = cmds.window('ms_info_window', title='Mayaseed info', sizeable=False)
        cmds.columnLayout(rs=10, columnOffset=['both', 20], width=600)
        cmds.rowLayout(numberOfColumns=2)
        cmds.text('', width=30)
        cmds.image(image=os.path.join(ROOT_DIRECTORY, 'graphics', 'mayaseed_graphic.png'))
        cmds.setParent('..')
        cmds.text('version: ' + MAYASEED_VERSION)
        cmds.text(open(os.path.join(ROOT_DIRECTORY, 'scripts', 'about.txt'),'r').read(), width=500, wordWrap=True, al='left')
        cmds.rowLayout(numberOfColumns=4)
        cmds.button( label='Mayaseed website', command=('import webbrowser\nwebbrowser.open_new_tab("http://www.jonathantopf.com/mayaseed/")'))
        cmds.button( label='appleseed website', command=('import webbrowser\nwebbrowser.open_new_tab("http://appleseedhq.net/")'))
        cmds.text('', width=166)
        cmds.button( label='Close', command=('import maya.cmds as cmds\ncmds.deleteUI(\"' + window + '\", window=True)'), width=100)
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=2)
        cmds.text('', width=478)
        cmds.text('jt')
        cmds.setParent('..')
        cmds.text('')
        cmds.showWindow(window)
        





