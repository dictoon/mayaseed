
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
    params['animated_textures'] = cmds.getAttr(render_settings_node + '.export_animated_textures')
    params['scene_scale'] = 1.0

    if not params['export_animation']:
        params['motion_samples'] = 1
    elif params['motion_samples'] < 2:
        ms_commands.warning('Motion samples must be >= 2, using 2.')
        params['motion_samples'] = 2

    # Advanced options.
    if cmds.listConnections(render_settings_node + '.environment'):
        params['environment'] = cmds.listRelatives(cmds.listConnections(render_settings_node + '.environment')[0])[0]
    else:
        params['environment'] = False

    # Cameras.
    # params['sceneCameraExportAllCameras'] = cmds.checkBox('ms_sceneCameraExportAllCameras', query=True, value=True)
    params['export_all_cameras_as_thinlens'] = cmds.getAttr(render_settings_node + '.export_all_cameras_as_thinlens')

    # Output.
    if cmds.listConnections(render_settings_node + '.camera'):
        params['output_camera'] = cmds.listConnections(render_settings_node + '.camera')[0]
    else:
        cmds.warning('No camera connected to {0}, using "persp".'.format(render_settings_node))
        params['output_camera'] = 'persp'

    if cmds.getAttr(render_settings_node + '.color_space') == 1:
        params['output_color_space'] = 'linear_rgb'
    elif cmds.getAttr(render_settings_node + '.color_space') == 2:
        params['output_color_space'] = 'spectral'
    elif cmds.getAttr(render_settings_node + '.color_space') == 3:
        params['output_color_space'] = 'ciexyz'
    else:
        params['output_color_space'] = 'srgb'

    params['output_res_width'] = cmds.getAttr(render_settings_node + '.width')
    params['output_res_height'] = cmds.getAttr(render_settings_node + '.height')

    # Custom final configuration.

    params['custom_final_config_check'] = cmds.getAttr(render_settings_node + '.export_custom_final_config')
    params['custom_final_config_engine'] = cmds.getAttr(render_settings_node + '.final_lighting_engine')
    if params['custom_final_config_engine'] == 0:
        params['custom_final_config_engine'] = 'pt'
    else:
        params['custom_final_config_engine'] = 'drt'

    params['drt_dl_bsdf_samples'] = cmds.getAttr(render_settings_node + '.drt_dl_bsdf_samples')
    params['drt_dl_light_samples'] = cmds.getAttr(render_settings_node + '.drt_dl_light_samples')
    params['drt_enable_ibl'] = cmds.getAttr(render_settings_node + '.drt_enable_ibl')
    params['drt_ibl_bsdf_samples'] = cmds.getAttr(render_settings_node + '.drt_ibl_bsdf_samples')
    params['drt_ibl_env_samples'] = cmds.getAttr(render_settings_node + '.drt_ibl_env_samples')
    params['drt_max_path_length'] = cmds.getAttr(render_settings_node + '.drt_max_path_length')
    params['drt_rr_min_path_length'] = cmds.getAttr(render_settings_node + '.drt_rr_min_path_length')

    params['pt_dl_light_samples'] = cmds.getAttr(render_settings_node + '.pt_dl_light_samples')
    params['pt_enable_caustics'] = cmds.getAttr(render_settings_node + '.pt_enable_caustics')
    params['pt_enable_dl'] = cmds.getAttr(render_settings_node + '.pt_enable_dl')
    params['pt_enable_ibl'] = cmds.getAttr(render_settings_node + '.pt_enable_ibl')
    params['pt_ibl_bsdf_samples'] = cmds.getAttr(render_settings_node + '.pt_ibl_bsdf_samples')
    params['pt_ibl_env_samples'] = cmds.getAttr(render_settings_node + '.pt_ibl_env_samples')
    params['pt_max_path_length'] = cmds.getAttr(render_settings_node + '.pt_max_path_length')
    params['pt_next_event_estimation'] = cmds.getAttr(render_settings_node + '.pt_next_event_estimation')
    params['pt_rr_min_path_length'] = cmds.getAttr(render_settings_node + '.pt_rr_min_path_length')

    params['gtr_filter_size'] = cmds.getAttr(render_settings_node + '.gtr_filter_size')
    params['gtr_min_samples'] = cmds.getAttr(render_settings_node + '.gtr_min_samples')
    params['gtr_max_samples'] = cmds.getAttr(render_settings_node + '.gtr_max_samples')
    params['gtr_max_contrast'] = cmds.getAttr(render_settings_node + '.gtr_max_contrast')
    params['gtr_max_variation'] = cmds.getAttr(render_settings_node + '.gtr_max_variation')

    if cmds.getAttr(render_settings_node + '.gtr_sampler') == 0:
        params['gtr_sampler'] = 'uniform'
    else:
        params['gtr_sampler'] = 'adaptive'

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
    sample_increment = 1.0
    if params['motion_samples'] > 1:
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
                print '?? adding transform sample to', transform.name
                transform.add_transform_sample()
                for descendant_transform in (transform.descendant_transforms + transform.child_transforms):
                    print '?? adding transform sample to', descendant_transform.name
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

        #check for incoming connections to transform attributes and set the is_animated var
        self.is_animated = False
        maya_transform_attribute_list = ['translate', 'translateX', 'translateY', 'translateZ', 
                                         'rotate', 'rotateX', 'rotateY', 'rotateZ', 
                                         'scale','scaleX','scaleY','scaleZ', 'visibility']

        for attribute in maya_transform_attribute_list:
            if cmds.listConnections(self.name + '.' + attribute) is not None:
                self.is_animated = True
                break

        # get children
        mesh_names = cmds.listRelatives(self.name, type='mesh', fullPath=True)
        if mesh_names is not None:
            for mesh_name in mesh_names:
                self.child_meshes.append(MMesh(params, mesh_name, self))

        light_names = cmds.listRelatives(self.name, type='light', fullPath=True)
        if light_names is not None:
            for light_name in light_names:
                self.child_lights.append(MLight(params, light_name, self))

        camera_names = cmds.listRelatives(self.name, type='camera', fullPath=True)
        if camera_names is not None:
            for camera_name in camera_names:
                self.child_cameras.append(MCamera(params, camera_name, self))

        transform_names = cmds.listRelatives(self.name, type='transform', fullPath=True)
        if transform_names is not None:
            for transform_name in transform_names:
                new_transform = MTransform(params, transform_name, self)
                self.child_transforms.append(new_transform)
                print '?? just appended', new_transform.name

                # add descendants
                self.descendant_cameras += new_transform.child_cameras
                self.descendant_meshes += new_transform.child_meshes
                self.descendant_lights += new_transform.child_lights
                self.descendant_transforms += new_transform.child_transforms

    def add_transform_sample(self):
        self.matrices.append(cmds.xform(self.name, query=True, matrix=True))


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
        self.matrices = [[1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]]

    def emit_xml(self, doc):
        doc.start_element('transform time="%s"' % self.time)
        doc.append_element('scaling value="%s"' % self.scaling_value)

        for matrix in self.matrices:
            doc.start_element('matrix')
            doc.append_line('%.15f %.15f %.15f %.15f' % (matrix[0], matrix[4], matrix[8],  matrix[12]))
            doc.append_line('%.15f %.15f %.15f %.15f' % (matrix[1], matrix[5], matrix[9],  matrix[13]))
            doc.append_line('%.15f %.15f %.15f %.15f' % (matrix[2], matrix[6], matrix[10], matrix[14]))
            doc.append_line('%.15f %.15f %.15f %.15f' % (matrix[3], matrix[7], matrix[11], matrix[15]))
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
        self.file_names = None
        self.instances = []

    def instantiate(self):
        object_instance = AsObjectInstance(self)
        self.instances.append(object_instance)
        return object_instance

    def emit_xml(self, doc):
        doc.start_element('object name="%s" model="%s"' % (self.name, self.model))
        self.file_names.emit_xml(doc)
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
        self.transforms = []

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

        for transform in self.transforms:
            transform.emit_xml(doc)

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

