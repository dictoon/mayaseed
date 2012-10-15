
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


import maya.cmds as cmds
import maya.mel as mel 
import maya.utils as mu
import os
import time
import re
import subprocess
import sys
import ms_commands
import ms_export_obj
import time

inch_to_meter = 0.02539999983236


#--------------------------------------------------------------------------------------------------
# WriteXml class.
#--------------------------------------------------------------------------------------------------

class WriteXml():
    spaces_per_indentation_level = 4

    def __init__(self, file_path):
        self.indentation_level = 0
        self.file_object = None
        try:
            self.file_object = open(file_path, 'w')
        except IOError:
            cmds.error("IO error: failed to open {0} for writing.".format(file_path))

    def start_element(self, str):
        self.append_line("<" + str + ">")
        self.indentation_level += 1
        
    def end_element(self, str):
        self.indentation_level -= 1
        self.append_line("</" + str + ">")
        
    def append_element(self, str):
        self.append_line("<" + str + "/>")

    def append_parameter(self, name, value):
        self.append_line('<parameter name="{0}" value="{1}" />'.format(name, value))

    def append_line(self, str):
        self.file_object.write(self.indentation_string() + str + "\n")

    def close(self):
        self.file_object.close()

    def indentation_string(self):
        return (self.indentation_level * self.spaces_per_indentation_level) * " "


#--------------------------------------------------------------------------------------------------
# check_export_cancelled function.
#--------------------------------------------------------------------------------------------------

def check_export_cancelled():
    if cmds.progressWindow(query=True, isCancelled=True):
        cmds.progressWindow(endProgress=1)
        raise RuntimeError('Export Cancelled.')


#--------------------------------------------------------------------------------------------------
# write_transform function.
#--------------------------------------------------------------------------------------------------

def write_transform(doc, scale, object=False, motion=False, motion_samples=2):
    if motion:
        sample_interval = 1.0 / (motion_samples - 1)

        start_time = cmds.currentTime(query=True)
        cmds.select(object)

        for i in range(motion_samples):
            cmds.currentTime(start_time + sample_interval * i)
            cmds.refresh()
            write_single_transform(doc, object, i, scale)

        cmds.currentTime(start_time)
        cmds.select(cl=True)
    else:
        write_single_transform(doc, object, 0, scale)

def write_single_transform(doc, object, time, scale):
    doc.start_element('transform time="{0}"'.format(time))

    if scale != 1.0:
        doc.append_element('scaling value="{0}"'.format(scale))

    if object:
        m = cmds.xform(object, query=True, ws=True, matrix=True)

        doc.start_element('matrix')
        doc.append_line('{0:.15f} {1:.15f} {2:.15f} {3:.15f}'.format(m[0], m[4], m[ 8], m[12]))
        doc.append_line('{0:.15f} {1:.15f} {2:.15f} {3:.15f}'.format(m[1], m[5], m[ 9], m[13]))
        doc.append_line('{0:.15f} {1:.15f} {2:.15f} {3:.15f}'.format(m[2], m[6], m[10], m[14]))
        doc.append_line('{0:.15f} {1:.15f} {2:.15f} {3:.15f}'.format(m[3], m[7], m[11], m[15]))
        doc.end_element('matrix')

    doc.end_element('transform')


#--------------------------------------------------------------------------------------------------
# get_maya_params function.
#--------------------------------------------------------------------------------------------------

def get_maya_params(render_settings_node):
    print("Retrieving settings from UI...")

    params = {}

    params['entityDefs'] = ms_commands.getEntityDefs(os.path.join(ms_commands.ROOT_DIRECTORY, 'scripts', 'appleseedEntityDefs.xml'))

    # Main settings.
    params['output_directory'] = cmds.getAttr(render_settings_node + '.output_directory')
    params['file_name'] = cmds.getAttr(render_settings_node + '.output_file')
    params['convertShadingNodes'] = cmds.getAttr(render_settings_node + '.convert_shading_nodes_to_textures')
    params['convertTexturesToExr'] = cmds.getAttr(render_settings_node + '.convert_textures_to_exr')
    params['overwrite_existing_textures'] = cmds.getAttr(render_settings_node + '.overwrite_existing_textures')
    params['export_camera_blur'] = cmds.getAttr(render_settings_node + '.export_camera_blur')
    params['exportMayaLights'] = cmds.getAttr(render_settings_node + '.export_maya_lights')
    params['export_transformation_blur'] = cmds.getAttr(render_settings_node + '.export_transformation_blur')
    params['export_deformation_blur'] = cmds.getAttr(render_settings_node + '.export_deformation_blur')
    params['motion_samples'] = cmds.getAttr(render_settings_node + '.motion_samples')
    params['export_animation'] = cmds.getAttr(render_settings_node + '.export_animation')
    params['animation_start_frame'] = cmds.getAttr(render_settings_node + '.animation_start_frame')
    params['animation_end_frame'] = cmds.getAttr(render_settings_node + '.animation_end_frame')
    params['animatedTextures'] = cmds.getAttr(render_settings_node + '.export_animated_textures')
    params['scene_scale'] = 1.0

    if params['motion_samples'] < 2:
        cmds.warning('Motion samples must be >= 2, using 2.')
        params['motion_samples'] = 2

    # Advanced options.
    if cmds.listConnections(render_settings_node + '.environment'):
        params['environment'] = cmds.listRelatives(cmds.listConnections(render_settings_node + '.environment')[0])[0]
    else:
        params['environment'] = False

    # Cameras.
    # params['sceneCameraExportAllCameras'] = cmds.checkBox('ms_sceneCameraExportAllCameras', query=True, value=True)
    params['sceneCameraDefaultThinLens'] = cmds.getAttr(render_settings_node + '.export_all_cameras_as_thinlens')
    
    # Materials.
    params['matLambertBSDF'] = 'Lambertian'
    params['matLambertEDF'] = 'None'
    params['matLambertSurfaceShader'] = 'Physical'
    params['matBlinnBSDF'] = 'Ashikhmin-Shirley'
    params['matBlinnEDF'] = 'None'
    params['matBlinnSurfaceShader'] = 'Physical'
    params['matPhongBSDF'] = 'Ashikhmin-Shirley'
    params['matPhongEDF'] = 'None'
    params['matPhongSurfaceShader'] = 'Physical'
    params['matSurfaceShaderBSDF'] = 'Lambertian'
    params['matSurfaceShaderEDF'] = 'Diffuse'
    params['matSurfaceShaderSurfaceShader'] = 'Physical'
    params['matDefaultBSDF'] = 'Lambertian'
    params['matDefaultEDF'] = 'None'
    params['matDefaultSurfaceShader'] = 'Physical'

    # Output.
    if cmds.listConnections(render_settings_node + '.camera'):
        params['outputCamera'] = cmds.listConnections(render_settings_node + '.camera')[0]
    else:
        cmds.warning("No camera connected to {0}, using \"persp\".".format(render_settings_node))
        params['outputCamera'] = 'persp'

    if cmds.getAttr(render_settings_node + '.color_space') == 1:
        params['outputColorSpace'] = 'linear_rgb'
    elif cmds.getAttr(render_settings_node + '.color_space') == 2:
        params['outputColorSpace'] = 'spectral'
    elif cmds.getAttr(render_settings_node + '.color_space') == 3:
        params['outputColorSpace'] = 'ciexyz'
    else:
        params['outputColorSpace'] = 'srgb'

    params['output_res_width'] = cmds.getAttr(render_settings_node + '.width')
    params['output_res_height'] = cmds.getAttr(render_settings_node + '.height')

    # Custom final configuration.

    params['customFinalConfigCheck'] = cmds.getAttr(render_settings_node + '.export_custom_final_config')
    params['customFinalConfigEngine'] = cmds.getAttr(render_settings_node + '.final_lighting_engine')

    params['drtDLBSDFSamples'] = cmds.getAttr(render_settings_node + '.drt_dl_bsdf_samples')
    params['drtDLLightSamples'] = cmds.getAttr(render_settings_node + '.drt_dl_light_samples')
    params['drtEnableIBL'] = cmds.getAttr(render_settings_node + '.drt_enable_ibl')
    params['drtIBLBSDFSamples'] = cmds.getAttr(render_settings_node + '.drt_ibl_bsdf_samples')
    params['drtIBLEnvSamples'] = cmds.getAttr(render_settings_node + '.drt_ibl_env_samples')
    params['drtMaxPathLength'] = cmds.getAttr(render_settings_node + '.drt_max_path_length')
    params['drtRRMinPathLength'] = cmds.getAttr(render_settings_node + '.drt_rr_min_path_length')

    params['ptDLLightSamples'] = cmds.getAttr(render_settings_node + '.pt_dl_light_samples')
    params['ptEnableCaustics'] = cmds.getAttr(render_settings_node + '.pt_enable_caustics')
    params['ptEnableDL'] = cmds.getAttr(render_settings_node + '.pt_enable_dl')
    params['ptEnableIBL'] = cmds.getAttr(render_settings_node + '.pt_enable_ibl')
    params['ptIBLBSDFSamples'] = cmds.getAttr(render_settings_node + '.pt_ibl_bsdf_samples')
    params['ptIBLEnvSamples'] = cmds.getAttr(render_settings_node + '.pt_ibl_env_samples')
    params['ptMaxPathLength'] = cmds.getAttr(render_settings_node + '.pt_max_path_length')
    params['ptNextEventEstimation'] = cmds.getAttr(render_settings_node + '.pt_next_event_estimation')
    params['ptRRMinPathLength'] = cmds.getAttr(render_settings_node + '.pt_rr_min_path_length')

    params['gtrFilterSize'] = cmds.getAttr(render_settings_node + '.gtr_filter_size')
    params['gtrMinSamples'] = cmds.getAttr(render_settings_node + '.gtr_min_samples')
    params['gtrMaxSamples'] = cmds.getAttr(render_settings_node + '.gtr_max_samples')
    params['gtrMaxContrast'] = cmds.getAttr(render_settings_node + '.gtr_max_contrast')
    params['gtrMaxVariation'] = cmds.getAttr(render_settings_node + '.gtr_max_variation')

    if cmds.getAttr(render_settings_node + '.gtr_sampler') == 0:
        params['gtrSampler'] = 'uniform'
    else:
        params['gtrSampler'] = 'adaptive'

    # Select obj exporter.
    if cmds.pluginInfo('ms_export_obj_' + str(int(mel.eval('getApplicationVersionAsFloat()'))), query=True, r=True):
        params['obj_exporter'] = ms_commands.export_obj
    else:
        cmds.warning("No native obj exporter found, exporting using Python obj exporter.")
        params['obj_exporter'] = ms_export_obj.export

    params['verbose_output'] = cmds.getAttr(render_settings_node + '.verbose_output')
    return params


#--------------------------------------------------------------------------------------------------
# get_maya_scene function.
#--------------------------------------------------------------------------------------------------

