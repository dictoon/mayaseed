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
import re
import ms_commands
import os

# the get() functions purpose is to retreive all information from the ms_rendersettings node as a dict

#****************************************************************************************************************************************************************************************************
# get() function ************************************************************************************************************************************************************************************
#****************************************************************************************************************************************************************************************************

def get(render_settings_node):
    print('getting params from ui')
    #compile regular expression to check for non numeric characters
    is_numeric = re.compile('^[0-9]+$')
    
    params = {'error':False}

    params['entityDefs'] = ms_commands.getEntityDefs(os.path.join(ms_commands.ROOT_DIRECTORY, 'scripts', 'appleseedEntityDefs.xml'))
    
    #main settings
    params['output_dir'] = cmds.getAttr(render_settings_node + '.output_directory')
    params['file_name'] = cmds.getAttr(render_settings_node + '.output_file')
    params['convert_shading_nodes'] = cmds.getAttr(render_settings_node + '.convert_shading_nodes_to_textures')
    params['convert_textures_to_exr'] = cmds.getAttr(render_settings_node + '.convert_textures_to_exr')
    params['overwrite_existing_exrs'] = cmds.getAttr(render_settings_node + '.overwrite_existing_exrs')
    params['file_name'] = cmds.getAttr(render_settings_node + '.output_file')
    params['export_camera_blur'] = cmds.getAttr(render_settings_node + '.export_camera_blur')
    params['export_transformation_blur'] = cmds.getAttr(render_settings_node + '.export_transformation_blur')
    params['export_deformation_blur'] = cmds.getAttr(render_settings_node + '.export_deformation_blur')
    params['motion_samples'] = cmds.getAttr(render_settings_node + '.motion_samples')
    params['export_animation'] = cmds.getAttr(render_settings_node + '.export_animation')
    params['animation_start_frame'] = cmds.getAttr(render_settings_node + '.animation_start_frame')
    params['animation_end_frame'] = cmds.getAttr(render_settings_node + '.animation_end_frame')
    params['animated_textures'] = cmds.getAttr(render_settings_node + '.export_animated_textures')
    params['scene_scale'] = 1
    
    #Advanced options
    #scene
    if cmds.listConnections(render_settings_node + '.environment'):
        params['environment'] = cmds.listRelatives(cmds.listConnections(render_settings_node + '.environment')[0])[0]
    else:
        params['environment'] = False

    #cameras
    params['scene_camera_default_thin_lens'] = cmds.getAttr(render_settings_node + '.export_all_cameras_as_thinlens')
    
    #assemblies
    params['mat_double_shade'] = cmds.getAttr(render_settings_node + '.double_sided_shading')

    # output 
    if cmds.listConnections(render_settings_node + '.camera'):
        params['output_camera'] = cmds.listConnections(render_settings_node + '.camera')[0]
    else:
        params['output_camera'] = 'perspShape'
        #raise RuntimeError('no camera connected to ' + render_settings_node)
    
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

    # configuration
    # custom Final config
    params['custom_final_config_check'] = cmds.getAttr(render_settings_node + '.export_custom_final_config')
    params['custom_final_config_engine'] = cmds.getAttr(render_settings_node + '.final_lighting_engine')

    params['custom_final_config_min_samples'] = cmds.getAttr(render_settings_node + '.min_samples')
    params['custom_final_config_max_samples'] = cmds.getAttr(render_settings_node + '.max_samples')


    params['drt_DL_BSDF_samples'] = cmds.getAttr(render_settings_node + '.drt_dl_bsdf_samples')
    params['drt_DL_Light_samples'] = cmds.getAttr(render_settings_node + '.drt_dl_light_samples')
    params['drt_enable_IBL'] = cmds.getAttr(render_settings_node + '.drt_enable_ibl')
    params['drt_IBL_BSDF_samples'] = cmds.getAttr(render_settings_node + '.drt_ibl_bsdf_samples')
    params['drt_IBL_env_samples'] = cmds.getAttr(render_settings_node + '.drt_ibl_env_samples')
    params['drt_max_path_length'] = cmds.getAttr(render_settings_node + '.drt_max_path_length')
    params['drt_RR_min_path_length'] = cmds.getAttr(render_settings_node + '.drt_rr_min_path_length')

    params['pt_DL_light_samples'] = cmds.getAttr(render_settings_node + '.pt_dl_light_samples')
    params['pt_enable_caustics'] = cmds.getAttr(render_settings_node + '.pt_enable_caustics')
    params['pt_enable_DL'] = cmds.getAttr(render_settings_node + '.pt_enable_dl')
    params['pt_enable_IBL'] = cmds.getAttr(render_settings_node + '.pt_enable_ibl')
    params['pt_IBL_BSDF_samples'] = cmds.getAttr(render_settings_node + '.pt_ibl_bsdf_samples')
    params['pt_IBL_env_samples'] = cmds.getAttr(render_settings_node + '.pt_ibl_env_samples')
    params['pt_max_path_length'] = cmds.getAttr(render_settings_node + '.pt_max_path_length')
    params['pt_next_event_estimation'] = cmds.getAttr(render_settings_node + '.pt_next_event_estimation')
    params['pt_RR_min_path_length'] = cmds.getAttr(render_settings_node + '.pt_rr_min_path_length')

    params['gtr_filter_size'] = cmds.getAttr(render_settings_node + '.gtr_filter_size')
    params['gtr_min_samples'] = cmds.getAttr(render_settings_node + '.gtr_min_samples')
    params['gtr_max_samples'] = cmds.getAttr(render_settings_node + '.gtr_max_samples')
    params['gtr_max_contrast'] = cmds.getAttr(render_settings_node + '.gtr_max_contrast')
    params['gtr_max_variation'] = cmds.getAttr(render_settings_node + '.gtr_max_variation')

    if cmds.getAttr(render_settings_node + '.gtr_sampler') == 0:
        params['gtr_sampler'] = 'uniform'
    else:
        params['gtr_sampler'] = 'adaptive'

    return params