class AsScene():

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

class AsProject():

    """ Class representing appleseed Project entity """

    def __init__(self):
        scene = None
        output = None
        configurations = None

    def emit_xml(self, doc):
        scene.emit_xml(doc)
        output.emit_xml(doc)
        configurations.emit_xml(doc)

#--------------------------------------------------------------------------------------------------
# traslate_maya_scene function.
#--------------------------------------------------------------------------------------------------

def translate_maya_scene(params, maya_scene):

    """ Main function for converting a cached maya scene into an appleseed object hierarchy """

    # create dict for storing appleseedobject models into
    # the key will be the file path to save the project too
    as_object_models = dict()

    # initialize frame list with single default value 
    frame_list = [int(cmds.currentTime(query=True))]

    # compute the base output directory
    scene_filepath = cmds.file(q=True, sceneName=True)
    scene_basename = os.path.splitext(os.path.basename(scene_filepath))[0]
    if len(scene_basename) == 0:
        scene_basename = "Untitled"
    project_directory = cmds.workspace(q=True, rd=True)
    params['output_directory'] = params['output_directory'].replace("<ProjectDir>", project_directory)
    params['output_directory'] = params['output_directory'].replace("<SceneName>", scene_basename)

    # compute the output file path
    base_file_name = params['file_name']
    base_file_name = params['file_name'].replace("<SceneName>", scene_basename)

    # if animation export is on populate frame list with correct frame numbers
    if params['export_animation']:
        frame_list = range(params['animation_start_frame'], params['animation_end_frame'] + 1)

    for frame_number in frame_list:
        ms_commands.info('exporting frame %i' % frame_number)

        # mb_sample_number is list of indices that should be iterated over in the cached maya scene for objects with motion blur
        # if animation export is turned off it should be initialised to the first sample
        mb_sample_number_list = range(params['motion_samples'])

        non_mb_sample_number = None
        if params['export_animation']:
            non_mb_sample_number = frame_number - params['animation_start_frame']
        else:
            non_mb_sample_number = 0

        # is animation export is turned on set the sample list according to the current frame and the sample count
        if params['export_animation']:
            mb_sample_number_list = range(params['motion_samples'])
            for i in range(params['motion_samples']):
                mb_sample_number_list[i] += (frame_number - params['animation_start_frame']) * (params['motion_samples'] - 1)

        # begin construction of as object hierarchy *************************************************

        as_project = AsProject()

        # create output and frame objects
        as_output = AsOutput()
        as_project.output = as_output
        as_frame = AsFrame()
        as_output.frames.append(as_frame)
        # note: frame camera is set when the camera is retrieved for the scene element
        as_frame.resolution = AsParameter('resolution', '%i %i' % (params['output_res_width'], params['output_res_height']))

        # create configurations object
        as_configurations = AsConfigurations()
        as_project.configurations = as_configurations

        # create interactive config
        interactive_config = AsConfiguration()
        as_configurations.configurations.append(interactive_config)
        interactive_config.name = 'interactive'
        interactive_config.base = 'base_interactive'

        # create final config
        final_config = AsConfiguration()
        as_configurations.configurations.append(final_config)
        final_config.name = 'final'
        final_config.base = 'base_final'

        if ['custom_final_config_check']:
            final_config.parameters.append(AsParameter('lighting_engine', params['custom_final_config_engine']))
            
            pt_paramaters = AsParameters()
            pt_paramaters.name = 'pt'
            pt_paramaters.parameters.append(AsParameter('dl_light_samples',      params['pt_dl_light_samples']))
            pt_paramaters.parameters.append(AsParameter('enable_caustics',       params['pt_enable_caustics']))
            pt_paramaters.parameters.append(AsParameter('enable_dl',             params['pt_enable_dl']))
            pt_paramaters.parameters.append(AsParameter('enable_ibl',            params['pt_enable_ibl']))
            pt_paramaters.parameters.append(AsParameter('ibl_env_samples',       params['pt_ibl_env_samples']))
            pt_paramaters.parameters.append(AsParameter('ibl_bsdf_samples',      params['pt_ibl_bsdf_samples']))
            pt_paramaters.parameters.append(AsParameter('max_path_length',       params['pt_max_path_length']))
            pt_paramaters.parameters.append(AsParameter('next_event_estimation', params['pt_next_event_estimation']))
            pt_paramaters.parameters.append(AsParameter('rr_min_path_length',    params['pt_rr_min_path_length']))
            final_config.parameters.append(pt_paramaters)

            drt_parameters = AsParameters()
            drt_parameters.name = 'drt'
            drt_parameters.parameters.append(AsParameter('dl_bsdf_samples',      params['drt_dl_bsdf_samples']))
            drt_parameters.parameters.append(AsParameter('dl_light_samples',     params['drt_dl_light_samples']))
            drt_parameters.parameters.append(AsParameter('enable_ibl',           params['drt_enable_ibl']))
            drt_parameters.parameters.append(AsParameter('ibl_bsdf_samples',     params['drt_ibl_bsdf_samples']))
            drt_parameters.parameters.append(AsParameter('ibl_env_samples',      params['drt_ibl_env_samples']))
            drt_parameters.parameters.append(AsParameter('max_path_length',      params['drt_max_path_length']))
            drt_parameters.parameters.append(AsParameter('rr_min_path_length',   params['drt_rr_min_path_length']))
            final_config.parameters.append(drt_parameters)

            generic_tile_renderer_parameters = AsParameters()
            generic_tile_renderer_parameters.name = 'generic_tile_renderer'
            generic_tile_renderer_parameters.parameters.append(AsParameter('filter_size',   params['gtr_filter_size']))
            generic_tile_renderer_parameters.parameters.append(AsParameter('sampler',       params['gtr_sampler']))
            generic_tile_renderer_parameters.parameters.append(AsParameter('min_samples',   params['gtr_min_samples']))
            generic_tile_renderer_parameters.parameters.append(AsParameter('max_samples',   params['gtr_max_samples']))
            generic_tile_renderer_parameters.parameters.append(AsParameter('max_contrast',  params['gtr_max_contrast']))
            generic_tile_renderer_parameters.parameters.append(AsParameter('max_variation', params['gtr_max_variation']))
            final_config.parameters.append(generic_tile_renderer_parameters)

        # begin scene object
        as_project.scene = AsScene()

        # retrieve camera from maya scene cache and create as camera
        for transform in maya_scene:
            for camera in transform.child_cameras + transform.descendant_cameras:
                if camera.transform.name == params['output_camera']:
                    # set camera parameter in as frame
                    as_frame.camera = AsParameter('camera', camera.safe_name)

                    # generic camera settings
                    as_camera = AsCamera()
                    as_camera.name = camera.safe_name
                    as_camera.film_dimensions = AsParameter('film_dimensions', '%i %i' % (camera.film_width, cameras.film_height))
                    as_camera.focal_length = AsParameter('focal_length', camera.focal_length)
                    
                    # dof specific camera settings
                    if camera.dof or params['export_all_cameras_as_thinlens']:
                        as_camera.model = 'thinlens_camera'
                        as_camera.focal_distance = AsParameter('focal_distance', cameras.focal_distance)
                        as_camera.f_Stop = AsParameter('f_Stop', camera.f_stop)
                    else:
                        as_camera.model = 'pinhole_camera'

                    # create sample number list
                    if params['export_camera_blur']:
                        camera_sample_number_list = mb_sample_number_list
                    else:
                        camera_sample_number_list = non_mb_sample_number

                    # add transforms
                    for sample_number in camera_sample_number_list:
                        as_transform = AsTransform()
                        as_transform.matrix = camera.world_space_matrices[sample_number]
                        as_camera.transforms.append(as_transform)

        # construct assembly hierarchy
        # start by creating a root assembly to hold all other assemblies
        root_assembly = AsAssembly()
        root_assembly.name = 'root_assembly'
        as_project.scene.assemblies.append(root_assembly)
        as_project.scene.assembly_instances.append(root_assembly.instantiate())

        for transform in maya_scene:
            construct_transform_descendents(root_assembly, root_assembly, [], transform, mb_sample_number_list, non_mb_sample_number, params['export_camera_blur'], params['export_transformation_blur'], params['export_deformation_blur'])

        # end construction of as project hierarchy ************************************************
        
        # add project to dict with the project file path as the key
        file_name = base_file_name.replace("#", str(frame_number).zfill(5))
        project_file_path = os.path.join(params['output_directory'], file_name)

        as_object_models[project_file_path] = as_project
        
    return as_object_models

