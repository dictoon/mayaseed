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
    # Define the static variables to which we will assign the node's attributes
    # in nodeInitializer() defined below.

    # #input
    # blend_weight                = OpenMaya.MObject()

    # scale_A                     = OpenMaya.MObject() 
    # scale_B                     = OpenMaya.MObject() 
    # rotate_A                    = OpenMaya.MObject() 
    # rotate_B                    = OpenMaya.MObject() 
    # translate_A                 = OpenMaya.MObject() 
    # translate_B                 = OpenMaya.MObject() 
    # shear_A                     = OpenMaya.MObject() 
    # shear_B                     = OpenMaya.MObject() 
    # rotatePivot_A               = OpenMaya.MObject() 
    # rotatePivot_B               = OpenMaya.MObject() 
    # rotatePivotTranslate_A      = OpenMaya.MObject() 
    # rotatePivotTranslate_B      = OpenMaya.MObject() 
    # scalePivot_A                = OpenMaya.MObject() 
    # scalePivot_B                = OpenMaya.MObject() 
    # scalePivotTranslate_A       = OpenMaya.MObject() 
    # scalePivotTranslate_B       = OpenMaya.MObject() 
    # rotateAxis_A                = OpenMaya.MObject() 
    # rotateAxis_B                = OpenMaya.MObject() 
    # transMinusRotatePivot_A     = OpenMaya.MObject() 
    # transMinusRotatePivot_B     = OpenMaya.MObject() 


    # #output
    # scale                       = OpenMaya.MObject() 
    # rotate                      = OpenMaya.MObject() 
    # translate                   = OpenMaya.MObject() 
    # shear                       = OpenMaya.MObject() 
    # rotatePivot                 = OpenMaya.MObject() 
    # rotatePivotTranslate        = OpenMaya.MObject() 
    # scalePivot                  = OpenMaya.MObject() 
    # scalePivotTranslate         = OpenMaya.MObject() 
    # rotateAxis                  = OpenMaya.MObject() 
    # transMinusRotatePivot       = OpenMaya.MObject() 


    def __init__(self):
        ''' Constructor. '''
        OpenMayaMPx.MPxNode.__init__(self)
 