def get_maya_scene(params):
    
    """ Parses the maya scene and returns a list of root transforms with the relevant children """

    print("Caching Maya scene data...")

    start_time = cmds.currentTime(query=True)

    # the maya scene is stored as a list of root transforms that contain mesh's/geometry/lights as children
    maya_root_transforms = []

    # find all root transforms and create Mtransforms from them
    for maya_transform in cmds.ls(tr=True, long=True):
        if not cmds.listRelatives(maya_transform, ap=True, fullPath=True):
            maya_root_transforms.append(MTransform(params, maya_transform, None))

    start_time = cmds.currentTime(query=True)
    start_frame = int(start_time)
    end_frame = start_frame
    sample_increment = 1.0 / (params['motion_samples'] - 1)

    if params['export_animation']:
        start_frame = params['animation_start_frame']
        end_frame = params['animation_end_frame']

    if params['export_transformation_blur'] or params['export_deformation_blur'] or params['export_camera_blur']:
        end_frame += 1

    # compute the base output directory
    scene_filepath = cmds.file(q=True, sceneName=True)
    scene_basename = os.path.splitext(os.path.basename(scene_filepath))[0]
    if len(scene_basename) == 0:
        scene_basename = "Untitled"
    project_directory = cmds.workspace(q=True, rd=True)
    params['output_directory'] = params['output_directory'].replace("<ProjectDir>", project_directory)
    params['output_directory'] = params['output_directory'].replace("<SceneName>", scene_basename)

    texture_dir = ms_commands.create_dir(os.path.join(params['output_directory'], 'textures'))

    # add motion samples
    current_frame = start_frame

    while current_frame <= end_frame:
        cmds.currentTime(current_frame)
        rounded_time = '%.6f' % current_frame

        # create frame output directories
        frame_dir = ms_commands.create_dir(os.path.join(params['output_directory'], rounded_time))
        geo_dir = ms_commands.create_dir(os.path.join(frame_dir, 'geometry'))

        if params['export_transformation_blur'] or (current_frame == start_frame):
            print("Adding transform samples, frame {0}...".format(current_frame))
            for transform in maya_root_transforms:
                transform.add_transform_sample()
                for descendant_transform in transform.descendant_transforms:
                    descendant_transform.add_transform_sample()

        if params['export_deformation_blur'] or (current_frame == start_frame):
            print("Adding deformation samples, frame {0}...".format(current_frame))
            for transform in maya_root_transforms:
                for mesh in (transform.descendant_meshes + transform.child_meshes):
                    mesh.add_deform_sample(geo_dir, current_frame)

        if params['export_camera_blur'] or (current_frame == start_frame):
            print("Adding camera transformation samples, frame {0}...".format(current_frame))
            for transform in maya_root_transforms:
                for camera in (transform.descendant_cameras + transform.child_cameras):
                    camera.add_matrix_sample()

        # output textures
        for transform in maya_root_transforms:
            for mesh in (transform.child_meshes + transform.descendant_meshes):
                for material in mesh.materials:
                    for texture in material.textures:
                        # if its the first frame of the animation force a sample
                        # otherwise only add samples for animated textures
                        if texture.is_animated or (current_frame == start_frame):
                            texture.add_image_sample(texture_dir, current_frame)

        current_frame += sample_increment

        # add code to export textures here    

    # return to pre-export time
    cmds.currentTime(start_time)

    return maya_root_transforms


#--------------------------------------------------------------------------------------------------
# MTransform class.
#--------------------------------------------------------------------------------------------------

class MTransform():

    """ Lightweight class representing info for a Maya transform node """

    def __init__(self, params, maya_transform_name, parent):
        self.params = params
        if self.params['verbose_output']:
            print("Creating MTransform {0}...".format(maya_transform_name))
        self.name = maya_transform_name
        self.safe_name = ms_commands.legalizeName(self.name)
        self.parent = parent

        # child attributes
        self.child_cameras = []
        self.descendant_cameras = []
        self.child_meshes = []
        self.descendant_meshes = []
        self.child_lights = []
        self.descendant_lights = []
        self.child_transforms = []
        self.descendant_transforms = []

        # sample attributes
        self.matrices = []
        self.visibility_states = []

        # get children
        mesh_names = cmds.listRelatives(self.name, type='mesh', fullPath=True)
        if mesh_names != None:
            for mesh_name in mesh_names:
                self.child_meshes.append(MMesh(params, mesh_name, self))

        light_names = cmds.listRelatives(self.name, type='light', fullPath=True)
        if light_names != None:
            for light_name in light_names:
                self.child_lights.append(MLight(params, light_name, self))

        camera_names = cmds.listRelatives(self.name, type='camera', fullPath=True)
        if camera_names != None:
            for camera_name in camera_names:
                self.child_cameras.append(MCamera(params, camera_name, self))

        transform_names = cmds.listRelatives(self.name, type='transform', fullPath=True)
        if transform_names != None:
            for transform_name in transform_names:
                new_transform = MTransform(params, transform_name, self)
                self.child_transforms.append(new_transform)

                # add descendants
                self.descendant_cameras += new_transform.child_cameras
                self.descendant_meshes += new_transform.child_meshes
                self.descendant_lights += new_transform.child_lights
                self.descendant_transforms += new_transform.child_transforms

    def add_transform_sample(self):
        self.matricies.append(cmds.xform(self.name, query=True, matrix=True))


#--------------------------------------------------------------------------------------------------
# MTransformChild class.
#--------------------------------------------------------------------------------------------------

class MTransformChild():

    """ Base class for all classes representing Maya scene entities """

    def __init__(self, params, maya_entity_name, MTransform_object):
        self.params = params
        if self.params['verbose_output']:
            print("Creating {0}: {1}...".format(self.__class__.__name__, maya_entity_name))
        self.name = maya_entity_name
        self.safe_name = ms_commands.legalizeName(self.name)
        self.transform = MTransform_object


#--------------------------------------------------------------------------------------------------
# MMesh class.
#--------------------------------------------------------------------------------------------------

class MMesh(MTransformChild):

    """ Lightweight class representing Maya mesh data """

    def __init__(self, params, maya_mesh_name, MTransform_object):
        MTransformChild.__init__(self, params, maya_mesh_name, MTransform_object)                
        self.mesh_file_names = []
        self.materials = []

        attached_material_names = ms_commands.get_attached_materials(self.name)

        if attached_material_names is not None:
            for material_name in attached_material_names:
                if cmds.nodeType(material_name) == 'ms_appleseed_material':
                    self.materials.append(MMsMaterial(self.params, material_name))

    def add_deform_sample(self, mesh_dir, time):
        file_name = '{0}_{1}.obj'.format(self.safe_name, time)
        output_file_path = os.path.join(mesh_dir, file_name)
        self.mesh_file_names.append(ms_commands.export_obj(self.safe_name, output_file_path, overwrite=True))


#--------------------------------------------------------------------------------------------------
# MLight class.
#--------------------------------------------------------------------------------------------------

class MLight(MTransformChild):

    """ Lightweight class representing Maya light data """

    def __init__(self, params, maya_light_name, MTransform_object):
        MTransformChild.__init__(self, params, maya_light_name, MTransform_object)
        self.color = cmds.getAttr(self.name + '.color')
        self.multiplier = cmds.getAttr(self.name+'.intensity')
        self.decay = cmds.getAttr(self.name+'.decayRate')
        self.model = cmds.nodeType(self.name)
        if self.model == 'spotLight':
            self.inner_angle = cmds.getAttr(self.name + '.coneAngle')
            self.outer_angle = cmds.getAttr(self.name + '.coneAngle') + cmds.getAttr(self.name + '.penumbraAngle')


#--------------------------------------------------------------------------------------------------
# MCamera class.
#--------------------------------------------------------------------------------------------------

class MCamera(MTransformChild):

    """ Lightweight class representing Maya camera data """

    def __init__(self, params, maya_camera_name, MTransform_object):
        MTransformChild.__init__(self, params, maya_camera_name, MTransform_object)

        # In Maya cameras are descendents of transforms like other objects but in appleseed they exist outside
        # of the main assembly. For this reason we include the world space matrix as an attribute of the camera's
        # transform even though it's not a 'correct' representation of the Maya scene.
        self.world_space_matrices = []

        self.dof = (self.name + '.depthOfField' )
        self.focal_distance = cmds.getAttr(self.name + '.focusDistance') 
        self.focal_length = float(cmds.getAttr(self.name + '.focalLength')) / 1000
        self.f_stop = cmds.getAttr(self.name + '.fStop')

        maya_resolution_aspect = float(self.params['output_res_width']) / float(self.params['output_res_height'])
        maya_film_aspect = cmds.getAttr(self.name + '.horizontalFilmAperture') / cmds.getAttr(self.name + '.verticalFilmAperture')

        if maya_resolution_aspect > maya_film_aspect:
            self.film_width = float(cmds.getAttr(self.name + '.horizontalFilmAperture')) * inch_to_meter
            self.film_height = self.film_width / maya_resolution_aspect  
        else:
            self.film_height = float(cmds.getAttr(self.name + '.verticalFilmAperture')) * inch_to_meter
            self.film_width = self.film_height * maya_resolution_aspect 

    def add_matrix_sample(self):
        self.world_space_matrices.append(cmds.xform(self.transform.name, query=True, matrix=True, ws=True))


#--------------------------------------------------------------------------------------------------
# MFile class.
#--------------------------------------------------------------------------------------------------

class MFile():

    """ Lightweight class representing Maya file nodes """

    def __init__(self, params, maya_file_node):
        self.params = params
        self.name = maya_file_node
        self.safe_name = ms_commands.legalizeName(self.name)
        self.image_name = cmds.getAttr(self.name + '.fileTextureName')
        self.resolved_image_name = ms_commands.getFileTextureName(self.name)
        self.image_file_names = []
        self.is_animated = cmds.getAttr(self.name + '.useFrameExtension')
        self.alpha_is_luminance = cmds.getAttr(self.name + '.alphaIsLuminance')

        texture_placement_node = ms_commands.getConnectedNode(self.name + '.uvCoord')
        if texture_placement_node is not None:
            self.has_uv_placement = True
            self.repeat_u = cmds.getAttr(texture_placement_node + '.repeatU')
            self.repeat_v = cmds.getAttr(texture_placement_node + '.repeatV')
        else:
            self.has_uv_placement = False

    def add_image_sample(self, output_directory, time):
        image_name = ms_commands.get_file_textureName(self.name, time)

        if self.params['convertTexturesToExr']:
            converted_image = ms_commands.convertTexToExr(image_name, output_directory, overwrite=self.params['overwrite_existing_textures'], pass_through=False)
            self.image_file_names.append(converted_image)
        else:
            self.image_file_names.append(image_name)

#--------------------------------------------------------------------------------------------------
# MMsEnvironment class.
#--------------------------------------------------------------------------------------------------

class MMsEnvironment():

    """ Lightweight class representing Maya ms_environment nodes """

    def __init__(self, params, maya_ms_environment_node):
        self.name = maya_ms_environment_node
        self.safe_name = ms_commands.legalizeName(self.name)

        self.model = cmds.getAttr(self.name + '.model')

        # ********** key *************
        # Constant Environment = 0
        # Gradient Environment = 1
        # Latitude Longitude Map = 2
        # Mirrorball Map = 3

        self.constant_exitance = cmds.getAttr(self.name + '.constant_exitance')
        self.gradient_horizon_exitance = cmds.getAttr(self.name + '.gradient_horizon_exitance')
        self.gradient_zenith_exitance = cmds.getAttr(self.name + '.gradient_zenith_exitance')
        self.latitude_longitude_exitance = cmds.getAttr(self.name + '.latitude_longitude_exitance')
        self.mirrorball_exitance = cmds.getAttr(self.name + '.mirrorball_exitance')
        self.exitance_multiplier = cmds.getAttr(self.name + '.exitance_multiplier')