#--------------------------------------------------------------------------------------------------
# construct_transform_descendents function.
#--------------------------------------------------------------------------------------------------

def construct_transform_descendents(root_assembly, parent_assembly, matrix_stack, maya_transform, mb_sample_number_list, non_mb_sample_number, camera_blur, transformation_blur, object_blur):

    """ this function recursivley builds an as object hierarchy from a maya scene """

    print '??', len(maya_transform.matrices)
    print '??', maya_transform.matrices
    print '??', maya_transform.name
    print '?? sample', non_mb_sample_number

    current_assembly = parent_assembly
    current_matrix_stack = matrix_stack + [maya_transform.matrices[non_mb_sample_number]]

    if maya_transform.is_animated and (transformation_blur == True):

        current_assembly = AsAssembly()
        current_assembly.name = maya_transform.safe_name
        parent_assembly.assemblies.append(current_assembly)
        current_matrix_stack = []

        for i in mb_sample_number_list:
            new_transform = MTransform()
            new_transform.matrices = [maya_transform.matrix[i]] + matrix_stack
            current_assembly.transforms.append(new_transform)

    for transform in maya_transform.child_transforms:
        construct_transform_descendents(root_assembly, current_assembly, current_matrix_stack, transform, mb_sample_number_list, non_mb_sample_number, camera_blur, transformation_blur, object_blur)

    for light in maya_transform.child_lights:
        
        light_color = AsColor()
        light_color.name = light.name + '_color'
        light_color.RGB_color = light.color
        light_color.multiplier = light.multiplier
        current_assembly.colors.append(light_color)
        
        new_light = AsLight()
        new_light.name = light.safe_name
        new_light.color = AsParameter('color', light_color.name)
        new_light.transform = AsTransform()
        if current_matrix_stack == []:
            new_light.transform.martices = current_matrix_stack


        if light.model == 'spotLight':
            new_light.model = 'spot_light'
            new_light.inner_angle = parameter('inner_angle', light.inner_angle)
            new_light.outer_angle = parameter('outer_angle', light.outer_angle)
        else:
            new_light.model = 'point_light'

        current_assembly.lights.append(new_light)

    for mesh in maya_transform.child_meshes:
        # for now we wont be supporting instantiating objects
        # when the time comes i will add a function call here to find 
        # if the mesh has been defined somewhere in the assembly heriarchy already and instantiate it if so
        new_mesh = AsObject()
        new_mesh.name = mesh.safe_name
        if not object_blur:
            new_mesh.file_names = AsParameter('filename', mesh.mesh_file_names[non_mb_sample_number])
        else:
            file_names = AsParameters('filename')
            for i in mb_sample_number_list:
                file_names.parameters.append(AsParameter(i - mb_sample_number_list[0], mesh.mesh_file_names[i]))
            new_mesh.file_names = file_names

        current_assembly.objects.append(new_mesh)
        mesh_instance = new_mesh.instantiate()
        mesh_transform = AsTransform()
        if current_matrix_stack == []:
            mesh_transform.matrices = current_matrix_stack
        mesh_instance.transforms.append(mesh_transform)

        # translate materials and assign
        for maya_material in mesh.materials:
            as_materials = construct_appleseed_material_network(root_assembly, maya_material)
            if as_materials[0] is not None:
                mesh_instance.material_assignments.append(AsObjectInstanceMaterialAssignment(maya_material.safe_name, 'front', as_materials[0].name))
            if as_materials[1] is not None:
                mesh_instance.material_assignments.append(AsObjectInstanceMaterialAssignment(maya_material.safe_name, 'back', as_materials[1].name))

        current_assembly.object_instances.append(mesh_instance)

