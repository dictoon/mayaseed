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
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import sys

kPluginNodeName = "ms_renderSettings"
kPluginNodeId = OpenMaya.MTypeId(0x00333)

class ms_renderSettings(OpenMayaMPx.MPxNode):

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

def nodeCreator():
    return OpenMayaMPx.asMPxPtr( ms_renderSettings() )

def nodeInitializer():

    #define attributes
    #export file settings -------------------------------------
    #output directory attribute
    output_dir_string = OpenMaya.MFnStringData().create("/")
    output_dir_Attr = OpenMaya.MFnTypedAttribute()
    ms_renderSettings.output_dir =  output_dir_Attr.create("output_directory", "out_dir", OpenMaya.MFnData.kString, output_dir_string)   
    #output file attribute
    output_file_string = OpenMaya.MFnStringData().create("output_file.appleseed")
    output_file_Attr = OpenMaya.MFnTypedAttribute()
    ms_renderSettings.output_file =  output_file_Attr.create("output_file", "out_file", OpenMaya.MFnData.kString, output_file_string)  

    #environent -----------------------------------------------
    environment_msgAttr = OpenMaya.MFnMessageAttribute()
    ms_renderSettings.environment = environment_msgAttr.create("environment", "env")   

    #cameras --------------------------------------------------
    #export all cameras bool attribute
    export_all_cameras_nAttr = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.export_all_cameras = export_all_cameras_nAttr.create("export_all_cameras", "export_all_cams", OpenMaya.MFnNumericData.kBoolean)
    #export all cameras as thin lens bool attribute
    export_all_cameras_as_thin_lens_nAttr = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.export_all_cameras_as_thin_lens = export_all_cameras_as_thin_lens_nAttr.create("export_all_cameras_as_thinlens", "export_thinlens", OpenMaya.MFnNumericData.kBoolean)
    #interpret sets as assemblies bool attribute
    interpret_sets_as_assemblies_nAttr = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.interpret_sets_as_assemblies = interpret_sets_as_assemblies_nAttr.create("interpret_sets_as_assemblies", "sets_as_assemblies", OpenMaya.MFnNumericData.kBoolean)
    #double sided shading bool attribute
    double_sided_shading_nAttr = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.double_sided_shading = double_sided_shading_nAttr.create("double_sided_shading", "double_shade", OpenMaya.MFnNumericData.kBoolean)
    
    #output ---------------------------------------------------
    #camera
    camera_msgAttr = OpenMaya.MFnMessageAttribute()
    ms_renderSettings.camera = camera_msgAttr.create("camera", "cam")
    #color space
    color_space_enumAttr = OpenMaya.MFnEnumAttribute()
    ms_renderSettings.color_space = color_space_enumAttr.create("color_space", "col_space")
    color_space_enumAttr.addField("sRGB", 0)
    color_space_enumAttr.addField("Linear RGB", 1)
    color_space_enumAttr.addField("Spectral", 2)
    color_space_enumAttr.addField("ciexyz", 3)

    #configurations -------------------------------------------
    #custom interactive config
    export_custom_interactive_config_nAttr = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.export_custom_interactive_config = export_custom_interactive_config_nAttr.create("export_custom_interactive_config", "export_interactive", OpenMaya.MFnNumericData.kBoolean)  
    #lighting engine
    custom_interactive_config_lghting_engine_enumAttr = OpenMaya.MFnEnumAttribute()
    ms_renderSettings.custom_interactive_config_lghting_engine = custom_interactive_config_lghting_engine_enumAttr.create("interactive_lighting_engine", "interactive_engine")
    custom_interactive_config_lghting_engine_enumAttr.addField("Path Tracing", 0)
    custom_interactive_config_lghting_engine_enumAttr.addField("Distributed Ray Tracing", 1)
    #min samples
    custom_interactive_config_min_samples_AttrInt = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.custom_interactive_config_min_samples = custom_interactive_config_min_samples_AttrInt.create("interactive_min_samples", "interactive_min_samples", OpenMaya.MFnNumericData.kInt, 1)
    custom_interactive_config_min_samples_AttrInt.setHidden(False)
    custom_interactive_config_min_samples_AttrInt.setKeyable(True)
    #max samples
    custom_interactive_config_max_samples_AttrInt = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.custom_interactive_config_max_samples = custom_interactive_config_max_samples_AttrInt.create("interactive_max_samples", "interactive_max_samples", OpenMaya.MFnNumericData.kInt, 4)
    custom_interactive_config_max_samples_AttrInt.setHidden(False)
    custom_interactive_config_max_samples_AttrInt.setKeyable(True)
    #max ray depth
    custom_interactive_config_max_ray_depth_AttrInt = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.custom_interactive_config_max_ray_depth = custom_interactive_config_max_ray_depth_AttrInt.create("interactive_max_ray_depth", "interactive_ray_depth", OpenMaya.MFnNumericData.kInt, 4)
    custom_interactive_config_max_ray_depth_AttrInt.setHidden(False)
    custom_interactive_config_max_ray_depth_AttrInt.setKeyable(True)
    #light samples
    custom_interactive_config_light_samples_AttrInt = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.custom_interactive_config_light_samples = custom_interactive_config_light_samples_AttrInt.create("interactive_light_samples", "interactive_light_samples", OpenMaya.MFnNumericData.kInt, 16)
    custom_interactive_config_light_samples_AttrInt.setHidden(False)
    custom_interactive_config_light_samples_AttrInt.setKeyable(True)

    #custom final config
    export_custom_final_config_nAttr = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.export_custom_final_config = export_custom_final_config_nAttr.create("export_custom_final_config", "export_final", OpenMaya.MFnNumericData.kBoolean)  
    #lighting engine
    custom_final_config_lghting_engine_enumAttr = OpenMaya.MFnEnumAttribute()
    ms_renderSettings.custom_final_config_lghting_engine = custom_final_config_lghting_engine_enumAttr.create("final_lighting_engine", "final_engine")
    custom_final_config_lghting_engine_enumAttr.addField("Path Tracing", 0)
    custom_final_config_lghting_engine_enumAttr.addField("Distributed Ray Tracing", 1)
    #min samples
    custom_final_config_min_samples_AttrInt = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.custom_final_config_min_samples = custom_final_config_min_samples_AttrInt.create("final_min_samples", "final_min_samples", OpenMaya.MFnNumericData.kInt, 1)
    custom_final_config_min_samples_AttrInt.setHidden(False)
    custom_final_config_min_samples_AttrInt.setKeyable(True)
    #max samples
    custom_final_config_max_samples_AttrInt = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.custom_final_config_max_samples = custom_final_config_max_samples_AttrInt.create("final_max_samples", "final_max_samples", OpenMaya.MFnNumericData.kInt, 4)
    custom_final_config_max_samples_AttrInt.setHidden(False)
    custom_final_config_max_samples_AttrInt.setKeyable(True)
    #max ray depth
    custom_final_config_max_ray_depth_AttrInt = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.custom_final_config_max_ray_depth = custom_final_config_max_ray_depth_AttrInt.create("final_max_ray_depth", "final_ray_depth", OpenMaya.MFnNumericData.kInt, 4)
    custom_final_config_max_ray_depth_AttrInt.setHidden(False)
    custom_final_config_max_ray_depth_AttrInt.setKeyable(True)
    #light samples
    custom_final_config_light_samples_AttrInt = OpenMaya.MFnNumericAttribute()
    ms_renderSettings.custom_final_config_light_samples = custom_final_config_light_samples_AttrInt.create("final_light_samples", "final_light_samples", OpenMaya.MFnNumericData.kInt, 16)
    custom_final_config_light_samples_AttrInt.setHidden(False)
    custom_final_config_light_samples_AttrInt.setKeyable(True)


    # add attributes
    try:
        ms_renderSettings.addAttribute(ms_renderSettings.output_dir)
        ms_renderSettings.addAttribute(ms_renderSettings.output_file)

        ms_renderSettings.addAttribute(ms_renderSettings.environment)

        ms_renderSettings.addAttribute(ms_renderSettings.export_all_cameras)
        ms_renderSettings.addAttribute(ms_renderSettings.export_all_cameras_as_thin_lens)

        ms_renderSettings.addAttribute(ms_renderSettings.interpret_sets_as_assemblies)
        ms_renderSettings.addAttribute(ms_renderSettings.double_sided_shading)
        ms_renderSettings.addAttribute(ms_renderSettings.camera)
        ms_renderSettings.addAttribute(ms_renderSettings.color_space)

        ms_renderSettings.addAttribute(ms_renderSettings.export_custom_interactive_config)
        ms_renderSettings.addAttribute(ms_renderSettings.custom_interactive_config_lghting_engine)
        ms_renderSettings.addAttribute(ms_renderSettings.custom_interactive_config_min_samples)
        ms_renderSettings.addAttribute(ms_renderSettings.custom_interactive_config_max_samples)
        ms_renderSettings.addAttribute(ms_renderSettings.custom_interactive_config_max_ray_depth)
        ms_renderSettings.addAttribute(ms_renderSettings.custom_interactive_config_light_samples)

        ms_renderSettings.addAttribute(ms_renderSettings.export_custom_final_config)
        ms_renderSettings.addAttribute(ms_renderSettings.custom_final_config_lghting_engine)
        ms_renderSettings.addAttribute(ms_renderSettings.custom_final_config_min_samples)
        ms_renderSettings.addAttribute(ms_renderSettings.custom_final_config_max_samples)
        ms_renderSettings.addAttribute(ms_renderSettings.custom_final_config_max_ray_depth)
        ms_renderSettings.addAttribute(ms_renderSettings.custom_final_config_light_samples)
    except:
        sys.stderr.write( "Failed to create attributes of %s node\n" % kPluginNodeName )


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "", "", "Any")
    try:
        mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer )
    except:
        sys.stderr.write( "Failed to register command: %s\n" % kPluginNodeName )
        raise

def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( kPluginNodeId )
    except:
        sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeName )
        raise