#--------------------------------------------------------------------------------------------------
# MColor class.
#--------------------------------------------------------------------------------------------------

class MColorConnection():

        """ Lightweight class representing Maya color connections, although these are not Maya nodes we define an M class for ease of use"""

        def __init__(self, params, color_connection):
            self.name = color_connection
            self.safe_name = ms_commands.legalizeName(self.name)
            self.color_value = cmds.getAttr(self.name)
            self.normalized_color = ms_commands.normalizeRGB(cmds.getAttr(self.name)[0])[:3]
            self.multiplier = ms_commands.normalizeRGB(cmds.getAttr(self.name)[0])[3]
            self.connected_node = ms_commands.getConnectedNode(self.name)
            if self.connected_node is not None:
                self.connected_node_type = cmds.nodeType(self.connected_node)

#--------------------------------------------------------------------------------------------------
# MMsMaterial class.
#--------------------------------------------------------------------------------------------------

class MMsMaterial():

    """ Lightweight class representing Maya material nodes """

    def __init__(self, params, maya_ms_material_name):
        self.params = params
        self.name = maya_ms_material_name
        self.safe_name = ms_commands.legalizeName(self.name)

        self.shading_nodes = []
        self.colors = []
        self.textures = []

        self.duplicate_shaders = cmds.getAttr(self.name + '.duplicate_front_attributes_on_back')

        self.enable_front = cmds.getAttr(self.name + '.enable_front_material')
        self.enable_back = cmds.getAttr(self.name + '.enable_back_material')

        self.bsdf_front = self.get_connections(self.name + '.BSDF_front_color')
        self.edf_front = self.get_connections(self.name + '.EDF_front_color')
        self.surface_shader_front = self.get_connections(self.name + '.surface_shader_front_color')
        self.normal_map_front = self.get_connections(self.name + '.normal_map_front_color')
        self.alpha_map = self.get_connections(self.name + '.alpha_map_color')

        # only use front shaders on back if box is checked
        if not self.duplicate_shaders:
            self.bsdf_back = self.get_connections(self.name + '.BSDF_back_color')
            self.edf_back = self.get_connections(self.name + '.EDF_back_color')
            self.surface_shader_back = self.get_connections(self.name + '.surface_shader_back_color')
            self.normal_map_back = self.get_connections(self.name + '.normal_map_back_color')

            self.shading_nodes += [self.bsdf_front,
                                   self.bsdf_back,
                                   self.edf_front,
                                   self.edf_back,
                                   self.surface_shader_front,
                                   self.surface_shader_back]

            self.textures = self.textures + [self.normal_map_front,
                                             self.normal_map_back,
                                             self.alpha_map]

        else: 
            self.bsdf_back, self.edf_back, self.surface_shader_back, self.normal_map_back = self.bsdf_front, self.edf_front, self.surface_shader_front, self.normal_map_front

            self.shading_nodes += [self.bsdf_front,
                                   self.edf_front,
                                   self.surface_shader_front]

            if self.normal_map_front is not None:
                  self.textures.append(self.normal_map_front)
            if self.alpha_map is not None:
                self.textures.append(self.alpha_map)


    def get_connections(self, attr_name):
        connection = MColorConnection(self.params, attr_name)

        if connection.connected_node is not None:
            if cmds.nodeType(connection.connected_node) == 'ms_appleseed_shading_node':
                shading_node = MMsShadingNode(self.params, connection.connected_node)
                self.shading_nodes = self.shading_nodes + [shading_node] + shading_node.child_shading_nodes
                self.colors += shading_node.colors
                self.textures += shading_node.textures
                return shading_node

            elif cmds.nodeType(connection.connected_node) == 'file':
                texture_node = MFile(self.params, connection.connected_node)
                self.textures += [texture_node]
                return texture_node

        else:
            return None

#--------------------------------------------------------------------------------------------------
# MMsShadingNode class.
#--------------------------------------------------------------------------------------------------

class MMsShadingNode():

    """ Lightweight class representing Maya shading nodes """

    def __init__(self, params, maya_ms_shading_node_name):
        self.params = params
        self.name = maya_ms_shading_node_name
        self.safe_name = ms_commands.legalizeName(self.name)

        self.type = cmds.getAttr(self.name + '.node_type')    #bsdf, edf etc
        self.model = cmds.getAttr(self.name + '.node_model')  #lambertian etc

        self.child_shading_nodes = []
        self.attributes = dict()
        self.colors = []
        self.textures = []

        #add the correct attributes based on the entity defs xml
        for attribute_key in params['entityDefs'][self.model].attributes.keys():
            self.attributes[attribute_key] = ''

        for attribute_key in self.attributes.keys():
            maya_attribute = self.name + '.' + attribute_key

            # create variable to store the final string value
            attribute_value = ''

            # if the attribute is a color/entity
            if params['entityDefs'][self.model].attributes[attribute_key].type == 'entity_picker':

                color_connection = MColorConnection(self.params, maya_attribute)

                if color_connection.connected_node:

                    # if the node is an appleseed shading node
                    if color_connection.connected_node_type == 'ms_appleseed_shading_node':
                        shading_node = MMsShadingNode(self.params, color_connection.connected_node)
                        attribute_value = shading_node
                        self.child_shading_nodes = self.child_shading_nodes + [shading_node] + shading_node.child_shading_nodes
                        self.colors += shading_node.colors
                        self.textures = self.textures + shading_node.textures

                    # else if it's a Maya texture node
                    elif color_connection.connected_node_type == 'file':
                        texture_node = MFile(self.params, color_connection.connected_node)
                        attribute_value = texture_node
                        self.textures += [texture_node]

                # no node is connected, just use the color value
                else:
                    attribute_value = color_connection

            elif params['entityDefs'][self.model].attributes[attribute_key].type == 'dropdown_list': 
                pass
            # the node must be a text entity
            else:
                attribute_value = str(cmds.getAttr(maya_attribute))

            # add attribute to dict
            self.attributes[attribute_key] = attribute_value

#--------------------------------------------------------------------------------------------------
# AsParameter class.
#--------------------------------------------------------------------------------------------------

class AsParameter():

    """ Class representing an appleseed Parameter entity """

    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value

    def emit_xml(self, doc):
        doc.append_parameter(self.name, str(self.value))

#--------------------------------------------------------------------------------------------------
# AsParameters class.
#--------------------------------------------------------------------------------------------------

class AsParameters():

    """ Class representing an appleseed Parameters entity """

    def __init__(self, name=None):
        self.name = name
        self.parameters = []

    def emit_xml(self, doc):
        doc.start_element('parameters name="%s"' % self.name)
        for parameter in self.parameters:       
            parameter.emit_xml(doc)                         
        doc.end_element('parameters')

#--------------------------------------------------------------------------------------------------
# AsColor class.
#--------------------------------------------------------------------------------------------------

class AsColor():

    """ Class representing an appleseed Color entity """

    def __init__(self):
        self.name = None
        self.RGB_color = [0.5,0.5,0.5]
        self.alpha = 1
        self.multiplier = AsParameter('multiplier', '1')
        self.color_space = AsParameter('color_space', 'srgb')
        self.wavelength_range = '400.0, 700.0'

    def emit_xml(self, doc):
        print '// Writing color %s' % self.name
        doc.start_element('color name="%s"' % self.name)  
        self.color_space.emit_xml(doc)
        self.multiplier.emit_xml(doc)

        doc.start_element('values')
        doc.append_line('%.6f %.6f %.6f' % (self.RGB_color[0], self.RGB_color[1], self.RGB_color[2]))
        doc.end_element('values')
        doc.start_element('alpha')
        doc.append_line('%.6f' % self.alpha)
        doc.end_element('alpha')
        doc.end_element('color')

#--------------------------------------------------------------------------------------------------
# AsTransform class.
#--------------------------------------------------------------------------------------------------

class AsTransform():

    """ Class representing an appleseed Transform entity """

    def __init__(self):
        self.time = '000'
        self.scaling_value = 1
        self.matrix = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]

    def emit_xml(self, doc):
        doc.start_element('transform time="%s"' % self.time)

        doc.append_element('scaling value="%s"' % self.scaling_value)
        doc.start_element('matrix')

        doc.append_line('%.15f %.15f %.15f %.15f' % (self.matrix[0], self.matrix[4], self.matrix[8],  self.matrix[12]))
        doc.append_line('%.15f %.15f %.15f %.15f' % (self.matrix[1], self.matrix[5], self.matrix[9],  self.matrix[13]))
        doc.append_line('%.15f %.15f %.15f %.15f' % (self.matrix[2], self.matrix[6], self.matrix[10], self.matrix[14]))
        doc.append_line('%.15f %.15f %.15f %.15f' % (self.matrix[3], self.matrix[7], self.matrix[11], self.matrix[15]))

        doc.end_element('matrix')
        doc.end_element('transform') 

#--------------------------------------------------------------------------------------------------
# AsTexture class.
#--------------------------------------------------------------------------------------------------

class AsTexture():

    """ Class representing an appleseed Texture entity """

    def __init__(self):
        self.name = None
        self.model = 'disk_texture_2d'
        self.color_space = AsParameter('color_space', 'srgb')
        self.file_name = None
        self.instances = []

    def instantiate():
        texture_instance = AsTextureInstance(self)
        self.instances.append(texture_instance)
        return texture_instance

    def emit_xml(self, doc):
        doc.start_element('texture name="%s" model="%s"' % (self.name, self.model))
        self.color_space.emit_xml(doc)
        self.file_name.emit_xml(doc)
        doc.end_element('model')

#--------------------------------------------------------------------------------------------------
# AsTextureInstance class.
#--------------------------------------------------------------------------------------------------

class AsTextureInstance():

    """ Class representing an appleseed Texture Instance entity """

    def __init__(self, as_texture):
        self.name = '%s_instance_%i' % (as_texture.name, len(as_texture.instances))
        self.texture = as_texture
        self.addressing_mode = AsParameter('addressing_mode', 'wrap')
        self.filtering_mode = AsParameter('filtering_mode', 'bilinear')
        self.alpha_mode = AsParameter('alpha_mode', 'alpha_channel')

    def emit_xml(self, doc):
        doc.start_element('texture_instance name="%s" texture="%s"' % (self.name, self.texture.name))
        self.addressing_mode.emit_xml(doc)
        self.filtering_mode.emit_xml(doc)
        self.alpha_mode.emit_xml(doc)
        doc.end_element('texture_instance')

#--------------------------------------------------------------------------------------------------
# AsObject class.
#--------------------------------------------------------------------------------------------------