#--------------------------------------------------------------------------------------------------
# construct_appleseed_material_network function.
#--------------------------------------------------------------------------------------------------

def construct_appleseed_material_network(root_assembly, ms_material):
    
    """ constructs a AsMaterial from an MMsMaterial """

    materials = [None, None]
    
    # check if material already exists in root_assembly
    for material in root_assembly.materials:
        if material.name == (ms_material.name + '_front') and (ms_material.enable_front):
            materials[0] = material
        elif material.name == (ms_material.name + '_back') and (ms_material.enable_back):
            material[1] = material
        if not materials == [None, None]:
            return materials

    # if the materials are not yet defined construct them
    if ms_material.enable_front:
        front_material = AsMaterial()
        front_material.name = ms_material.safe_name + '_front'
        if ms_material.bsdf_front is not None:
            new_bsdf = build_as_shading_nodes(root_assembly, ms_material.bsdf_front)
            front_material.bsdf = AsParameter('bsdf', new_bsdf.name)
        if ms_material.bsdf_front is not None:
            new_bsdf = build_as_shading_nodes(root_assembly, ms_material.bsdf_front)
            front_material.bsdf = AsParameter('edf', new_bsdf.name)
        if ms_material.bsdf_front is not None:
            new_bsdf = build_as_shading_nodes(root_assembly, ms_material.bsdf_front)
            front_material.bsdf = AsParameter('surface_shader', new_bsdf.name)
        if ms_material.normal_map_front is not None:
            new_texture = AsTexture()
            new_texture.name = ms_material.normal_map_front.safe_name
            new_texture.file_name = AsParameter('filename', ms_material.normal_map_front.resolved_image_name)
            root_assembly.textures.append(new_texture)
            new_texture_instance = new_texture.instantiate()
            root_assembly.texture_instances.append(new_texture_instance)
            front_material.normal_map = AsParameter('normal_map', new_texture_instance.name)
        if ms_material.alpha_map_front is not None:
            new_texture = AsTexture()
            new_texture.name = ms_material.alpha_map_front.safe_name
            new_texture.file_name = AsParameter('filename', ms_material.alpha_map_front.resolved_image_name)
            root_assembly.textures.append(new_texture)
            new_texture_instance = new_texture.instantiate()
            root_assembly.texture_instances.append(new_texture_instance)
            front_material.alpha_map_front = AsParameter('alpha_map_front', new_texture_instance.name)
        
        root_assembly.materials.append(front_material)
        materials[0] = front_material

    if ms_material.enable_back:
        back_material = AsMaterial()
        back_material.name = ms_material.safe_name + '_back'
        if ms_material.bsdf_back is not None:
            new_bsdf = build_as_shading_nodes(root_assembly, ms_material.bsdf_back)
            back_material.bsdf = AsParameter('bsdf', new_bsdf.name)
        if ms_material.bsdf_back is not None:
            new_bsdf = build_as_shading_nodes(root_assembly, ms_material.bsdf_back)
            back_material.bsdf = AsParameter('edf', new_bsdf.name)
        if ms_material.bsdf_back is not None:
            new_bsdf = build_as_shading_nodes(root_assembly, ms_material.bsdf_back)
            back_material.bsdf = AsParameter('surface_shader', new_bsdf.name)
        if ms_material.normal_map_back is not None:
            new_texture = AsTexture()
            new_texture.name = ms_material.normal_map_back.safe_name
            new_texture.file_name = AsParameter('filename', ms_material.normal_map_back.resolved_image_name)
            root_assembly.textures.append(new_texture)
            new_texture_instance = new_texture.instantiate()
            root_assembly.texture_instances.append(new_texture_instance)
            back_material.normal_map = AsParameter('normal_map', new_texture_instance.name)
        if ms_material.alpha_map_back is not None:
            new_texture = AsTexture()
            new_texture.name = ms_material.alpha_map_back.safe_name
            new_texture.file_name = AsParameter('filename', ms_material.alpha_map_back.resolved_image_name)
            root_assembly.textures.append(new_texture)
            new_texture_instance = new_texture.instantiate()
            root_assembly.texture_instances.append(new_texture_instance)
            back_material.alpha_map_back = AsParameter('alpha_map_back', new_texture_instance.name)

        root_assembly.materials.append(back_material)
        materials[1] = back_material

        return materials


