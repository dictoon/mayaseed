
#
# Copyright (c) 2012 Jonathan Topf
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

#

import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

# Plug-in information:
kPluginNodeName = 'ms_appleseed_material'
kPluginNodeClassify = 'shader/surface'
kPluginNodeId = OpenMaya.MTypeId(0x00334)

##########################################################
# Plug-in 
##########################################################
class appleseed_material(OpenMayaMPx.MPxNode):
    # Define the static variables to which we will assign the node's attributes
    # in nodeInitializer() defined below.
    surfacePointAttribute = OpenMaya.MObject()   
    outColorAttribute = OpenMaya.MObject()
    hardwareColorAttribute = OpenMaya.MObject()
    
    render_layerAttribute = OpenMaya.MObject()
    BSDF_frontAttribute = OpenMaya.MObject()
    EDF_frontAttribute = OpenMaya.MObject()
    surface_shader_frontAttribute = OpenMaya.MObject()
    alpha_mapAttribute = OpenMaya.MObject()
    normal_map_frontAttribute = OpenMaya.MObject()



    def __init__(self):
        ''' Constructor. '''
        OpenMayaMPx.MPxNode.__init__(self)
 
##########################################################
# Plug-in compute.
##########################################################

    def compute(self, pPlug, pDataBlock):

        if (( pPlug == appleseed_material.outColorAttribute ) or ( pPlug == appleseed_material.hardwareColorAttribute )):
            
            # Get the data handles corresponding to your attributes among the values in the data block.
            surfacePointDataHandle = pDataBlock.inputValue( appleseed_material.surfacePointAttribute )
            BSDF_frontDataHandle = pDataBlock.inputValue( appleseed_material.BSDF_frontAttribute )
            hardwareColorDataHandle = pDataBlock.inputValue( appleseed_material.hardwareColInAttribute )
            
            # Obtain the (x,y,z) location of the currently rendered point in camera coordinates.
            surfacePoint = surfacePointDataHandle.asFloatVector()
            
            # Get the BSDF_front and hardware Color values.
            BSDF_frontValue = BSDF_frontDataHandle.asFloatVector()
            hardwareValue = hardwareColorDataHandle.asFloatVector()

            outColor = OpenMaya.MFloatVector(0.5, 0.5, 0.5)
            hardwareColor = OpenMaya.MFloatVector(0.5, 0.5, 0.5)

            outColor.x = hardwareValue.x
            outColor.y = hardwareValue.y
            outColor.z = hardwareValue.z

            # Write to the output data.
            outColorDataHandle = pDataBlock.outputValue( appleseed_material.outColorAttribute )
            outColorDataHandle.setMFloatVector( outColor )
            outColorDataHandle.setClean()

            hardwareColorDataHandle = pDataBlock.outputValue( appleseed_material.hardwareColorAttribute )
            hardwareColorDataHandle.setMFloatVector( hardwareColor )
            hardwareColorDataHandle.setClean()

            # cmds.setAttr(+'.hardwareColor', 1,0,0)

        else:
            return OpenMaya.kUnknownParameter



##########################################################
# Plug-in initialization.
##########################################################
def nodeCreator():

    return OpenMayaMPx.asMPxPtr( appleseed_material() )

def nodeInitializer():

    # Create a numeric attribute function set, since our attributes will all be defined by numeric types.
    numericAttributeFn = OpenMaya.MFnNumericAttribute()
    
    #==================================
    # INPUT NODE ATTRIBUTE(S)
    #==================================
    # - The (x,y,z) point on the surface defined according to the camera's frame of reference.
    #   > (!) Important: the 'pointCamera' string relates to the samplerInfo maya node.
    #   > This value is supplied by the render sampler at computation time.
    appleseed_material.surfacePointAttribute = numericAttributeFn.createPoint('pointCamera', 'p')
    numericAttributeFn.setStorable(False)
    numericAttributeFn.setHidden(True)
    appleseed_material.addAttribute( appleseed_material.surfacePointAttribute )
    
    #render_layer Attribute
    #output directory attribute
    render_layer_string = OpenMaya.MFnStringData().create("default_render_layer")
    render_layer_Attr = OpenMaya.MFnTypedAttribute()
    appleseed_material.render_layer =  render_layer_Attr.create("render_layer", "render_layer", OpenMaya.MFnData.kString, render_layer_string)  
    appleseed_material.addAttribute( appleseed_material.render_layer )

    #duplicate front attributes on back
<<<<<<< HEAD:src/plugins/ms_appleseed_material.py
    duplcated_front_on_back_nAttr = OpenMaya.MFnNumericAttribute()
    appleseed_material.duplcated_front_on_back = duplcated_front_on_back_nAttr.create("duplcated_front_attributes_on_back", "duplcated_front_on_back", OpenMaya.MFnNumericData.kBoolean, True)
    appleseed_material.addAttribute( appleseed_material.duplcated_front_on_back )

    # front ***************************

=======
    duplicate_front_on_back_nAttr = OpenMaya.MFnNumericAttribute()
    appleseed_material.duplicate_front_on_back = duplicate_front_on_back_nAttr.create("duplicate_front_attributes_on_back", "duplicate_front_on_back", OpenMaya.MFnNumericData.kBoolean, True)
    appleseed_material.addAttribute( appleseed_material.duplicate_front_on_back )

    # front ***************************

    #enable front
    enable_front_nAttr = OpenMaya.MFnNumericAttribute()
    appleseed_material.enable_front = enable_front_nAttr.create("enable_front_material", "enable_front", OpenMaya.MFnNumericData.kBoolean, True)
    appleseed_material.addAttribute( appleseed_material.enable_front )