class AsObject():

    """ Class representing appleseed Object entity """

    def __init__(self):
        self.name = None
        self.model = 'mesh_object'
        self.file_name = None
        self.instances = []

    def instantiate(self):
        object_instance = AsObjectInstance(self)
        self.instances.append(object_instance)
        return object_instance

    def emit_xml(self, doc):
        doc.start_element('object name="%s" model="%s"' % (self.name, self.model))
        self.file_name.emit_xml(doc)
        doc.end_element('object')

#--------------------------------------------------------------------------------------------------
# AsObjectInstanceMaterialAssignment class.
#--------------------------------------------------------------------------------------------------

class AsObjectInstanceMaterialAssignment():

    """ Class representing appleseed Object Instance Material Assignment entity """

    def __init__(self, slot=None, side=None, material=None):
        self.slot = slot
        self.side = side
        self.material = material

    def emit_xml(self, doc):
        doc.append_element('assign_material slot="%s" side="%s" material="%s"' % (self.slot, self.side, self.material))

#--------------------------------------------------------------------------------------------------
# AsObjectInstance class.
#--------------------------------------------------------------------------------------------------

class AsObjectInstance():

    """ Class representing appleseed Object Instance entity """

    def __init__(self, as_object):
        self.name = self.name = '%s_instance_%i' % (as_object.name, len(as_object.instances))
        self.object = as_object
        self.transforms = []
        self.material_assignments = []

    def emit_xml(self, doc):
        doc.start_element('object_inatsnce name="%s" object="%s"' % (self.name, self.object.name))
        for transform in self.transforms:
            transform.emit_xml(doc)
        for material_assignment in self.material_assignments:
            material_assignment.emit_xml(doc)
        doc.end_element('object')

#--------------------------------------------------------------------------------------------------
# AsCamera class.
#--------------------------------------------------------------------------------------------------

class AsCamera():

    """ Class representing appleseed Camera entity """

    def __init__(self):
        self.name = None
        self.model = None
        self.film_dimensions = None
        self.focal_length = None
        self.f_stop = None
        self.diaphragm_blades = AsParameter('diaphragm_blades', '0')
        self.diaphragm_tilt_angle = AsParameter('diaphragm_tilt_angle', '0.0')
        self.transforms = []
    
    def emit_xml(self, doc):
        doc.start_element('camera name="%s" model="%s"' % (self.name, self.model))

        self.film_dimensions.emit_xml(doc)
        self.focal_length.emit_xml(doc)

        if self.model == 'thinlens_camera':
            self.diaphragm_blades.emit_xml(doc)
            self.diaphragm_tilt_angle.emit_xml(doc)
            self.f_stop.emit_xml(doc)

        for transform in self.transforms:
            transform.emit_xml(doc)

        doc.end_element('camera')

#--------------------------------------------------------------------------------------------------
# AsEnvironment class.
#--------------------------------------------------------------------------------------------------

class AsEnvironment():

    """ Class representing appleseed Environment entity """

    def __init__(self):
        self.name = None
        self.environment_shader = None
        self.environment_edf = None

    def emit_xml(self, doc):
        doc.start_element('environment name="%s" model="edf_environment_shader"' % self.name)
        if self.environment_shader is not None:
            self.environment_shader.emit_xml(doc)
        self.environment_edf.emit_xml(doc)
        doc.end_element('environment')

#--------------------------------------------------------------------------------------------------
# AsEnvironmentShader class.
#--------------------------------------------------------------------------------------------------

class AsEnvironmentShader():

    """ Class representing appleseed Environment Shader entity """

    def __init__(self):
        self.name = None
        self.edf = None

    def emit_xml(self, doc):
        doc.start_element('environment_shader name="%s" model="edf_environment_shader"' % self.name)
        self.edf.emit_xml(doc)
        doc.end_element('environment_shader')

#--------------------------------------------------------------------------------------------------
# AsEnvironmentEdf class.
#--------------------------------------------------------------------------------------------------

class AsEnvironmentEdf():

    """ Class representing appleseed Environment EDF entity """

    def __init__(self):
        self.name = None
        self.model = None
        self.parameters = []

    def emit_xml(self, doc):
        doc.start_element('environment_edf name="%s" model="%s"' % (self.name, self.model))
        for parameter in self.parameters:
            parameter.emit_xml(doc)
        doc.end_element('environment')

#--------------------------------------------------------------------------------------------------
# AsMaterial class.
#--------------------------------------------------------------------------------------------------

class AsMaterial():

    """ Class representing appleseed Material entity """

    def __init__(self):
        self.name = None
        self.model = 'generic_material'
        self.bsdf = None
        self.edf = None
        self.surface_shader = None
        self.alpha_map = None
        self.normal_map = None

    def emit_xml(self, doc):
        doc.start_element('material name="%s" model="%s"' % (self.name, self.model))

        if self.bsdf is not None:
            self.bsdf.emit_xml(doc)

        if self.edf is not None:
            self.edf.emit_xml(doc)

        if self.surface_shader is not None:
            self.surface_shader.emit_xml(doc)

        if self.alpha_map is not None:
            self.alpha_map.emit_xml(doc)

        if self.normal_map is not None:
            self.normal_map.emit_xml(doc)

        doc.end_element('material')

#--------------------------------------------------------------------------------------------------
# AsBsdf class.
#--------------------------------------------------------------------------------------------------

class AsBsdf():

    """ Class representing appleseed BSDF entity """

    def __init__(self):
        self.name = None
        self.model = None
        self.parameters = []

    def emit_xml(sels, doc):
        doc.start_element('bsdf name="%s" model="%s"' % (self.name, self.model))
        for parameter in self.parameters:
            parameter.emit_xml(doc)
        doc.end_element('bsdf')

#--------------------------------------------------------------------------------------------------
# AsEdf class.
#--------------------------------------------------------------------------------------------------

class AsEdf():

    """ Class representing appleseed EDF entity """

    def __init__(self):
        self.name = None
        self.model = None
        self.parameters = []

    def emit_xml(self, doc):
        doc.start_element('edf name="%s" model="%s"' % (self.name, self.model))
        for parameter in self.parameters:
            parameter.emit_xml(doc)
        doc.end_element('edf')

#--------------------------------------------------------------------------------------------------
# AsSurfaceShader class.
#--------------------------------------------------------------------------------------------------

class AsSurfaceShader():

    """ Class representing appleseed Surface Shader entity """

    def __init__(self):
        self.name = None
        self.model = None
        self.parameters = []

    def emit_xml(self, doc):
        doc.start_element('surface_shader name="%s" model="%s"' % (self.name, self.model))
        for parameter in self.parameters:
            parameter.emit_xml(doc)
        doc.end_element('surface_shader')

#--------------------------------------------------------------------------------------------------
# AsLight class.
#--------------------------------------------------------------------------------------------------

class AsLight():

    """ Class representing appleseed Surface Shader entity """

    def __init__(self):
        self.name = None
        self.model = None
        self.color = None
        self.multiplier = None
        self.inner_angle = None
        self.outer_angle = None
        self.transform = None

    def emit_xml(self, doc):
        doc.start_element('light name="%s" model="%s"' % (self.name, self.model))
        self.color.emit_xml(doc)
        if self.model == 'spot_light':
            self.inner_angle.emit_xml(doc)
            self.outer_angle.emit_xml(doc)
        self.transform.emit_xml(doc)
        doc.end_element('light')

#--------------------------------------------------------------------------------------------------
# AsAssembly class.
#--------------------------------------------------------------------------------------------------

class AsAssembly():

    """ Class representing appleseed Assembly entity """

    def __init__(self):
        self.name = None
        self.colors = []
        self.textures = []
        self.texture_instances = []
        self.materials = []
        self.bsdfs = []
        self.edfs = []
        self.surface_shaders = []
        self.lights = []
        self.objects = []
        self.object_instances = []
        self.assemblies = []
        self.assembly_instances = []

        self.instances = []

    def instantiate(self):
        assembly_instance = AsAssemblyInstance(self)
        self.object_instances.append(assembly_instance)
        return assembly_instance

    def emit_xml(self, doc):
        doc.start_element('assembly name="%s"' % self.name)

        for color in self.colors:
            color.emit_xml(doc)

        for texture in self.textures:
            texture.emit_xml(doc)

        for texture_instance in self.texture_instances:
            texture_instance.emit_xml(doc)

        for material in self.materials:
            material.emit_xml(doc)

        for bsdf in self.bsdfs:
            bsdf.emit_xml(doc)

        for edf in self.edfs:
            edf.emit_xml(doc)

        for surface_shader in self.surface_shaders:
            surface_shader.emit_xml(doc)

        for light in self.lights:
            light.emit_xml(doc)

        for object in self.objects:
            object.emit_xml(doc)

        for object_instance in self.object_instances:
            object_instance.emit_xml(doc)

        for assembly in self.assemblies:
            assembly.emit_xml(doc)

        for assembly_instance in self.assembly_instances:
            assembly_instance.emit_xml(doc)

        doc.end_element('assembly')

#--------------------------------------------------------------------------------------------------
# AsAssemblyInstance class.
#--------------------------------------------------------------------------------------------------

class AsAssemblyInstance():

    """ Class representing appleseed Assembly Instance entity """

    def __init__(self, as_assembly):
        self.name = '%s_instance_%i' % (as_assembly.name, len(as_assembly.instances))
        self.assembly = as_assembly
        self.transforms = []

    def emit_xml(self, doc):
        doc.start_element('assembly_instance name="%s" assembly="%s"' % (self.name, self.assembly.name))
        for transform in self.transforms:
            transform.emit_xml(doc)
        doc.end_element('assembly_instance')

#--------------------------------------------------------------------------------------------------
# AsFrame class.
#--------------------------------------------------------------------------------------------------

class AsFrame():

    """ Class representing appleseed Frame entity """

    def __init__(self):
        self.name = 'beauty'
        self.camera = None
        self.color_space = AsParameter('camera', 'srgb')
        self.resolution = None

    def emit_xml(self, doc):
        doc.start_element('frame name="%s"' % self.name)
        self.camera.emit_xml(doc)
        self.color_space.emit_xml(doc)
        self.resolution.emit_xml(doc)
        doc.end_element('frame')

#--------------------------------------------------------------------------------------------------
# AsOutput class.
#--------------------------------------------------------------------------------------------------

class AsOutput():

    """ Class representing appleseed Output entity """

    def __init__(self):
        self.frames = []

    def emit_xml(self, doc):
        doc.start_element('output')
        for frame in self.frames:
            frame.emit_xml(doc)
        doc.end_element('output')

#--------------------------------------------------------------------------------------------------
# AsConfiguration class.
#--------------------------------------------------------------------------------------------------

class AsConfiguration():

    """ Class representing appleseed Configuration entity """

    def  __init__(self):
        self.name = None
        self.base = None
        self.parameters = []

    def emit_xml(self, doc):
        doc.start_element('configuration')
        doc.end_element('configuration')



#--------------------------------------------------------------------------------------------------
# AsConfigurations class.
#--------------------------------------------------------------------------------------------------

class AsConfigurations():

    """ Class representing appleseed Configurations entity """

    def __init__(self):
        self.configurations = []

    def emit_xml(self, doc):
        doc.start_element('configurations')
        for configuration in self.configurations:
            configuration.emit_xml(doc)
        doc.end_element('configurations')