#--------------------------------------------------------------------------------------------------
# build_as_shading_nodes function.
#--------------------------------------------------------------------------------------------------

def build_as_shading_nodes(root_assembly, current_maya_shading_node):

    """ takes a maya MMsShading node and returns a AsEdf, AsBsdf or AsSurfaceSahder """

    current_shading_node = None
    if current_maya_shading_node.type == 'bsdf':
        current_shading_node = AsBsdf()
        root_assembly.bsdfs.append(current_shading_node)
    elif current_maya_shading_node.type == 'edf':
        current_shading_node = AsEdf()
        root_assembly.edfs.append(current_shading_node)
    elif current_maya_shading_node.type == 'surface_shader':
        current_shading_node = AsSurfaceShader()
        root_assembly.surface_shaders.append(current_shading_node)
    
    current_shading_node.name = current_maya_shading_node.safe_name
    current_shading_node.model = current_maya_shading_node.model

    root_assembly.shading_nodes.append(current_shading_node)

    for attrib_key in current_maya_shading_node.attribs:
        if current_maya_shading_node.attribs[attrib_key].__class__.__name__ == 'MMsShadingNode':
            new_shading_node = None
            for shading_node in shading_nodes:
                if shading_node.name == current_maya_shading_node.attribs[attrib_key].safe_name:
                    new_shading_node = shading_node

            if new_shading_node is None:
                new_shading_node = build_as_shading_nodes(root_assembly, current_maya_shading_node.attribs[attrib_key])

            new_shading_node_parameter = AsParameter(attrib_key, new_shadin_node.name)
            current_shading_node.parameters.append(new_shadin_node_parameter)

        elif current_maya_shading_node.attribs[attrib_key].__class__.__name__ == 'MFile':
            new_texture_entity = None
            for texture in textures:
                if texture.name == current_maya_shading_node[attrib_key].safe_name:
                    new_texture_entity = texture

            if new_texture_entity is None:
                new_texture_entity = AsTexture()
                new_texture_entity.name = current_maya_shading_node[attrib_key].safe_name
                new_texture_entity.file_name = AsParameter('filename', current_maya_shading_node.attribs[attrib_key].image_name)
                root_assembly.textures.append(new_texture_entity)

            new_texture_instance = new_texture_entity.instance()
            root_assembly.texture_instances.append(new_texture_instance)

            new_shading_node_parameter = AsParameter(attrib_key, new_texture_instance.name)
            current_shading_node.parameters.append(new_shadin_node_parameter)

        elif current_maya_shading_node.attribs[attrib_key].__class__.__name__ == 'MColorConnection':
            new_color_entity = None
            for color in colors:
                if color.name == current_maya_shading_node.attribs[attrib_key].safe_name:
                    new_color_entity = color

            if color is None:
                new_color_entity = AsColor()
                new_color_entity.name = current_maya_shading_node.attribs[attrib_key].safe_name
                new_color_entity.RGB_color = current_maya_shading_node.attribs[attrib_key].normalized_color
                new_color_entity.multiplier.value = current_maya_shading_node.attribs[attrib_key].multiplier
                root_assembly.colors.append(new_color_entity)

            new_shading_node_parameter = AsParameter(attrib_key, new_color_entity.name)
            current_shading_node.parameters.append(new_shadin_node_parameter)
            
        elif current_maya_shading_node.attribs[attrib_key].__class__.__name__ == 'str':
            new_shading_node_parameter = AsParameter(attrib_key, current_maya_shading_node.attribs[attrib_key])
            current_shading_node.parameters.append(new_shadin_node_parameter)

    return current_shading_node