##########################################################
# Plug-in compute.
##########################################################

    def compute(self, pPlug, pDataBlock):

        # Get the data handles corresponding to your attributes among the values in the data block.
        blend_weight_handle                = pDataBlock.inputValue( jt_mix_transform.blend_weight )

        scale_A_handle                     = pDataBlock.inputValue( jt_mix_transform.scale_A ) 
        scale_B_handle                     = pDataBlock.inputValue( jt_mix_transform.scale_B ) 
        rotate_A_handle                    = pDataBlock.inputValue( jt_mix_transform.rotate_A ) 
        rotate_B_handle                    = pDataBlock.inputValue( jt_mix_transform.rotate_B ) 
        translate_A_handle                 = pDataBlock.inputValue( jt_mix_transform.translate_A ) 
        translate_B_handle                 = pDataBlock.inputValue( jt_mix_transform.translate_B ) 
        shear_A_handle                     = pDataBlock.inputValue( jt_mix_transform.shear_A ) 
        shear_B_handle                     = pDataBlock.inputValue( jt_mix_transform.shear_B ) 
        rotatePivot_A_handle               = pDataBlock.inputValue( jt_mix_transform.rotatePivot_A ) 
        rotatePivot_B_handle               = pDataBlock.inputValue( jt_mix_transform.rotatePivot_B ) 
        rotatePivotTranslate_A_handle      = pDataBlock.inputValue( jt_mix_transform.rotatePivotTranslate_A ) 
        rotatePivotTranslate_B_handle      = pDataBlock.inputValue( jt_mix_transform.rotatePivotTranslate_B ) 
        scalePivot_A_handle                = pDataBlock.inputValue( jt_mix_transform.scalePivot_A ) 
        scalePivot_B_handle                = pDataBlock.inputValue( jt_mix_transform.scalePivot_B ) 
        scalePivotTranslate_A_handle       = pDataBlock.inputValue( jt_mix_transform.scalePivotTranslate_A ) 
        scalePivotTranslate_B_handle       = pDataBlock.inputValue( jt_mix_transform.scalePivotTranslate_B ) 
        rotateAxis_A_handle                = pDataBlock.inputValue( jt_mix_transform.rotateAxis_A ) 
        rotateAxis_B_handle                = pDataBlock.inputValue( jt_mix_transform.rotateAxis_B ) 
        transMinusRotatePivot_A_handle     = pDataBlock.inputValue( jt_mix_transform.transMinusRotatePivot_A ) 
        transMinusRotatePivot_B_handle     = pDataBlock.inputValue( jt_mix_transform.transMinusRotatePivot_B ) 

        # get the values from the datablocks
        blend_weight_value                = blend_weight_handle.asFloat()

        scale_A_value                     = scale_A_handle.asVector() 
        scale_B_value                     = scale_B_handle.asVector() 
        rotate_A_value                    = rotate_A_handle.asVector() 
        rotate_B_value                    = rotate_B_handle.asVector() 
        translate_A_value                 = translate_A_handle.asVector() 
        translate_B_value                 = translate_B_handle.asVector() 
        shear_A_value                     = shear_A_handle.asVector() 
        shear_B_value                     = shear_B_handle.asVector() 
        rotatePivot_A_value               = rotatePivot_A_handle.asVector() 
        rotatePivot_B_value               = rotatePivot_B_handle.asVector() 
        rotatePivotTranslate_A_value      = rotatePivotTranslate_A_handle.asVector() 
        rotatePivotTranslate_B_value      = rotatePivotTranslate_B_handle.asVector() 
        scalePivot_A_value                = scalePivot_A_handle.asVector() 
        scalePivot_B_value                = scalePivot_B_handle.asVector() 
        scalePivotTranslate_A_value       = scalePivotTranslate_A_handle.asVector() 
        scalePivotTranslate_B_value       = scalePivotTranslate_B_handle.asVector() 
        rotateAxis_A_value                = rotateAxis_A_handle.asVector() 
        rotateAxis_B_value                = rotateAxis_B_handle.asVector() 
        transMinusRotatePivot_A_value     = transMinusRotatePivot_A_handle.asVector() 
        transMinusRotatePivot_B_value     = transMinusRotatePivot_B_handle.asVector() 

        # create vars to work with the output attribs
        blend_weight_inverse_value      = 1.0 - blend_weight_value

        # quick function to blend two MVectors/tuples and return an mVector
        def blendValues(attr_A, attr_B):
            x = ((attr_A[0] * blend_weight_value) + (attr_B[0] * blend_weight_inverse_value)) 
            y = ((attr_A[1] * blend_weight_value) + (attr_B[1] * blend_weight_inverse_value))
            z = ((attr_A[2] * blend_weight_value) + (attr_B[2] * blend_weight_inverse_value))
            return OpenMaya.MVector( x, y, z)

        #calculate output values
        scale_var                   = blendValues(scale_A_value, scale_B_value)
        rotate_var                  = blendValues(rotate_A_value, rotate_B_value)
        translate_var               = blendValues(translate_A_value, translate_B_value)
        shear_var                   = blendValues(shear_A_value, shear_B_value)
        rotatePivot_var             = blendValues(rotatePivot_A_value, rotatePivot_B_value)
        rotatePivotTranslate_var    = blendValues(rotatePivotTranslate_A_value, rotatePivotTranslate_B_value)
        scalePivot_var              = blendValues(scalePivot_A_value, scalePivot_B_value)
        scalePivotTranslate_var     = blendValues(scalePivotTranslate_A_value, scalePivotTranslate_B_value)
        rotateAxis_var              = blendValues(rotateAxis_A_value, rotateAxis_B_value)
        transMinusRotatePivot_var   = blendValues(transMinusRotatePivot_A_value, transMinusRotatePivot_B_value)

        # createPoint output data handles

        scale_data_handle                       = pDataBlock.outputValue( jt_mix_transform.scale )
        rotate_data_handle                      = pDataBlock.outputValue( jt_mix_transform.rotate ) 
        translate_data_handle                   = pDataBlock.outputValue( jt_mix_transform.translate ) 
        shear_data_handle                       = pDataBlock.outputValue( jt_mix_transform.shear ) 
        rotatePivot_data_handle                 = pDataBlock.outputValue( jt_mix_transform.rotatePivot ) 
        rotatePivotTranslate_data_handle        = pDataBlock.outputValue( jt_mix_transform.rotatePivotTranslate ) 
        scalePivot_data_handle                  = pDataBlock.outputValue( jt_mix_transform.scalePivot ) 
        scalePivotTranslate_data_handle         = pDataBlock.outputValue( jt_mix_transform.scalePivotTranslate ) 
        rotateAxis_data_handle                  = pDataBlock.outputValue( jt_mix_transform.rotateAxis ) 
        transMinusRotatePivot_data_handle       = pDataBlock.outputValue( jt_mix_transform.transMinusRotatePivot )

        # assign them the corrcet values

        scale_data_handle.setMVector( scale_var )
        rotate_data_handle.setMVector( rotate_var )
        translate_data_handle.setMVector( translate_var )
        shear_data_handle.setMVector( shear_var ) 
        rotatePivot_data_handle.setMVector( rotatePivot_var )
        rotatePivotTranslate_data_handle.setMVector( rotatePivotTranslate_var )
        scalePivot_data_handle.setMVector( scalePivot_var )
        scalePivotTranslate_data_handle.setMVector( scalePivotTranslate_var )
        rotateAxis_data_handle.setMVector( rotateAxis_var )
        transMinusRotatePivot_data_handle.setMVector( transMinusRotatePivot_var )

        # set the date handles clean

        scale_data_handle.setClean()
        rotate_data_handle.setClean()
        translate_data_handle.setClean()
        shear_data_handle.setClean() 
        rotatePivot_data_handle.setClean()
        rotatePivotTranslate_data_handle.setClean()
        scalePivot_data_handle.setClean()
        scalePivotTranslate_data_handle.setClean()
        rotateAxis_data_handle.setClean()
        transMinusRotatePivot_data_handle.setClean()


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

    #scale A
    jt_mix_transform.scale_A = numericAttributeFn.createPoint( 'scale_A', 'scale_A' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.scale_A )

    #scale B
    jt_mix_transform.scale_B = numericAttributeFn.createPoint( 'scale_B', 'scale_B' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.scale_B )

    #rotate A
    jt_mix_transform.rotate_A = numericAttributeFn.createPoint( 'rotate_A', 'rotate_A' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.rotate_A )

    #rotate B
    jt_mix_transform.rotate_B = numericAttributeFn.createPoint( 'rotate_B', 'rotate_B' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.rotate_B )

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

    #shear A
    jt_mix_transform.shear_A = numericAttributeFn.createPoint( 'shear_A', 'shear_A' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.shear_A )

    #shear B
    jt_mix_transform.shear_B = numericAttributeFn.createPoint( 'shear_B', 'shear_B' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.shear_B )

    #rotatePivot A
    jt_mix_transform.rotatePivot_A = numericAttributeFn.createPoint( 'rotatePivot_A', 'rotatePivot_A' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.rotatePivot_A )

    #rotatePivot B
    jt_mix_transform.rotatePivot_B = numericAttributeFn.createPoint( 'rotatePivot_B', 'rotatePivot_B' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.rotatePivot_B )

    #rotatePivotTranslate A
    jt_mix_transform.rotatePivotTranslate_A = numericAttributeFn.createPoint( 'rotatePivotTranslate_A', 'rotatePivotTranslate_A' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.rotatePivotTranslate_A )

    #rotatePivotTranslate B
    jt_mix_transform.rotatePivotTranslate_B = numericAttributeFn.createPoint( 'rotatePivotTranslate_B', 'rotatePivotTranslate_B' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.rotatePivotTranslate_B )

    #scalePivot A
    jt_mix_transform.scalePivot_A = numericAttributeFn.createPoint( 'scalePivot_A', 'scalePivot_A' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.scalePivot_A )

    #scalePivot B
    jt_mix_transform.scalePivot_B = numericAttributeFn.createPoint( 'scalePivot_B', 'scalePivot_B' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.scalePivot_B )

    #scalePivotTranslate A
    jt_mix_transform.scalePivotTranslate_A = numericAttributeFn.createPoint( 'scalePivotTranslate_A', 'scalePivotTranslate_A' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.scalePivotTranslate_A )

    #scalePivotTranslate B
    jt_mix_transform.scalePivotTranslate_B = numericAttributeFn.createPoint( 'scalePivotTranslate_B', 'scalePivotTranslate_B' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.scalePivotTranslate_B )

    #rotateAxis A
    jt_mix_transform.rotateAxis_A = numericAttributeFn.createPoint( 'rotateAxis_A', 'rotateAxis_A' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.rotateAxis_A )

    #rotateAxis B
    jt_mix_transform.rotateAxis_B = numericAttributeFn.createPoint( 'rotateAxis_B', 'rotateAxis_B' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.rotateAxis_B )

    #transMinusRotatePivot A
    jt_mix_transform.transMinusRotatePivot_A = numericAttributeFn.createPoint( 'transMinusRotatePivot_A', 'transMinusRotatePivot_A' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.transMinusRotatePivot_A )

    #transMinusRotatePivot B
    jt_mix_transform.transMinusRotatePivot_B = numericAttributeFn.createPoint( 'transMinusRotatePivot_B', 'transMinusRotatePivot_B' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.transMinusRotatePivot_B )


    #==================================
    # OUTPUT NODE ATTRIBUTE(S)
    #==================================

    #scale
    jt_mix_transform.scale = numericAttributeFn.createPoint( 'scale', 'scale' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.scale )

    #rotate
    jt_mix_transform.rotate = numericAttributeFn.createPoint( 'rotate', 'rotate' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.rotate )

    #translate
    jt_mix_transform.translate = numericAttributeFn.createPoint( 'translate', 'translate' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.translate )

    #shear
    jt_mix_transform.shear = numericAttributeFn.createPoint( 'shear', 'shear' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.shear )

    #rotatePivot
    jt_mix_transform.rotatePivot = numericAttributeFn.createPoint( 'rotatePivot', 'rotatePivot' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.rotatePivot )

    #rotatePivotTranslate
    jt_mix_transform.rotatePivotTranslate = numericAttributeFn.createPoint( 'rotatePivotTranslate', 'rotatePivotTranslate' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.rotatePivotTranslate )

    #scalePivot
    jt_mix_transform.scalePivot = numericAttributeFn.createPoint( 'scalePivot', 'scalePivot' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.scalePivot )

    #scalePivotTranslate
    jt_mix_transform.scalePivotTranslate = numericAttributeFn.createPoint( 'scalePivotTranslate', 'scalePivotTranslate' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.scalePivotTranslate )

    #rotateAxis
    jt_mix_transform.rotateAxis = numericAttributeFn.createPoint( 'rotateAxis', 'rotateAxis' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.rotateAxis )

    #transMinusRotatePivot
    jt_mix_transform.transMinusRotatePivot = numericAttributeFn.createPoint( 'transMinusRotatePivot', 'transMinusRotatePivot' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 1.0,1.0,1.0 )
    jt_mix_transform.addAttribute( jt_mix_transform.transMinusRotatePivot )


    # set which attributes effect what, all attributes effects all attributes in this case
    jt_mix_transform.attributeAffects( jt_mix_transform.scale_A, jt_mix_transform.scale )
    jt_mix_transform.attributeAffects( jt_mix_transform.scale_B, jt_mix_transform.scale )

    jt_mix_transform.attributeAffects( jt_mix_transform.rotate_A, jt_mix_transform.rotate )
    jt_mix_transform.attributeAffects( jt_mix_transform.rotate_B, jt_mix_transform.rotate )

    jt_mix_transform.attributeAffects( jt_mix_transform.translate_A, jt_mix_transform.translate )
    jt_mix_transform.attributeAffects( jt_mix_transform.translate_B, jt_mix_transform.translate )

    jt_mix_transform.attributeAffects( jt_mix_transform.shear_A, jt_mix_transform.shear )
    jt_mix_transform.attributeAffects( jt_mix_transform.shear_B, jt_mix_transform.shear )

    jt_mix_transform.attributeAffects( jt_mix_transform.rotatePivot_A, jt_mix_transform.rotatePivot )
    jt_mix_transform.attributeAffects( jt_mix_transform.rotatePivot_B, jt_mix_transform.rotatePivot )

    jt_mix_transform.attributeAffects( jt_mix_transform.rotatePivotTranslate_A, jt_mix_transform.rotatePivotTranslate )
    jt_mix_transform.attributeAffects( jt_mix_transform.rotatePivotTranslate_B, jt_mix_transform.rotatePivotTranslate )

    jt_mix_transform.attributeAffects( jt_mix_transform.scalePivot_A, jt_mix_transform.scalePivot )
    jt_mix_transform.attributeAffects( jt_mix_transform.scalePivot_B, jt_mix_transform.scalePivot )

    jt_mix_transform.attributeAffects( jt_mix_transform.scalePivotTranslate_A, jt_mix_transform.scalePivotTranslate )
    jt_mix_transform.attributeAffects( jt_mix_transform.scalePivotTranslate_B, jt_mix_transform.scalePivotTranslate )

    jt_mix_transform.attributeAffects( jt_mix_transform.rotateAxis_A, jt_mix_transform.rotateAxis )
    jt_mix_transform.attributeAffects( jt_mix_transform.rotateAxis_B, jt_mix_transform.rotateAxis )

    jt_mix_transform.attributeAffects( jt_mix_transform.transMinusRotatePivot_A, jt_mix_transform.transMinusRotatePivot )
    jt_mix_transform.attributeAffects( jt_mix_transform.transMinusRotatePivot_B, jt_mix_transform.transMinusRotatePivot )

    jt_mix_transform.attributeAffects( jt_mix_transform.blend_weight, jt_mix_transform.scale )
    jt_mix_transform.attributeAffects( jt_mix_transform.blend_weight, jt_mix_transform.rotate )
    jt_mix_transform.attributeAffects( jt_mix_transform.blend_weight, jt_mix_transform.translate )
    jt_mix_transform.attributeAffects( jt_mix_transform.blend_weight, jt_mix_transform.rotatePivot )
    jt_mix_transform.attributeAffects( jt_mix_transform.blend_weight, jt_mix_transform.rotatePivotTranslate )
    jt_mix_transform.attributeAffects( jt_mix_transform.blend_weight, jt_mix_transform.scalePivot )
    jt_mix_transform.attributeAffects( jt_mix_transform.blend_weight, jt_mix_transform.scalePivotTranslate )
    jt_mix_transform.attributeAffects( jt_mix_transform.blend_weight, jt_mix_transform.rotateAxis )
    jt_mix_transform.attributeAffects( jt_mix_transform.blend_weight, jt_mix_transform.transMinusRotatePivot )


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

