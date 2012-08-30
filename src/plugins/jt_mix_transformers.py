#!/usr/bin/python

#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2010-2012 Francois Beaune
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

# Plug-in information:
kPluginNodeName = 'jt_mix_transform'
kPluginNodeClassify = 'utility'
kPluginNodeId = OpenMaya.MTypeId(0x00434)

##########################################################
# Plug-in 
##########################################################

class jt_mix_transform(OpenMayaMPx.MPxNode):
    def __init__(self):
        ''' Constructor. '''
        OpenMayaMPx.MPxNode.__init__(self)
 
##########################################################
# Plug-in compute.
##########################################################

    def compute(self, pPlug, pDataBlock):

        # Get the data handles corresponding to your attributes among the values in the data block.
        blend_weight_handle = pDataBlock.inputValue( jt_mix_transform.blend_weight )
        translate_A_handle = pDataBlock.inputValue( jt_mix_transform.translate_A ) 
        translate_B_handle = pDataBlock.inputValue( jt_mix_transform.translate_B ) 
 

        # get the values from the datablocks
        blend_weight_value = blend_weight_handle.asFloat()
        translate_A_value = translate_A_handle.asFloat3() 
        translate_B_value = translate_B_handle.asFloat3() 


        print 'blend weight', blend_weight_value
        print 'a', translate_A_value
        print 'b', translate_B_value




##########################################################
# Plug-in initialization.
##########################################################
def nodeCreator():

    return OpenMayaMPx.asMPxPtr( jt_mix_transform() )

def nodeInitializer():

    # Create a numeric attribute function set, since our attributes will all be defined by numeric types.
    numericAttributeFn = OpenMaya.MFnNumericAttribute()
    
    #==================================
    # INPUT NODE ATTRIBUTE(S)
    #==================================

    #blend weight
    jt_mix_transform.blend_weight = numericAttributeFn.create( 'blend_weight', 'blend', OpenMaya.MFnNumericData.kFloat, 0.5)
    numericAttributeFn.setHidden(False)
    numericAttributeFn.setKeyable(True)
    jt_mix_transform.addAttribute( jt_mix_transform.blend_weight )

    #translate A
    jt_mix_transform.translate_A = numericAttributeFn.createPoint( 'translate_A', 'translate_A' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.translate_A )

    #translate B
    jt_mix_transform.translate_B = numericAttributeFn.createPoint( 'translate_B', 'translate_B' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.translate_B )


    #==================================
    # OUTPUT NODE ATTRIBUTE(S)
    #==================================

    #translate
    jt_mix_transform.translate = numericAttributeFn.createPoint( 'translate', 'translate' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.translate )


    # set which attributes effect what, all attributes effects all attributes in this case
    jt_mix_transform.attributeAffects( jt_mix_transform.translate_A, jt_mix_transform.translate )
    jt_mix_transform.attributeAffects( jt_mix_transform.translate_B, jt_mix_transform.translate )
    jt_mix_transform.attributeAffects( jt_mix_transform.blend_weight, jt_mix_transform.translate )



def initializePlugin( mobject ):
    ''' Initializes the plug-in. '''
    mplugin = OpenMayaMPx.MFnPlugin( mobject )
    try:
        mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, 
                    nodeInitializer, OpenMayaMPx.MPxNode.kDependNode, kPluginNodeClassify )
    except:
        sys.stderr.write( "Failed to register node: " + kPluginNodeName )
        raise

def uninitializePlugin( mobject ):
    ''' Unitializes the plug-in. '''
    mplugin = OpenMayaMPx.MFnPlugin( mobject )
    try:
        mplugin.deregisterNode( kPluginNodeId )
    except:
        sys.stderr.write( "Failed to deregister node: " + kPluginNodeName )
        raise