>>>>>>> ac1f639b5f3988137112ec105bbe8a20f891a1d4:plugins/ms_appleseed_material.py
    #BSDF_front Attribute
    appleseed_material.BSDF_frontAttribute = numericAttributeFn.createColor( 'BSDF_front_color', 'BSDF_front' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 0.0,0.0,0.0 )
    appleseed_material.addAttribute( appleseed_material.BSDF_frontAttribute )
    
    #EDF_front Attribute
    appleseed_material.EDF_frontAttribute = numericAttributeFn.createColor( 'EDF_front_color', 'EDF_front' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 0.0,0.0,0.0 )
    appleseed_material.addAttribute( appleseed_material.EDF_frontAttribute )
    
    #surface_shader_front Attribute
    appleseed_material.surface_shader_frontAttribute = numericAttributeFn.createColor( 'surface_shader_front_color', 'surface_shader_front' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 0.0,0.0,0.0 )
    appleseed_material.addAttribute( appleseed_material.surface_shader_frontAttribute )
    
    #normal_map_front Attribute
    appleseed_material.normal_map_frontAttribute = numericAttributeFn.createColor( 'normal_map_front_color', 'normal_map_front' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 0.0,0.0,0.0 )
    appleseed_material.addAttribute( appleseed_material.normal_map_frontAttribute )

    # back ***************************

<<<<<<< HEAD:src/plugins/ms_appleseed_material.py
=======
    #enable back
    enable_back_nAttr = OpenMaya.MFnNumericAttribute()
    appleseed_material.enable_back = enable_back_nAttr.create("enable_back_material", "enable_back", OpenMaya.MFnNumericData.kBoolean, True)
    appleseed_material.addAttribute( appleseed_material.enable_back )

>>>>>>> ac1f639b5f3988137112ec105bbe8a20f891a1d4:plugins/ms_appleseed_material.py
    #BSDF_back Attribute
    appleseed_material.BSDF_backAttribute = numericAttributeFn.createColor( 'BSDF_back_color', 'BSDF_back' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 0.0,0.0,0.0 )
    appleseed_material.addAttribute( appleseed_material.BSDF_backAttribute )
<<<<<<< HEAD:src/plugins/ms_appleseed_material.py
    
    #EDF_back Attribute
    appleseed_material.EDF_backAttribute = numericAttributeFn.createColor( 'EDF_back_color', 'EDF_back' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 0.0,0.0,0.0 )
    appleseed_material.addAttribute( appleseed_material.EDF_backAttribute )
    
    #surface_shader_back Attribute
    appleseed_material.surface_shader_backAttribute = numericAttributeFn.createColor( 'surface_shader_back_color', 'surface_shader_back' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 0.0,0.0,0.0 )
=======
    
    #EDF_back Attribute
    appleseed_material.EDF_backAttribute = numericAttributeFn.createColor( 'EDF_back_color', 'EDF_back' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 0.0,0.0,0.0 )
    appleseed_material.addAttribute( appleseed_material.EDF_backAttribute )
    
    #surface_shader_back Attribute
    appleseed_material.surface_shader_backAttribute = numericAttributeFn.createColor( 'surface_shader_back_color', 'surface_shader_back' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 0.0,0.0,0.0 )
>>>>>>> ac1f639b5f3988137112ec105bbe8a20f891a1d4:plugins/ms_appleseed_material.py
    appleseed_material.addAttribute( appleseed_material.surface_shader_backAttribute )
    
    #normal_map_back Attribute
    appleseed_material.normal_map_backAttribute = numericAttributeFn.createColor( 'normal_map_back_color', 'normal_map_back' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 0.0,0.0,0.0 )
    appleseed_material.addAttribute( appleseed_material.normal_map_backAttribute )



    #alpha_map Attribute
    appleseed_material.alpha_mapAttribute = numericAttributeFn.createColor( 'alpha_map_color', 'alpha_map' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 0.0,0.0,0.0 )
    appleseed_material.addAttribute( appleseed_material.alpha_mapAttribute )

    #hardware Color Attribute
    appleseed_material.hardwareColInAttribute = numericAttributeFn.createColor( 'hardware_color_in', 'hci' )
    numericAttributeFn.setStorable( True )
    numericAttributeFn.setDefault( 0.5,0.5,0.5 )
    appleseed_material.addAttribute( appleseed_material.hardwareColInAttribute )
    

    #==================================
    # OUTPUT NODE ATTRIBUTE(S)
    #==================================    
    # - The pixel color output.
    #   > This value is computed in our appleseed_material.compute() method, and should not be stored.
    appleseed_material.outColorAttribute = numericAttributeFn.createColor( 'outColor', 'oc')
    numericAttributeFn.setStorable( False )
    numericAttributeFn.setWritable( False )
    numericAttributeFn.setReadable( True )
    numericAttributeFn.setHidden( False )
    appleseed_material.addAttribute( appleseed_material.outColorAttribute )


    appleseed_material.hardwareColorAttribute = numericAttributeFn.createColor( 'hardwareColor', 'hc')
    numericAttributeFn.setStorable( False )
    numericAttributeFn.setWritable( False )
    numericAttributeFn.setReadable( True )
    numericAttributeFn.setHidden( False )
    appleseed_material.addAttribute( appleseed_material.hardwareColorAttribute )
    
    #==================================
    # NODE ATTRIBUTE DEPENDENCIES
    #==================================
    #  - All the input attributes affect the computation of the pixel color output (outColor).
    appleseed_material.attributeAffects( appleseed_material.BSDF_frontAttribute, appleseed_material.outColorAttribute )
    appleseed_material.attributeAffects( appleseed_material.BSDF_frontAttribute, appleseed_material.hardwareColorAttribute )
    appleseed_material.attributeAffects( appleseed_material.hardwareColInAttribute, appleseed_material.outColorAttribute )

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