#--------------------------------------------------------------------------------------------------
# AsScene class.
#--------------------------------------------------------------------------------------------------

class asScene():

    """ Class representing appleseed Scene entity """

    def __init__(self):
        self.cameras = []
        self.colors = []
        self.textures = []
        self.texture_instances = []
        self.environment_edfs = []
        self.environment_shaders = []
        self.environment = None
        self.output = None
        self.configurations = None
        self.assemblies = []
        self.assembly_instances = []

    def emit_xml(doc):
        doc.start_element('scene')

        for camera in self.cameras:
            camera.emit_xml(doc)

        for color in self.colors:
            color.emit_xml(doc)

        for texture in self.textures:
            texture.emit_xml(doc)

        for texture_instance in self.texture_instances:
            texture_instance.emit_xml(doc)

        for environment_edf in self.environment_edfs:
            environment_edf.emit_xml(doc)

        for environment_shader in self.environment_shaders:
            environment_shader.emit_xml(doc)

        if self.environment is not None:
            self.environment.emit_xml(doc)

        if self.output is not None:
            self.output.emit_xml(doc)

        if self.configurations is not None:
            self.configurations.emit_xml(doc)

        for assembly in self.assemblies:
            assembly.emit_xml(doc)

        for assembly_instance in self.assembly_instances:
            assembly_instance.emit_xml(doc)

        doc.end_element('scene')

#--------------------------------------------------------------------------------------------------
# AsProject class.
#--------------------------------------------------------------------------------------------------

class asProject():

    """ Class representing appleseed Project entity """

    def __init__(self):
        scene = None

    def emit_xml(self, doc):
        scene.emit_xml(doc)

#--------------------------------------------------------------------------------------------------
# traslate_maya_scene class.
#--------------------------------------------------------------------------------------------------

def translate_maya_scene(render_settings_node):

    """ Main function for converting a cached maya scene into an appleseed object heirarchy """

    params = get_maya_params(render_settings_node)
    
    maya_scene = get_maya_scene (params)

    # initialize frame list with single default value 
    frame_list = [int(cmds.currentTime(query=True))]

    # if animation export is on populate frame list with correct frame numbers
    if params['export_animation']:
        frame_list = range(params['animation_start_frame'], params['animation_end_frame'] + 1)

    for frame_number in frame_list:
        pass

    # project = AsProject()

    # doc = WriteXml(filepath)
    # doc.append_line('<?xml version="1.0" encoding="UTF-8"?>')
    # doc.append_line('<!-- File generated by Mayaseed version {0} -->'.format(ms_commands.MAYASEED_VERSION))

    # project.emit_xml(doc)

    # doc.close()

#--------------------------------------------------------------------------------------------------
# Color class.
#--------------------------------------------------------------------------------------------------

class Color():
    def __init__(self, name, color, multiplier):
        self.name = name
        self.color = color
        self.multiplier = multiplier
        self.color_space = 'srgb'
        self.alpha = 1.0

    def writeXML(self, doc):
        print('Writing color {0}'.format(self.name))
        doc.start_element('color name="{0}"'.format(self.name))       
        doc.append_parameter('color', '{0:.6f} {1:.6f} {2:.6f}'.format(self.color[0], self.color[1], self.color[2]))
        doc.append_parameter('color_space', self.color_space)
        doc.append_parameter('multiplier', self.multiplier)
        doc.append_parameter('alpha', self.alpha)

        doc.start_element('values')
        doc.append_line('{0:.6f} {1:.6f} {2:.6f}'.format(self.color[0], self.color[1], self.color[2]))
        doc.end_element('values')
        doc.start_element('alpha')
        doc.append_line('{0:.6f}'.format(self.alpha))
        doc.end_element('alpha')
        doc.end_element('color')


#--------------------------------------------------------------------------------------------------
# Texture class.
#--------------------------------------------------------------------------------------------------

class Texture():
    def __init__(self, name, file_name, color_space='srgb', alpha_mode='alpha_channel'):
        self.name = name

        directory = ms_commands.legalizeName(os.path.split(file_name)[0])
        filename = ms_commands.legalizeName(os.path.split(file_name)[1])
        self.filepath = os.path.join(directory, filename)

        self.color_space = color_space
        self.alpha_mode = alpha_mode

    def writeXMLObject(self, doc):
        print('Writing texture object {0}'.format(self.name))
        doc.start_element('texture name="{0}" model="disk_texture_2d"'.format(self.name))
        doc.append_parameter('color_space', self.color_space)
        doc.append_parameter('filename', self.filepath)
        doc.end_element('texture')

    def writeXMLInstance(self, doc):
        print('Writing texture instance {0}_inst'.format(self.name))
        doc.start_element('texture_instance name="{0}_inst" texture="{0}"'.format(self.name, self.name))
        doc.append_parameter('addressing_mode', 'wrap')
        doc.append_parameter('filtering_mode', 'bilinear')
        doc.append_parameter('alpha_mode', self.alpha_mode)
        doc.end_element('texture_instance')


#--------------------------------------------------------------------------------------------------
# Light class.
#--------------------------------------------------------------------------------------------------

class Light():
    def __init__(self, params, name, model='point_light'):
        self.params = params
        self.name = name
        self.model = model
        self.color_name = self.name + '_exitance'
        self.color = cmds.getAttr(self.name+'.color')[0]
        self.multiplier = cmds.getAttr(self.name+'.intensity')
        self.decay = cmds.getAttr(self.name+'.decayRate')
        self.inner_angle = None
        self.outer_angle = None

    def writeXML(self, doc):
        print('Writing light: {0}'.format(self.name))
        doc.start_element('light name="{0}" model="{1}"'.format(self.name, self.model))

        # add spot light attribs if they exist
        if self.model == 'spot_light':
            doc.append_parameter('inner_angle', self.inner_angle)
            doc.append_parameter('outer_angle', self.outer_angle)

        doc.append_parameter('exitance', self.color_name)

        write_transform(doc, self.params['scene_scale'], self.name, self.params['export_transformation_blur'], self.params['motion_samples'])
        doc.end_element('light')


#--------------------------------------------------------------------------------------------------
# Material class.
#--------------------------------------------------------------------------------------------------

class Material():
    def __init__(self, params, maya_node):
        self.params = params
        self.name = maya_node
        self.safe_name = ms_commands.legalizeName(self.name)
        self.duplicate_shaders = cmds.getAttr(self.name + '.duplicate_front_attributes_on_back')
        self.shading_nodes = []
        self.colors = []
        self.textures = []
        self.enable_front = cmds.getAttr(self.name + '.enable_front_material')
        self.enable_back = cmds.getAttr(self.name + '.enable_back_material')

        self.bsdf_front = self.getMayaAttr(self.name + '.BSDF_front_color')
        self.edf_front = self.getMayaAttr(self.name + '.EDF_front_color')
        self.surface_shader_front = self.getMayaAttr(self.name + '.surface_shader_front_color')
        self.normal_map_front = self.getMayaAttr(self.name + '.normal_map_front_color')
        self.alpha_map = self.getMayaAttr(self.name + '.alpha_map_color')

        # only use front shaders on back if box is checked
        if not self.duplicate_shaders:
            self.bsdf_back = self.getMayaAttr(self.name + '.BSDF_back_color')
            self.edf_back = self.getMayaAttr(self.name + '.EDF_back_color')
            self.surface_shader_back = self.getMayaAttr(self.name + '.surface_shader_back_color')
            self.normal_map_back = self.getMayaAttr(self.name + '.normal_map_back_color')

            self.shading_nodes += [self.bsdf_front,
                                   self.bsdf_back,
                                   self.edf_front,
                                   self.edf_back,
                                   self.surface_shader_front,
                                   self.surface_shader_back]

            self.textures = self.textures + [self.normal_map_front,
                                             self.normal_map_back,
                                             self.alpha_map]

        else: 
            self.bsdf_back, self.edf_back, self.surface_shader_back, self.normal_map_back = self.bsdf_front, self.edf_front, self.surface_shader_front, self.normal_map_front

            self.shading_nodes += [self.bsdf_front,
                                   self.edf_front,
                                   self.surface_shader_front]

            self.textures += [self.normal_map_front, self.alpha_map]

    def getMayaAttr(self, attr_name):
        connection = cmds.listConnections(attr_name)
        if connection:
            if cmds.nodeType(connection[0]) == 'ms_appleseed_shading_node':
                shading_node = ShadingNode(self.params, connection[0])
                self.shading_nodes = self.shading_nodes + [shading_node] + shading_node.getChildren()
                self.colors += shading_node.colors
                self.textures += shading_node.textures
                return shading_node

            elif cmds.nodeType(connection[0]) == 'file':
                maya_texture_file = ms_commands.getFileTextureName(connection[0])
                texture = ms_commands.convertTexToExr(maya_texture_file, self.params['absolute_tex_dir'], overwrite=self.params['overwrite_existing_textures'], pass_through=False)
                texture_node = Texture(connection[0] + '_texture', os.path.join(self.params['tex_dir'], os.path.split(texture)[1]))
                attribute_value = texture_node.name + '_inst'
                self.textures += [texture_node]
                return texture_node

        else:
            return None

    def getShadingNodes(self):
        return self.shading_nodes

    def writeXML(self, doc):
        if self.duplicate_shaders:
            if self.enable_front:
                print("Writing material {0}...".format(self.name))
                doc.start_element('material name="{0}" model="generic_material"'.format(self.name))
                if self.bsdf_front:
                    doc.append_parameter('bsdf', self.bsdf_front.name)
                if self.edf_front:
                    doc.append_parameter('edf', self.edf_front.name)
                doc.append_parameter('surface_shader', self.surface_shader_front.name)
                if self.alpha_map:
                    doc.append_parameter('alpha_map', self.alpha_map.name + '_inst')
                if self.normal_map_front:
                    doc.append_parameter('normal_map', self.normal_map_front.name + '_inst')
                doc.end_element('material')
        else:
            if self.enable_front:
                print("Writing material {0}_front...".format(self.name))
                doc.start_element('material name="{0}_front" model="generic_material"'.format(self.name))
                if self.bsdf_front:
                    doc.append_parameter('bsdf', self.bsdf_front.name)
                if self.edf_front:
                    doc.append_parameter('edf', self.edf_front.name)
                doc.append_parameter('surface_shader', self.surface_shader_front.name)
                if self.alpha_map:
                    doc.append_parameter('alpha_map', self.alpha_map.name + '_inst')
                if self.normal_map_front:
                    doc.append_parameter('normal_map', self.normal_map_front.name + '_inst')
                doc.end_element('material')    
            if self.enable_back:
                print("Writing material {0}_back...".format(self.name))
                doc.start_element('material name="{0}_back" model="generic_material"'.format(self.name))
                if self.bsdf_back:
                    doc.append_parameter('bsdf', self.bsdf_back.name)
                if self.edf_back:
                    doc.append_parameter('edf', self.edf_back.name)
                doc.append_parameter('surface_shader', self.surface_shader_back.name)
                if self.alpha_map:
                    doc.append_parameter('alpha_map', self.alpha_map.name + '_inst')
                if self.normal_map_back:
                    doc.append_parameter('normal_map', self.normal_map_back.name + '_inst')
                doc.end_element('material') 