#--------------------------------------------------------------------------------------------------
# export_container_new function.
#--------------------------------------------------------------------------------------------------

def export_container_new(render_settings_node):

    """ This function triggers the 3 main processes in exporting, scene caching, translation and saving"""
    
    export_start_time = time.time()
    
    params = get_maya_params(render_settings_node)
    maya_scene = get_maya_scene(params)

    scene_cache_finish = time.time()
    ms_commands.info('Scene cached for translation in %.2f seconds' % (scene_cache_finish - export_start_time))

    as_object_models = translate_maya_scene(params, maya_scene)

    scene_translation_finish = time.time() 
    ms_commands.info('Scene translated in %.2f seconds' % (scene_translation_finish - scene_cache_finish))

    for as_object_model_key in as_object_models:

        cmds.info('Saving %s' % as_object_model_key)
        doc = WriteXml(as_object_model_key)
        doc.append_line('<?xml version="1.0" encoding="UTF-8"?>')
        doc.append_line('<!-- File generated by Mayaseed version {0} -->'.format(ms_commands.MAYASEED_VERSION))
        as_object_models[as_object_model_key].emit_xml(doc)
        doc.close()

    save_finish_time = time.time() 

    export_finish_time = time.time() 

    cmds.info('Export finished in %.2f seconds, See the script editor for details' % (export_finish_time - export_start_time))


#--------------------------------------------------------------------------------------------------
# export_new function.
#--------------------------------------------------------------------------------------------------

def export_new(render_settings_node):

    """ This function is a wrapper for export_container so that we can profile the export easily """ 

    if cmds.getAttr(render_settings_node + '.profile_export'):
        import cProfile
        command = 'import ms_export\nms_export.export_container_new("' + render_settings_node + '")'
        cProfile.run(command)
    else:
        export_container_new(render_settings_node)