#--------------------------------------------------------------------------------------------------
# ShadingNode class.
#--------------------------------------------------------------------------------------------------

class ShadingNode():
    def __init__(self, params, name, attributes=False, node_type=False, model=False):
        self.params = params
        self.name = name
        self.type = node_type           # bsdf etc
        self.model = model              # ashikhmin-shirley etc
        self.child_shading_nodes = []
        self.attributes = dict()
        self.colors = []
        self.textures = []

        # if the node comes with attributes to initialize with then use them
        if attributes:
            self.attributes = attributes

        # else find them from Maya
        else:
            self.type = cmds.getAttr(self.name + '.node_type')      # bsdf, edf...
            self.model = cmds.getAttr(self.name + '.node_model')    # lambertian...

            # add the correct attributes based on the entity defs XML
            for attribute_key in params['entityDefs'][self.model].attributes.keys():
                self.attributes[attribute_key] = ''

            for attribute_key in self.attributes.keys():
                maya_attribute = self.name + '.' + attribute_key

                # create variable to store the final string value
                attribute_value = ''

                # if the attribute is a color/entity
                if params['entityDefs'][self.model].attributes[attribute_key].type == 'entity_picker':

                    # get attribute color value
                    attribute_color = cmds.getAttr(maya_attribute)[0]
                    connected_node = None

                    # check for connected node
                    connection = cmds.listConnections(maya_attribute, destination=False, source=True)
                    if connection:
                        connected_node = connection[0]

                    # if there is a node connected
                    if connected_node:
                        # if the node is an appleseed shading node
                        if cmds.nodeType(connected_node) == 'ms_appleseed_shading_node':
                            shading_node = ShadingNode(self.params, connected_node)
                            attribute_value = shading_node.name
                            self.child_shading_nodes = self.child_shading_nodes + [shading_node] + shading_node.child_shading_nodes
                            self.colors += shading_node.colors
                            self.textures = self.textures + shading_node.textures

                        # else if it's a Maya texture node
                        elif cmds.nodeType(connected_node) == 'file':
                            maya_texture_file = ms_commands.getFileTextureName(connected_node)
                            texture = ms_commands.convertTexToExr(maya_texture_file, params['absolute_tex_dir'], overwrite=self.params['overwrite_existing_textures'], pass_through=False)
                            texture_node = Texture(connected_node + '_texture', os.path.join(params['tex_dir'], os.path.split(texture)[1]))
                            attribute_value = texture_node.name + '_inst'
                            self.textures += [texture_node]

                        # if the node is unrecognized, bake it
                        elif self.params['convertShadingNodes']:
                            # convert texture and get path
                            output_texture = os.path.join(params['tex_dir'], connected_node + '.exr')
                            texture = ms_commands.convertConnectionToImage(self.name, attribute_key, output_texture, resolution=1024)
                            texture_node = Texture(connected_node + '_texture', os.path.join(params['tex_dir'], os.path.split(texture)[1]))
                            attribute_value = texture_node.name + '_inst'
                            self.textures += [texture_node]

                    # no node is connected, just use the color value
                    else:
                        # if that color is gray interpret the R value as a 1-dimensional value
                        if attribute_color[0] == attribute_color[1] and attribute_color[0] == attribute_color[2]:
                            attribute_value = str(attribute_color[0])

                        # if it's not black it must be a color so create a color node
                        elif attribute_color != (0, 0, 0):
                            color_name = self.name + '_' + attribute_key + '_color'
                            normalized_color = ms_commands.normalizeRGB(attribute_color)
                            color_node = Color(color_name, normalized_color[:3], normalized_color[3])
                            attribute_value = color_node.name
                            self.colors += [color_node]

                elif params['entityDefs'][self.model].attributes[attribute_key].type == 'dropdown_list': 
                    pass

                # the node must be a text entity
                else:
                    attribute_value = str(cmds.getAttr(maya_attribute))

                # add attribute to dict
                self.attributes[attribute_key] = attribute_value

    def getChildren(self):
        return self.child_shading_nodes

    def writeXML(self, doc):
        print("Writing shading node {0}...".format(self.name))
        doc.start_element('{0} name="{1}" model="{2}"'.format(self.type, self.name, self.model))

        #add the relevant parameters
        for attribute_key in self.attributes.keys():
            #only output the attribute if it has a value
            if self.attributes[attribute_key]:
                doc.append_parameter(attribute_key, self.attributes[attribute_key])

        doc.end_element(self.type)


#--------------------------------------------------------------------------------------------------
# Bsdf class.
#--------------------------------------------------------------------------------------------------

class Bsdf():
    def __init__(self, name, model, bsdf_params):
        self.name = name
        self.model = model
        self.bsdf_params = bsdf_params

    def writeXML(self, doc):
        print("Writing BSDF {0}...".format(self.name))
        doc.start_element('bsdf name="{0}" model="{1}"'.format(self.name, self.model))
        for param in self.bsdf_params:
            doc.append_parameter(param, self.bsdf_params[param])
        doc.end_element('bsdf')


#--------------------------------------------------------------------------------------------------
# Edf class.
#--------------------------------------------------------------------------------------------------

class Edf():
    def __init__(self, name, model, edf_params):
        self.name = name
        self.model = model
        self.edf_params = edf_params

    def writeXML(self, doc):
        print("Writing EDF {0}...".format(self.name))
        doc.start_element('edf name="{0}" model="{1}"'.format(self.name, self.model))
        for param in self.edf_params:
            doc.append_parameter(param, self.edf_params[param])
        doc.end_element('edf')


#--------------------------------------------------------------------------------------------------
# SurfaceShader class.
#--------------------------------------------------------------------------------------------------

class SurfaceShader():
    def __init__(self, name, model, surface_shader_params=None):
        self.name = name
        self.model = model
        self.surface_shader_params = surface_shader_params

    def writeXML(self, doc):
        doc.start_element('surface_shader name="{0}" model="{1}"'.format(self.name, self.model))
        if self.model == 'constant_surface_shader':
            for param in self.surface_shader_params:
                doc.append_parameter(param, self.surface_shader_params[param])
        doc.end_element('surface_shader')


#--------------------------------------------------------------------------------------------------
# Camera class.
#--------------------------------------------------------------------------------------------------

class Camera():
    def __init__(self, params, cam):
        self.params = params
        if self.params['sceneCameraDefaultThinLens'] or cmds.getAttr(cam + '.depthOfField'):
            self.model = 'thinlens_camera'
            self.f_stop = cmds.getAttr(cam + '.fStop')
            self.focal_distance = cmds.getAttr(cam + '.focusDistance')
            self.diaphragm_blades = 0
            self.diaphragm_tilt_angle = 0.0
        else:
            self.model = 'pinhole_camera'
        self.name = cam

        maya_resolution_aspect = float(params['output_res_width']) / float(params['output_res_height'])
        maya_film_aspect = cmds.getAttr(cam + '.horizontalFilmAperture') / cmds.getAttr(cam + '.verticalFilmAperture')

        if maya_resolution_aspect > maya_film_aspect:
            self.film_width = float(cmds.getAttr(self.name + '.horizontalFilmAperture')) * inch_to_meter
            self.film_height = self.film_width / maya_resolution_aspect  
        else:
            self.film_height = float(cmds.getAttr(self.name + '.verticalFilmAperture')) * inch_to_meter
            self.film_width = self.film_height * maya_resolution_aspect 

        self.focal_length = float(cmds.getAttr(self.name+'.focalLength')) / 1000

    def writeXML(self, doc):
        print("Writing camera {0}...".format(self.name))
        doc.start_element('camera name="{0}" model="{1}"'.format(self.name, self.model))

        doc.append_parameter('film_dimensions', '{0} {1}'.format(self.film_width, self.film_height))
        doc.append_parameter('focal_length', self.focal_length)

        if self.model == 'thinlens_camera':
            print("Exporting {0} as thin lens camera...".format(self.name))
            doc.append_parameter('focal_distance', self.focal_distance)
            doc.append_parameter('f_stop', self.f_stop)
            doc.append_parameter('diaphragm_blades', self.diaphragm_blades)
            doc.append_parameter('diaphragm_tilt_angle', self.diaphragm_tilt_angle)

        #output transform matrix
        write_transform(doc, self.params['scene_scale'], self.name, self.params['export_camera_blur'], self.params['motion_samples'])

        doc.end_element('camera')


#--------------------------------------------------------------------------------------------------
# Environment class.
#--------------------------------------------------------------------------------------------------

class Environment():
    def __init__(self, params, name, shader, edf):
        self.params = params
        self.name = name
        self.environment_shader = shader
        self.environment_edf = edf

    def writeXML(self, doc):
        print("Writing environment {0}...".format(self.name))
        doc.start_element('environment name="{0}" model="generic_environment"'.format(self.name))
        doc.append_parameter('environment_edf', self.environment_edf)
        doc.end_element('environment')


#--------------------------------------------------------------------------------------------------
# EnvironmentShader class.
#--------------------------------------------------------------------------------------------------

class EnvironmentShader():
    def __init__(self, name, edf):
        self.name = name
        self.edf = edf

    def writeXML(self, doc):
        print("Writing environment shader {0}...".format(self.name))
        doc.start_element('environment_shader name="{0}" model="edf_environment_shader"'.format(self.name))
        doc.append_parameter('environment_edf', self.edf)
        doc.end_element('environment_shader')


#--------------------------------------------------------------------------------------------------
# EnvironmentEdf class.
#--------------------------------------------------------------------------------------------------

class EnvironmentEdf():
    def __init__(self, name, model, edf_params):
        self.name = name
        self.model = model
        self.edf_params = edf_params

    def writeXML(self, doc):
        print("Writing environment EDF {0}...".format(self.name))
        doc.start_element('environment_edf name="{0}" model="{1}"'.format(self.name, self.model))
        for param in self.edf_params:
            doc.append_parameter(param, self.edf_params[param])
        doc.end_element('environment_edf')


#--------------------------------------------------------------------------------------------------
# Geometry class.
#--------------------------------------------------------------------------------------------------

class Geometry():
    def __init__(self, params, name, output_file, assembly='main_assembly'):
        check_export_cancelled()
        self.params = params
        self.name = name
        self.short_name = ms_commands.legalizeName(self.name.split('|')[-1])
        self.safe_name = ms_commands.legalizeName(name)

        self.hierarchy_name = name
        self.material_nodes = []
        self.shading_nodes = []
        self.colors = []
        self.textures = []

        current_object = name
        while cmds.listRelatives(current_object, parent=True):
            current_object = cmds.listRelatives(current_object, parent=True, fullPath=True)[0]
            self.hierarchy_name = current_object + ' ' + self.hierarchy_name
        self.output_file = output_file
        self.assembly = assembly

        # get material name
        shape_node = cmds.listRelatives(self.name, shapes=True, fullPath=True)[0]

        # get list of unique shading engines
        shading_engines = set(cmds.listConnections(shape_node, t='shadingEngine')) 

        if shading_engines:
            for shading_engine in shading_engines:
                connected_material = cmds.listConnections(shading_engine + ".surfaceShader")
                if connected_material != None:
                    if cmds.nodeType(connected_material[0]) == 'ms_appleseed_material':
                        # this is an appleseed material
                        new_material = Material(self.params, connected_material[0])
                        self.material_nodes.append(new_material)
                        self.shading_nodes = self.shading_nodes + new_material.getShadingNodes()
                        self.colors = self.colors + new_material.colors
                        self.textures = self.textures + new_material.textures
                    else: 
                        cmds.warning("No appleseed material or shader translation connected to {0}.".format(self.name))
        else:
            cmds.warning("No shading engine connected to {0}.".format(self.name))

    def getMaterials(self):
        return self.material_nodes

    def getShadingNodes(self):
        return self.shading_nodes

    def writeXMLInstance(self, doc):
        print('writing object instance: '+ self.name)
        doc.start_element('object_instance name="{0}.0_inst" object="{1}.0"'.format(self.short_name, self.short_name))
        
        if not self.params['export_transformation_blur']:
            write_transform(doc, self.params['scene_scale'], self.name)

        for material in self.material_nodes:
            if material.duplicate_shaders:
                if material.enable_front:
                    doc.append_element('assign_material slot="{0}" side="front" material="{1}"'.format(material.name, material.name))
                if material.enable_back:
                    doc.append_element('assign_material slot="{0}" side="back" material="{1}"'.format(material.name, material.name))
            else:
                if material.enable_front:
                    doc.append_element('assign_material slot="{0}" side="front" material="{1}_front"'.format(material.name, material.name))
                if material.enable_back:
                    doc.append_element('assign_material slot="{0}" side="back" material="{1}_back"'.format(material.name, material.name))
        doc.end_element('object_instance')


#--------------------------------------------------------------------------------------------------
# Assembly class.
#--------------------------------------------------------------------------------------------------

class Assembly():
    def __init__(self, params, name='main_assembly', object_list=False, position_from_object=False):
        check_export_cancelled()
        self.params = params
        self.name = ms_commands.legalizeName(name)
        self.position_from_object = position_from_object
        self.light_objects = []
        self.geo_objects = []
        self.material_objects = []
        self.shading_node_objects = []
        self.color_objects = []
        self.texture_objects = []

        # add shape nodes as geo objects
        if object_list:
            for object in object_list:
                if cmds.nodeType(object) == 'mesh':
                    geo_transform = cmds.listRelatives(object, ad=True, ap=True, fullPath=True)[0]
                    if not (geo_transform in self.geo_objects):
                        geo_filename = self.name + '.obj'
                        geo_filepath = os.path.join(self.params['geo_dir'], geo_filename)
                        self.geo_objects.append(Geometry(self.params, geo_transform, geo_filepath, self.name))
                elif (cmds.nodeType(object) == 'pointLight') and self.params['exportMayaLights']:
                    light_transform = cmds.listRelatives(object, ad=True, ap=True, fullPath=True)[0]
                    if not (light_transform in self.light_objects):
                        self.light_objects.append(Light(self.params, cmds.listRelatives(object, ad=True, ap=True, fullPath=True)[0]))
                elif (cmds.nodeType(object) == 'spotLight') and self.params['exportMayaLights']:
                    light_transform = cmds.listRelatives(object, ad=True, ap=True, fullPath=True)[0]
                    if not (light_transform in self.light_objects):
                        light_object = Light(self.params, cmds.listRelatives(object, ad=True, ap=True, fullPath=True)[0])
                        light_object.model = 'spot_light'
                        light_object.inner_angle = cmds.getAttr(object + '.coneAngle')
                        light_object.outer_angle = cmds.getAttr(object + '.coneAngle') + cmds.getAttr(object + '.penumbraAngle')
                        self.light_objects.append(light_object)

        # add light colors to list
        for light_object in self.light_objects:
            light_color_object = Color(light_object.color_name, light_object.color, light_object.multiplier)
            self.color_objects.append(light_color_object)

        # populate material, shading node and color list
        for geo in self.geo_objects:
            if geo.getMaterials() != None:
                self.material_objects = self.material_objects + geo.getMaterials()
            else:
                cmds.warning("No material connected to {0}.".format(geo.name))
            self.shading_node_objects = self.shading_node_objects + geo.getShadingNodes()
            self.color_objects = self.color_objects + geo.colors
            self.texture_objects = self.texture_objects + geo.textures

        # materials
        unsorted_materials = self.material_objects
        self.material_objects = dict()
        for material in unsorted_materials:
            if not material.name in self.material_objects:
                self.material_objects[material.name] = material
        self.material_objects = self.material_objects.values()

        # shading nodes
        unsorted_shading_nodes = self.shading_node_objects
        self.shading_node_objects = dict()
        for shading_node in unsorted_shading_nodes:
            if shading_node != None:
                if not shading_node.name in self.shading_node_objects:
                    self.shading_node_objects[shading_node.name] = shading_node
        self.shading_node_objects = self.shading_node_objects.values()

        # colors
        unsorted_colors = self.color_objects
        self.color_objects = dict()
        for color in unsorted_colors:
            if not color.name in self.color_objects:
                self.color_objects[color.name] = color
        self.color_objects = self.color_objects.values()

        # textures
        unsorted_textures = self.texture_objects
        self.texture_objects = dict()
        for texture in unsorted_textures:
            if texture!= None:
                if not texture.name in self.texture_objects:
                    self.texture_objects[texture.name] = texture
        self.texture_objects = self.texture_objects.values()

    def writeXML(self, doc):
        print("Writing assembly {0}...".format(self.name))
        doc.start_element('assembly name="{0}"'.format(self.name))

        # write colors
        for col in self.color_objects:
            col.writeXML(doc)

        # write texture objects
        for tex in self.texture_objects:
            tex.writeXMLObject(doc)

        # write texture instances
        for tex in self.texture_objects:
            tex.writeXMLInstance(doc)

        # write bsdfs
        for shading_node in self.shading_node_objects:
            if shading_node.type == 'bsdf':
                shading_node.writeXML(doc)

        # write edfs
        for shading_node in self.shading_node_objects:
            if shading_node.type == 'edf':
                shading_node.writeXML(doc)

        # write surface shaders
        for shading_node in self.shading_node_objects:
            if shading_node.type == 'surface_shader':
                shading_node.writeXML(doc)

        # write materials
        for material in self.material_objects:
            material.writeXML(doc)

        # export and write objects
        for geo in self.geo_objects:
            file_name = ms_commands.legalizeName(geo.short_name)

            doc.start_element('object name="{0}" model="mesh_object"'.format(file_name))

            if self.params['export_deformation_blur']:
                # store the start time of the export
                start_time = cmds.currentTime(query=True)

                motion_samples = self.params['motion_samples']
                sample_interval = 1.0 / (motion_samples - 1)

                doc.start_element('parameters name="filename"')

                for i in range(motion_samples):
                    frame = start_time + sample_interval * i
                    print("Exporting pose {0}...".format(frame))

                    cmds.currentTime(frame)
                    cmds.refresh()

                    obj_filename = "{0}.{1:03}.obj".format(file_name, i)
                    doc.append_parameter("{0:03}".format(i), "{0}/{1}".format(self.params['geo_dir'], obj_filename))

                    # write the OBJ file to disk
                    obj_filepath = os.path.join(self.params['absolute_geo_dir'], obj_filename)
                    check_export_cancelled()
                    self.params['obj_exporter'](geo.name, obj_filepath, overwrite=True)

                doc.end_element('parameters')

                cmds.currentTime(start_time)
            else:
                obj_filename = file_name + ".obj"
                doc.append_parameter('filename', os.path.join(self.params['geo_dir'], obj_filename))

                # write the OBJ file to disk
                obj_filepath = os.path.join(self.params['absolute_geo_dir'], obj_filename)
                check_export_cancelled()
                self.params['obj_exporter'](geo.name, obj_filepath)

            self.params['progress_bar_progress'] += self.params['progress_bar_increments']
            cmds.progressWindow(edit=True, progress=self.params['progress_bar_progress'])

            doc.end_element('object')

        # write lights
        for light_object in self.light_objects:
           light_object.writeXML(doc)

        # write geo object instances
        for geo in self.geo_objects:
            geo.writeXMLInstance(doc)

        doc.end_element('assembly')
        doc.start_element('assembly_instance name="{0}_inst" assembly="{1}"'.format(self.name, self.name))

        # if transformation blur is set output the transform with motion from the position_from_object variable
        if self.params['export_transformation_blur']:
            write_transform(doc, self.params['scene_scale'], self.position_from_object, True, self.params['motion_samples'])
        else:
            write_transform(doc, self.params['scene_scale'])
        doc.end_element('assembly_instance')


#--------------------------------------------------------------------------------------------------
# Scene class.
#--------------------------------------------------------------------------------------------------

class Scene():
    def __init__(self,params):
        check_export_cancelled()
        self.params = params
        self.assembly_list = []
        self.color_objects = dict()
        self.texture_objects = dict()
        self.assembly_objects = dict()

        # setup environment 
        if self.params['environment']:
            env_name = self.params['environment']
            self.environment = Environment(self.params, env_name, (env_name + '_env_shader'), env_name + '_env_edf')

            env_edf_model_enum = cmds.getAttr(env_name + '.model')
            env_edf_params = dict()

            if env_edf_model_enum == 0:
                environment_edf_model = 'constant_environment_edf'

                environment_color = ms_commands.normalizeRGB(cmds.getAttr(env_name + '.constant_exitance')[0])
                self.addColor('constant_env_exitance', environment_color[0:3], environment_color[3])

                env_edf_params['exitance'] = 'constant_env_exitance'

            elif env_edf_model_enum == 1:
                environment_edf_model = 'gradient_environment_edf'

                horizon_exitance = ms_commands.normalizeRGB(cmds.getAttr(env_name + '.gradient_horizon_exitance')[0])
                self.addColor('gradient_env_horizon_exitance', horizon_exitance[0:3], horizon_exitance[3])

                zenith_exitance = ms_commands.normalizeRGB(cmds.getAttr(env_name + '.gradient_zenith_exitance')[0])
                self.addColor('gradient_env_zenith_exitance', zenith_exitance[0:3], zenith_exitance[3])

                env_edf_params['horizon_exitance'] = 'gradient_env_horizon_exitance'
                env_edf_params['zenith_exitance'] = 'gradient_env_zenith_exitance'

            elif env_edf_model_enum == 2:
                environment_edf_model = 'latlong_map_environment_edf'

                exitance_connection = cmds.connectionInfo(env_name + '.latitude_longitude_exitance', sourceFromDestination=True).split('.')[0]
                if exitance_connection:
                    if cmds.nodeType(exitance_connection) == 'file':
                        maya_texture_file = ms_commands.getFileTextureName(exitance_connection)
                        texture_file = ms_commands.convertTexToExr(maya_texture_file, params['absolute_tex_dir'], self.params['overwrite_existing_textures'])
                        self.addTexture(env_name + '_latlong_edf_map', os.path.join(params['tex_dir'], os.path.split(texture_file)[1]))

                        env_edf_params['exitance'] = env_name + '_latlong_edf_map_inst'
                        env_edf_params['exitance_multiplier'] = cmds.getAttr(env_name + '.exitance_multiplier')
                        env_edf_params['horizontal_shift'] = 0.0
                        env_edf_params['vertical_shift'] = 0.0
                else:
                    cmds.error("No texture connected to {0}.latitude_longitude_exitance.".format(env_name))

            elif env_edf_model_enum == 3:
                environment_edf_model = 'mirrorball_map_environment_edf'

                exitance_connection = cmds.connectionInfo(env_name + '.mirror_ball_exitance', sourceFromDestination=True).split('.')[0]
                if exitance_connection:
                    if cmds.nodeType(exitance_connection) == 'file':
                        maya_texture_name = ms_commands.getFileTextureName(exitance_connection)
                        texture_file = ms_commands.convertTexToExr(maya_texture_name, params['absolute_tex_dir'], self.params['overwrite_existing_textures'])
                        self.addTexture(env_name + '_mirrorball_map_environment_edf', os.path.join(params['tex_dir'], os.path.split(texture_file)[1]))

                        env_edf_params['exitance'] = env_name + '_mirrorball_map_environment_edf_inst'
                        env_edf_params['exitance_multiplier'] = cmds.getAttr(env_name + '.exitance_multiplier')
                else:
                    cmds.error("No texture connected to {0}.mirrorball_exitance.".format(env_name))

            else:
                cmds.error("No environment model selected for {0}.".format(env_name))

            self.environment_edf = EnvironmentEdf(env_name + '_env_edf', environment_edf_model, env_edf_params)
            self.environment_shader = EnvironmentShader(env_name + '_env_shader', env_name + '_env_edf')

        else:
            self.environment = None

    def addColor(self, name, value, multiplier=1):
        if not name in self.color_objects:
            self.color_objects[name] = Color(name, value, multiplier)

    def addTexture(self, name, file_name):
        if not name in self.texture_objects:
            self.texture_objects[name] = Texture(name, file_name)

    def writeXML(self, doc):
        doc.start_element('scene')

        # write current camera
        camera_instance = Camera(self.params, self.params['outputCamera'])
        camera_instance.writeXML(doc)

        # write colors
        for col in self.color_objects:
             self.color_objects[col].writeXML(doc)

        # write texture objects
        for tex in self.texture_objects:
            self.texture_objects[tex].writeXMLObject(doc)

        # write texture instances
        for tex in self.texture_objects:
            self.texture_objects[tex].writeXMLInstance(doc)
        
        # if there is an environment write it
        if self.environment:
            self.environment_edf.writeXML(doc)
            self.environment_shader.writeXML(doc)
            self.environment.writeXML(doc)

        # write assemblies
        shape_list = cmds.ls(g=True, v=True, long=True, noIntermediate=True)
        light_list = cmds.ls(lt=True, v=True, long=True)

        self.params['progress_bar_increments'] = 100.0 / len(shape_list)
        self.params['progress_bar_progress'] = 0

        if self.params['export_transformation_blur']:
            for geo in shape_list:
                check_export_cancelled()
                if ms_commands.shapeIsExportable(geo):
                    # add first connected transform to the list
                    geo_transform = cmds.listRelatives(geo, ad=True, ap=True, fullPath=True)[0]
                    geo_assembly = Assembly(self.params, geo_transform + '_assembly', [geo], geo_transform)
                    geo_assembly.writeXML(doc)

            for light in light_list:
                    light_transform = cmds.listRelatives(light, ad=True, ap=True, fullPath=True)[0]
                    light_assembly = Assembly(self.params, light_transform + '_assembly', [light], light_transform)
                    light_assembly.writeXML(doc)
        else:
            assembly = Assembly(self.params, "assembly", light_list + shape_list)
            assembly.writeXML(doc)

        doc.end_element('scene')


#--------------------------------------------------------------------------------------------------
# Output class.
#--------------------------------------------------------------------------------------------------

class Output():
    def __init__(self, params):
        self.params = params

    def writeXML(self, doc):
        doc.start_element('output')
        doc.start_element('frame name="beauty"')
        doc.append_parameter('camera', self.params['outputCamera'])
        doc.append_parameter('color_space', self.params['outputColorSpace'])
        doc.append_parameter('resolution', '{0} {1}'.format(self.params['output_res_width'], self.params['output_res_height']))
        doc.end_element('frame')
        doc.end_element('output')


#--------------------------------------------------------------------------------------------------
# Configurations class.
#--------------------------------------------------------------------------------------------------

class Configurations():
    def __init__(self, params):
        self.params = params

    def writeXML(self, doc):
        doc.start_element("configurations")

        # Emit interactive configuration.
        doc.append_element('configuration name="interactive" base="base_interactive"')

        # Emit final configuration.
        if self.params['customFinalConfigCheck']:
            doc.start_element('configuration name="final" base="base_final"')

            if self.params['customFinalConfigEngine'] == 0:
                doc.append_parameter('lighting_engine', 'pt')
            else:
                doc.append_parameter('lighting_engine', 'drt')
            
            doc.start_element('parameters name="drt"')
            doc.append_parameter('dl_bsdf_samples', self.params['drtDLBSDFSamples'])
            doc.append_parameter('dl_light_samples', self.params['drtDLLightSamples'])
            doc.append_parameter('enable_ibl', self.params['drtEnableIBL'])
            doc.append_parameter('ibl_bsdf_samples', self.params['drtIBLBSDFSamples'])
            doc.append_parameter('ibl_env_samples', self.params['drtIBLEnvSamples'])
            doc.append_parameter('max_path_length', self.params['drtMaxPathLength'])
            doc.append_parameter('rr_min_path_length', self.params['drtRRMinPathLength'])
            doc.end_element("parameters")

            doc.start_element('parameters name="pt"')
            doc.append_parameter('dl_light_samples', self.params['ptDLLightSamples'])

            if self.params['ptEnableCaustics']:
                doc.append_parameter('enable_caustics', 'true')
            else:
                doc.append_parameter('enable_caustics', 'false')

            if self.params['ptEnableDL']:
                doc.append_parameter('enable_dl', 'true')
            else:
                doc.append_parameter('enable_dl', 'false')

            if self.params['ptEnableIBL']:
                doc.append_parameter('enable_ibl', 'true')
            else:
                doc.append_parameter('enable_ibl', 'false')

            doc.append_parameter('ibl_bsdf_samples', self.params['ptIBLBSDFSamples'])
            doc.append_parameter('ibl_env_samples', self.params['ptIBLEnvSamples'])
            doc.append_parameter('max_path_length', self.params['ptMaxPathLength'])

            if self.params['ptNextEventEstimation']:
                doc.append_parameter('next_event_estimation', 'true')
            else:
                doc.append_parameter('next_event_estimation', 'false')

            doc.append_parameter('rr_min_path_length', self.params['ptRRMinPathLength'])
            doc.end_element("parameters")

            doc.start_element('parameters name="generic_tile_renderer"')
            doc.append_parameter('filter_size', self.params['gtrFilterSize'])
            doc.append_parameter('sampler', self.params['gtrSampler'])
            doc.append_parameter('min_samples', self.params['gtrMinSamples'])
            doc.append_parameter('max_samples', self.params['gtrMaxSamples'])
            doc.append_parameter('max_contrast', self.params['gtrMaxContrast'])
            doc.append_parameter('max_variation', self.params['gtrMaxVariation'])
            doc.end_element('parameters')

            doc.end_element("configuration")

        else:
            doc.append_element('configuration name="final" base="base_final"')

        doc.end_element('configurations')


#--------------------------------------------------------------------------------------------------
# Main export function.
#--------------------------------------------------------------------------------------------------

def safe_make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def export_container(render_settings_node):
    params = get_maya_params(render_settings_node)

    # create progress bar
    params['progress_amount'] = 0
    cmds.progressWindow(title='Exporting', progress=params['progress_amount'], status='Exporting ' + render_settings_node, isInterruptable=True)

    # compute the base output directory
    scene_filepath = cmds.file(q=True, sceneName=True)
    scene_basename = os.path.splitext(os.path.basename(scene_filepath))[0]
    if len(scene_basename) == 0:
        scene_basename = "Untitled"
    project_directory = cmds.workspace(q=True, rd=True)
    params['output_directory'] = params['output_directory'].replace("<ProjectDir>", project_directory)
    params['output_directory'] = params['output_directory'].replace("<SceneName>", scene_basename)

    if params['export_animation']:
        start_frame = params['animation_start_frame']
        end_frame = params['animation_end_frame']
    else:
        start_frame = cmds.currentTime(query=True)
        end_frame = start_frame

    start_time = time.time()

    current_frame = start_frame
    original_time = cmds.currentTime(query=True)

    # loop through frames and perform export
    while (current_frame  <= end_frame):
        # todo: add check for Escape being held down here to cancel an export

        # todo: is this necessary, since we're already doing it when exporting geometry?
        cmds.currentTime(current_frame)
        frame_name = '{0:04}'.format(int(current_frame))

        # compute the output file path
        filename = params['file_name']
        filename = filename.replace("<SceneName>", scene_basename)
        filename = filename.replace("#", frame_name)
        filepath = os.path.join(params['output_directory'], filename)

        # directory for geometry
        params['geo_dir'] = os.path.join(frame_name, "geometry")
        params['absolute_geo_dir'] = os.path.join(params['output_directory'], params['geo_dir'])

        # directory for textures
        params['tex_dir'] = 'textures'
        if params['animatedTextures']:
            params['tex_dir'] = os.path.join(frame_name, params['tex_dir'])
        params['absolute_tex_dir'] = os.path.join(params['output_directory'], params['tex_dir'])

        # create directories if they don't exist yet
        safe_make_dirs(params['absolute_geo_dir'])
        safe_make_dirs(params['absolute_tex_dir'])

        print("Opening output file {0}...".format(filepath))

        doc = WriteXml(filepath)
        doc.append_line('<?xml version="1.0" encoding="UTF-8"?>')
        doc.append_line('<!-- File generated by Mayaseed version {0} -->'.format(ms_commands.MAYASEED_VERSION))

        doc.start_element('project')
        scene_element = Scene(params)
        scene_element.writeXML(doc)
        output_element = Output(params)
        output_element.writeXML(doc)
        config_element = Configurations(params)
        config_element.writeXML(doc)
        doc.end_element('project')
        doc.close()

        current_frame += 1

    cmds.currentTime(original_time)
    cmds.select(render_settings_node)

    # Compute and report export time.
    export_time = time.time() - start_time
    export_message = "Export completed in {0:.1f} seconds.".format(export_time)
    print(export_message)

    # end progress bar
    cmds.progressWindow(endProgress=1)

    cmds.confirmDialog(title="Export Completed", icon='information', message=export_message, button="OK")

def export(render_settings_node):
    if cmds.getAttr(render_settings_node + '.profile_export'):
        import cProfile
        command = 'import ms_export\nms_export.export_container("' + render_settings_node + '")'
        cProfile.run(command)
    else:
        export_container(render_settings_node)
