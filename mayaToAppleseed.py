# mayaToAppleseed.py 

# WORK IN PROGRESS!!

# uncomment the next few lines replace the path and run them in the maya script editor to launch the script 
#--------------------maya command (python)--------------------
#import sys
#sys.path.append('/projects/mayaToAppleseed') #where '/projects/mayaToAppleseed' is the file containing the scripts
#import mayaToAppleseed
#reload(mayaToAppleseed)
#mayaToAppleseed.m2s()


import maya.cmds as cmds
import os
import time
import re

script_name = "mayaToAppleseed.py"
version = "0.01"
more_info_url = "https://github.com/jonathantopf/mayaToAppleseed"

inch_to_meter = 0.02539999983236

#
# load params function
#

def getMayaParams(log):
    log.info('getting params from ui')
    #comile regular expression to check for non numeric chracters
    is_numeric = re.compile('^[0-9]+$')
    
    params = {'error':False}
    
    #main settings
    params['outputDir'] = cmds.textField('m2s_outputDir', query=True, text=True)
    params['fileName'] = cmds.textField('m2s_fileName', query=True, text=True)
    params['verbose'] = cmds.checkBox('m2s_verbose', query=True, value=True)
    params['scene_scale'] = 1
    
    #Advanced options
    #cameras
    params['sceneCameraExportAllCameras'] = cmds.checkBox('m2s_sceneCameraExportAllCameras', query=True, value=True)
    params['sceneCameraDefaultThinLens'] = cmds.checkBox('m2s_sceneCameraDefaultThinLens', query=True, value=True)
    
    #assemblies
    #materials
    params['matLambertBSDF'] = cmds.optionMenu('m2s_matLambertBSDF', query=True, value=True)
    params['matLambertEDF'] = cmds.optionMenu('m2s_matLambertEDF', query=True, value=True)
    params['matLambertSurfaceShader'] = cmds.optionMenu('m2s_matLambertSurfaceShader', query=True, value=True)
    params['matBlinnBSDF'] = cmds.optionMenu('m2s_matBlinnBSDF', query=True, value=True)
    params['matBlinnEDF'] = cmds.optionMenu('m2s_matBlinnEDF', query=True, value=True)
    params['matBlinnSurfaceShader'] = cmds.optionMenu('m2s_matBlinnSurfaceShader', query=True, value=True)
    params['matPhongBSDF'] = cmds.optionMenu('m2s_matPhongBSDF', query=True, value=True)
    params['matPhongEDF'] = cmds.optionMenu('m2s_matPhongEDF', query=True, value=True)
    params['matPhongSurfaceShader'] = cmds.optionMenu('m2s_matPhongSurfaceShader', query=True, value=True)
    params['matSurfaceShaderBSDF'] = cmds.optionMenu('m2s_matSurfaceShaderBSDF', query=True, value=True)
    params['matSurfaceShaderEDF'] = cmds.optionMenu('m2s_matSurfaceShaderEDF', query=True, value=True)
    params['matSurfaceShaderSurfaceShader'] = cmds.optionMenu('m2s_matSurfaceShaderSurfaceShader', query=True, value=True)
    params['matDefaultBSDF'] = cmds.optionMenu('m2s_matDefaultBSDF', query=True, value=True)
    params['matDefaultEDF'] = cmds.optionMenu('m2s_matDefaultEDF', query=True, value=True)
    params['matDefaultSurfaceShader'] = cmds.optionMenu('m2s_matDefaultSurfaceShader', query=True, value=True)

    params['matConvertTexturesToEXR'] = cmds.checkBox('m2s_matConvertTexturesToEXR', query=True, value=True)

    # output 
    params['outputCamera'] = cmds.optionMenu('m2s_outputCamera', query=True, value=True)
    params['outputColorSpace'] = cmds.optionMenu('m2s_outputColorSpace', query=True, value=True)
    params['outputResWidth'] = cmds.textField('m2s_outputResWidth', query=True, text=True)
    if not is_numeric.match(params['outputResWidth']):
        params['error'] = True
        log.err('Output Resolution Width may only contain whole numbers')
    params['outputResHeight'] = cmds.textField('m2s_outputResHeight', query=True, text=True)
    if not is_numeric.match(params['outputResHeight']):
        params['error'] = True
        log.err('Output Resolution Height may only contain whole numbers')
        
    # configurations
    # custom intercative config
    params['customInteractiveConfigCheck'] = cmds.checkBox('m2s_customInteractiveConfigCheck', query=True, value=True)
    params['customInteractiveConfigEngine'] = cmds.optionMenu('m2s_customInteractiveConfigEngine', query=True, value=True)
    params['customInteractiveConfigMinSamples'] = cmds.textField('m2s_customInteractiveConfigMinSamples', query=True, text=True)
    if not is_numeric.match(params['customInteractiveConfigMinSamples']):
        params['error'] = True
        log.err('Custom Interactive Config Min Samples may only contain whole numbers')
    params['customInteractiveConfigMaxSamples'] = cmds.textField('m2s_customInteractiveConfigMaxSamples', query=True, text=True)
    if not is_numeric.match(params['customInteractiveConfigMaxSamples']):
        params['error'] = True
        log.err('Custom Interactive Config Max Samples may only contain whole numbers')
    # custom Final config
    params['customFinalConfigCheck'] = cmds.checkBox('m2s_customFinalConfigCheck', query=True, value=True)
    params['customFinalConfigEngine'] = cmds.optionMenu('m2s_customFinalConfigEngine', query=True, value=True)
    params['customFinalConfigMinSamples'] = cmds.textField('m2s_customFinalConfigMinSamples', query=True, text=True)
    if not is_numeric.match(params['customFinalConfigMinSamples']):
        params['error'] = True
        log.err('Custom Final Config Min Samples may only contain whole numbers')
    params['customFinalConfigMaxSamples'] = cmds.textField('m2s_customFinalConfigMaxSamples', query=True, text=True)
    if not is_numeric.match(params['customFinalConfigMaxSamples']):
        params['error'] = True
        log.err('Custom Final Config Max Samples may only contain whole numbers')

    return(params)

#
# color object ---
#

class color():
    def __init__(self, log, name, color, multiplier):
        self.log = log
        self.name = name
        self.color = [color[0][0],color[0][1],color[0][2]]
        self.multiplier = multiplier
        self.color_space = 'srgb'
        self.wavelength_range = '400.0 700.0'
        self.alpha = 1.0
    def writeXML(self, doc):
        self.log.info('writing color {0}'.format(self.name))
        doc.startElement('color name="{0}"'.format(self.name))
        doc.appendElement('parameter name="color" value="{0:.6f} {1:.6f} {2:.6f}"'.format(self.color[0], self.color[1], self.color[2]))
        doc.appendElement('parameter name="color_space" value="{0}"'.format(self.color_space))
        doc.appendElement('parameter name="multiplier" value="{0}"'.format(self.multiplier))
        doc.appendElement('parameter name="alpha" value="{0}"'.format(self.alpha))
        doc.startElement('values')
        doc.appendLine('{0:.6f} {1:.6f} {2:.6f}'.format(self.color[0], self.color[1], self.color[2]))
        doc.endElement('values')
        doc.startElement('alpha')
        doc.appendLine('{0:.6f}'.format(self.alpha))
        doc.endElement('alpha')
        doc.endElement('color')

#
# texture class --
#

class texture():
    def __init__(self, log, name, file_name, color_space='srgb'):
        self.log = log
        self.name = name
        self.file_name = file_name
        self.color_space = color_space
    def writeXMLObject(self, doc):
        self.log.info('writing texture object {0}'.format(self.name))
        doc.startElement('texture name="{0}" model="disk_texture_2d"'.format(self.name))
        doc.appendElement('parameter name="color_space" value="{0}"'.format(self.color_space))
        doc.appendElement('parameter name="filename" value="{0}"'.format(self.file_name))
        doc.endElement('texture')
    def writeXMLInstance(self, doc):
        self.log.info('writing texture instance {0}_inst'.format(self.name))
        doc.startElement('texture_instance name="{0}_inst" texture="{0}"'.format(self.name, self.name))
        doc.appendElement('parameter name="addressing_mode" value="clamp"')
        doc.appendElement('parameter name="filtering_mode" value="bilinear"')
        doc.endElement('texture_instance')

#
# light object --
#

class light():
    def __init__(self, params, log, name):
        self.params = params
        self.log = log
        self.name = name
        self.color_name = self.name + '_exitance'
        self.color = cmds.getAttr(self.name+'.color')
        self.multiplier = cmds.getAttr(self.name+'.intensity')
        self.decay = cmds.getAttr(self.name+'.decayRate')
        m = cmds.getAttr(self.name+'.matrix')
        self.transform = [m[0],m[1],m[2],m[3]], [m[4],m[5],m[6],m[7]], [m[8],m[9],m[10],m[11]], [m[12],m[13],m[14],m[15]]
    def writeXML(self, doc):
        self.log.info('writing light: {0}'.format(self.name))
        doc.startElement('light name="{0}" model="point_light"'.format(self.name))
        doc.appendElement('parameter name="exitance" value="{0}"'.format(self.color_name))
        writeTransform(doc, 1, self.transform)
        doc.endElement('light')

#
# shader object --
#

class material(): #object transform name
    def __init__(self, params, log, name, bsdf=None, edf=None, surface_shader=None): 
        self.params = params
        self.log = log
        self.name = name
        self.shader_type = cmds.nodeType(self.name)
        self.bsdf = bsdf 
        self.edf = edf
        self.surface_shader = surface_shader
        self.bsdf_color = [(0.5, 0.5, 0.5)]
        self.bsdf_texture = None
        self.edf_color = [(0,0,0)]
        self.edf_texture = None
        self.specular_color = [(0,0,0)]
        self.specular_texture = None
        #for shaders with color & incandescence attributes interpret them as bsdf and edf
        if (self.shader_type == 'lambert') or (self.shader_type == 'blinn') or (self.shader_type == 'phong') or (self.shader_type == 'phongE'):
            self.bsdf_color = cmds.getAttr(self.name+'.color')
            self.edf_color = cmds.getAttr(self.name+'.incandescence')
            color_connection = cmds.connectionInfo((self.name + '.color'), sourceFromDestination=True).split('.')[0]
            incandecence_connection = cmds.connectionInfo((self.name+'.incandescence'), sourceFromDestination=True).split('.')[0]
            if color_connection:
                if cmds.nodeType(color_connection) == 'file':
                    self.bsdf_texture = cmds.getAttr(color_connection+ '.fileTextureName')
                    self.log.info('texture connected to {0}'.format(self.name + '.color'))
            if incandecence_connection:
                if cmds.nodeType(incandecence_connection) == 'file':
                    self.edf_texture = cmds.getAttr(incandecence_connection + '.fileTextureName')
                    self.log.info('texture connected to {0}'.format(self.name + '.incandescence'))

        #get specular conponent for shaders which have one
        elif (self.shader_type == 'blinn') or (self.shader_type == 'phong') or (self.shader_type == 'phongE'):
            self.specular_color = cmds.getAttr(self.name+'.specularColor')
            specular_connection = cmds.connectionInfo((self.name + '.specularColor'), sourceFromDestination=True).split('.')[0]
            if specular_connection:
                if cmds.nodeType(specular_connection) == 'file':
                    self.specular_texture = cmds.getAttr(specular_connection + '.fileTextureName') 
                    self.log.info('texture connected to {0}'.format(self.name + '.specularColor'))

        #for surface shaders interpret outColor as bsdf and edf
        elif self.shader_type == 'surfaceShader':
            self.bsdf_color = cmds.getAttr(self.name+'.outColor')
            self.edf_color = self.bsdf_color

            outColor_connection = cmds.connectionInfo((self.name+'.outColor'), sourceFromDestination=True).split('.')[0]
            if outColor_connection:
                if cmds.nodeType(outColor_connection) == 'file':
                    self.bsdf_texture = cmds.getAttr(outColor_connection + '.fileTextureName') #get connected texture file name
                    self.edf_texture = bsdf_texture
                    self.log.info('texture connected to {0}'.format(self.name + '.outColor'))
            else:
                self.bsdf_texture = None
                self.edf_texture = None

        #else use default shader
        else:
            self.log.err('no valid texture connected to {0} using default'.format(self.name))
            self.name = 'default_texture'

    def writeXML(self,doc):
        self.log.info('writing material {0}'.format(self.name))
        doc.startElement('material name="{0}" model="generic_material"'.format(self.name))
        if self.bsdf:
            doc.appendElement('parameter name="bsdf" value="{0}"'.format(self.bsdf))
        if self.edf:
            doc.appendElement('parameter name="edf" value="{0}"'.format(self.edf))
        if self.surface_shader:
            doc.appendElement('parameter name="surface_shader" value="{0}"'.format(self.surface_shader))
        doc.endElement('material')

#
# bsdf class --
#

class bsdf():
    def __init__(self, log, name, model, bsdf_params):
        self.log = log
        self.name = name
        self.model = model
        self.bsdf_params = bsdf_params
    def writeXML(self, doc):
        self.log.info('writing bsdf {0}'.format(self.name))
        doc.startElement('bsdf name="{0}" model="{1}"'.format(self.name, self.model))
        for param in self.bsdf_params:
            doc.appendElement('parameter name="{0}" value="{1}"'.format(param, self.bsdf_params[param]))
        doc.endElement('bsdf')

#
# edf class --
#

class edf():
    def __init__(self, log, name, model, edf_params):
        self.log = log
        self.name = name
        self.model = model
        self.edf_params = edf_params
    def writeXML(self, doc):
        self.log.info('writing bsdf {0}'.format(self.name))
        doc.startElement('edf name="{0}" model="{1}"'.format(self.name, self.model))
        for param in self.edf_params:
            doc.appendElement('parameter name="{0}" value="{1}"'.format(param, self.edf_params[param]))
        doc.endElement('edf')

#
# surface shader class --
#

class surfaceShader():
    def __init__(self, log, name, model, surface_shader_params=None):
        self.log = log
        self.name = name
        self.model = model
        self.surface_shader_params = surface_shader_params

    def writeXML(self, doc):
        doc.startElement('surface_shader name="{0}" model="{1}"'.format(self.name, self.model))
        if self.model == 'constant_surface_shader':
            for param in self.surface_shader_params:
                doc.appendElement('parameter name="{0}" value="{1}"'.format(param, self.surface_shader_params[param]))
        doc.endElement('surface_shader')


#
# camera class --
#

class camera(): #(camera_name)
    def __init__(self, params, log, cam):
        self.params = params
        self.log = log
        if self.params['sceneCameraDefaultThinLens'] or cmds.getAttr(cam+'.depthOfField'):
            self.model = 'thinlens_camera'
            self.f_stop = cmds.getAttr(cam+'.fStop')
            self.focal_distance = cmds.getAttr(cam+'.focusDistance')
            self.diaphram_blades = 0
            self.diaphram_tilt_angle = 0.0
        else:
            self.model = 'pinhole_camera'
        self.name = cam
        self.aspect = float(params['outputResWidth'])/float(params['outputResHeight'])
        self.horizontal_fov = float(cmds.getAttr(self.name + '.horizontalFilmAperture')) * inch_to_meter
        self.vertical_fov = self.horizontal_fov / self.aspect
        self.focal_length = float(cmds.getAttr(self.name+'.focalLength')) / 1000
        # transpose camera matrix -> XXX0, YYY0, ZZZ0, XYZ1
        m = cmds.getAttr(cam+'.matrix')
        self.transform = [m[0],m[1],m[2],m[3]], [m[4],m[5],m[6],m[7]], [m[8],m[9],m[10],m[11]], [m[12],m[13],m[14],m[15]]
   
    def writeXML(self, doc):
        self.log.info('writing camera: {0}'.format(self.name))
        doc.startElement('camera name="{0}" model="{1}"'.format(self.name, self.model))
        doc.appendElement('parameter name="film_dimensions" value="{0} {1}"'.format(self.horizontal_fov, self.vertical_fov))
        doc.appendElement('parameter name="focal_length" value="{0}"'.format(self.focal_length))
        if self.model == 'thinlens_camera':
            self.log.info('exporting ' + self.name + ' as thinlens camera')
            doc.appendElement('parameter name="focal_distance" value="{0}"'.format(self.focal_distance))
            doc.appendElement('parameter name="f_stop" value="{0}"'.format(self.f_stop))
            doc.appendElement('parameter name="diaphragm_blades" value="{0}"'.format(self.diaphram_blades))
            doc.appendElement('parameter name="diaphragm_tilt_angle" value="{0}"'.format(self.diaphram_tilt_angle))
        #output transform matrix
        writeTransform(doc, self.params['scene_scale'], self.transform)
        doc.endElement('camera')

#
# geometry object --
#

class geometry(): # (object_transfrm_name, obj_file)
    def __init__(self, name, log, output_file, assembly='main_assembly'):
        self.name = name
        #get name in heirarchy
        self.heirarchy_name = name
        current_object = name
        while cmds.listRelatives(current_object, parent=True):
            current_object = cmds.listRelatives(current_object, parent=True)[0]
            self.heirarchy_name = current_object + ' ' + self.heirarchy_name
        self.log = log
        self.output_file = output_file
        self.assembly = assembly
        # get material name
        shape = cmds.listRelatives(self.name, s=True)[0]
        shadingEngine = cmds.listConnections(shape, t='shadingEngine')[0]
        self.material = cmds.connectionInfo((shadingEngine + ".surfaceShader"),sourceFromDestination=True).split('.')[0] #find the attribute the surface shader is plugged into athen split off the attribute name to leave the shader name
        # transpose camera matrix -> XXX0, YYY0, ZZZ0, XYZ1
        m = cmds.getAttr(name+'.matrix')
        self.transform = [m[0],m[1],m[2],m[3]], [m[4],m[5],m[6],m[7]], [m[8],m[9],m[10],m[11]], [m[12],m[13],m[14],m[15]]
        

    def writeXMLInstance(self, doc):
        self.log.info('writing objecct instance: '+self.name)
        doc.startElement('object_instance name="{0}_inst" object="{1}.{2}"'.format(self.name, self.assembly, self.heirarchy_name,))
        writeTransform(doc)
        doc.appendElement('assign_material slot="0" side="front" material="{0}"'.format(self.material))
        doc.appendElement('assign_material slot="0" side="back" material="{0}"'.format(self.material))
        doc.endElement('object_instance')
#
# assembly object --
#

class assembly():
    def __init__(self, params, log, name='main_assembly'):
        self.params = params
        self.log = log
        self.name = name
        self.light_objects = []
        self.geo_objects = dict()
        self.material_objects = dict()
        self.color_objects = dict()
        self.texture_objects = dict()
        self.surface_shader_objects = dict()
        self.bsdf_objects = dict()
        self.edf_objects = dict()

        #if name is default populate list with all lights otherwise just lights from set with the same name as the object
        if (self.name == 'main_assembly'):
            for light_shape in cmds.ls(lights=True):
                self.light_objects.append(light(self.params, self.log, cmds.listRelatives(light_shape, ad=True, ap=True)[0]))
        else:
            for light_shape in cmds.listRelatives(self.name, typ='light'):
                self.light_objects.append(light(self.params, self.log, cmds.listRelatives(light_shape, ad=True, ap=True)[0]), self.log)
        #add light colors to list
        for light_object in self.light_objects:
            self.addColor(light_object.color_name, light_object.color, light_object.multiplier)
        
        
        #if name is default populate list with all geometry otherwise just geometry from set with the same name as the object
        if (self.name == 'main_assembly'):
            #create a list of all geometry objects and itterate over them
            for geo in cmds.ls(g=True):
                geo_transform = cmds.listRelatives(geo, ad=True, ap=True)[0]
                if not geo_transform in self.geo_objects:
                    self.geo_objects[geo_transform] = geometry(geo_transform, self.log, ('geo/'+self.name+'.obj'), self.name)
        else:
            for geo in cmds.listConnections(self.name, sh=True):
                geo_transform = cmds.listRelatives(geo, ad=True, ap=True)[0]
                if not geo_transform in self.geo_objects:
                    self.geo_objects[geo_transform] = geometry(geo_transform, self.log, ('geo/'+self.name+'.obj'), self.name)
                
        #populate list with individual materials
        for geo in self.geo_objects:
            self.addMaterial(self.geo_objects[geo].material)

    def addColor(self, name, value, multiplier=1):
        if not name in self.color_objects:
            self.color_objects[name] = color(self.log, name, value, multiplier)

    def addTexture(self, name, file_name):
        if not name in self.texture_objects:
            self.texture_objects[name] = texture(self.log, name, file_name)
    
    def addEDF(self, material, type):
        edf_params = dict()
        if type == 'Diffuse':
            if material.edf_texture:
                self.addTexture(material.name + '_exitance', material.edf_texture)
                edf_params['exitance'] = (material.name + '_exitance_inst')
            else:
                self.addColor((material.name + '_exitance'), material.edf_color)
                edf_params['exitance'] = material.name + '_exitance'
            self.edf_objects[material.name + '_edf'] = edf(self.log, material.name + '_edf', 'diffuse_edf', edf_params)

    def addBSDF(self, material, type):
        self.log.info('translating {0} to {1} BSDF'.format(material.name, type))
        bsdf_params = dict()
        if type == 'Lambertian':
            #add reflectence component
            if material.bsdf_texture:
                self.addTexture(material.name + '_reflectance', material.bsdf_texture)
                bsdf_params['reflectance'] = (material.name + '_reflectance_inst')
            else:
                self.addColor((material.name + '_reflectance'), material.bsdf_color)
                bsdf_params['reflectance'] = material.name + '_reflectance'
            self.bsdf_objects[material.name + '_bsdf'] = bsdf(self.log, material.name + '_bsdf', 'lambertian_brdf', bsdf_params)

        elif type =='Ashikhmin-Shirley':
            bsdf_params['shininess_u'] = 0.5
            bsdf_params['shininess_v'] = 0.5
            # add diffuse reflectence component
            if material.bsdf_texture:
                self.addTexture(material.name + '_diffuse_reflectance', material.bsdf_texture)
                bsdf_params['diffuse_reflectance'] = (material.name + '_diffuse_reflectance_inst')
            else:
                self.addColor(material.name + '_diffuse_reflectance', material.bsdf_color)
                bsdf_params['diffuse_reflectance'] = material.name + '_diffuse_reflectance'
            #add glossy reflectence component
            if material.specular_texture:
                self.addTexture(material.name + '_glossy_reflectance', material.specular_texture)
                bsdf_params['glossy_reflectance'] = material.name + '_glossy_reflectance'
            else:
                self.addColor(material.name + '_glossy_reflectance', material.bsdf_color)
                bsdf_params['glossy_reflectance'] = material.name + '_glossy_reflectance'
            self.bsdf_objects[material.name + '_bsdf'] = bsdf(self.log, material.name + '_bsdf', 'ashikhmin_brdf', bsdf_params)

        elif type == 'Kelemen':
            bsdf_params['roughness'] = 0.5
            #add matte_reflectance component
            if material.bsdf_texture:
                self.addTexture(material.name + '_matte_reflectance', material.bsdf_texture)
                bsdf_params['matte_reflectance'] = (material.name + '_matte_reflectance_inst')
            else:
                self.addColor(material.name + '_matte_reflectance', material.bsdf_color)
                bsdf_params['matte_reflectance'] = material.name + '_matte_reflectance'
            #add specular_reflectance component
            if material.specular_texture:
                self.addTexture(material.name + '_specular_reflectance', material.specular_texture)
                bsdf_params['specular_reflectance'] = material.name + '_specular_reflectance'
            else:
                self.addColor(material.name + '_specular_reflectance', material.bsdf_color)
                bsdf_params['specular_reflectance'] = material.name + '_specular_reflectance'
            self.bsdf_objects[material.name + '_bsdf'] = bsdf(self.log, material.name + '_bsdf', 'kelemen_brdf', bsdf_params)

        elif type == 'Specular_BRDF':
            #add reflectence component
            if material.bsdf_texture:
                self.addTexture(material.name + '_reflectance', material.bsdf_texture)
                bsdf_params['reflectance'] = (material.name + '_reflectance_inst')
            else:
                self.addColor((material.name + '_reflectance'), material.bsdf_color)
                bsdf_params['reflectance'] = material.name + '_reflectance'
            self.bsdf_objects[material.name + '_bsdf'] = bsdf(self.log, material.name + '_bsdf', 'specular_brdf', bsdf_params)
        

    def addSurfaceShader(self, material, name, type): 
        if not name in self.surface_shader_objects:
            surface_shader_params = dict()
            model=None
            #check surface shader type and add appropriate parameters to dict
            if type == 'Physical':
                model = 'physical_surface_shader'
            elif type == 'Constant':
                model = 'constant_surface_shader'
                #if surface_shader is set to constant, take color or texture from material bsdf
                if material.bsdf_texture:
                    self.addTexture(material.name + '_surface_shader_color', material.bsdf_texture)
                    surface_shader_params['color'] = (material.name + '_surface_shader_color_inst ')
                else:
                    self.addColor((material.name + '_surface_shader_color'), material.bsdf_color)
                    surface_shader_params['color'] = material.name + '_surface_shader_color'
            elif type == 'Ambient Occlusion':
                self.log.err('atempting to set {0} surface shader to ambient occlusion'.format(name))
                self.log.err('ambient occlusion not implimented yet')
            self.log.info('adding {0} surface shader to {0}'.format(type, name))
            self.surface_shader_objects[name] = surfaceShader(self.log, name, model, surface_shader_params)


    def addMaterial(self, name):
        if not name in self.material_objects:
            self.material_objects[name] = material(self.params, self.log, name)

            self.material_objects[name].bsdf = None
            self.material_objects[name].edf = None
            self.material_objects[name].surface_shader = None

            #create surface shader
            if self.material_objects[name].shader_type == 'lambert':
                if not self.params['matLambertSurfaceShader'] == 'None':   
                    if self.params['matLambertSurfaceShader'] == 'Physical':
                        self.material_objects[name].surface_shader = ('Physical_surface_shader')
                        self.addSurfaceShader(self.material_objects[name], 'Physical_surface_shader', self.params['matLambertSurfaceShader'])
                    else:
                        self.material_objects[name].surface_shader = (name + '_surface_shader')
                        self.addSurfaceShader(self.material_objects[name], name + '_surface_shader', self.params['matLambertSurfaceShader'])

            elif self.material_objects[name].shader_type == 'blinn':
                if not self.params['matBlinnSurfaceShader'] == 'None':   
                    if self.params['matBlinnSurfaceShader'] == 'Physical':
                        self.material_objects[name].surface_shader = ('Physical_surface_shader')
                        self.addSurfaceShader(self.material_objects[name], 'Physical_surface_shader', self.params['matBlinnSurfaceShader'])
                    else:
                        self.material_objects[name].surface_shader = (name + '_surface_shader')
                        self.addSurfaceShader(self.material_objects[name], name + '_surface_shader', self.params['matBlinnSurfaceShader'])

            elif self.material_objects[name].shader_type == 'phong' or self.material_objects[name].shader_type == 'phongE':
                if not self.params['matPhongSurfaceShader'] == 'None':   
                    if self.params['matPhongSurfaceShader'] == 'Physical':
                        self.material_objects[name].surface_shader = ('Physical_surface_shader')
                        self.addSurfaceShader(self.material_objects[name], 'Physical_surface_shader', self.params['matPhongSurfaceShader'])
                    else:
                        self.material_objects[name].surface_shader = (name + '_surface_shader')
                        self.addSurfaceShader(self.material_objects[name], name + '_surface_shader', self.params['matPhongSurfaceShader'])

            elif self.material_objects[name].shader_type == 'surfaceShader':
                if not self.params['matSurfaceShaderSurfaceShader'] == 'None':   
                    if self.params['matSurfaceShaderSurfaceShader'] == 'Physical':
                        self.material_objects[name].surface_shader = ('Physical_surface_shader')
                        self.addSurfaceShader(self.material_objects[name], 'Physical_surface_shader', self.params['matSurfaceShaderSurfaceShader'])
                    else:
                        self.material_objects[name].surface_shader = (name + '_surface_shader')
                        self.addSurfaceShader(self.material_objects[name], name + '_surface_shader', self.params['matSurfaceShaderSurfaceShader'])

            else:
                if not self.params['matDefaultSurfaceShader'] == 'None':   
                    if self.params['matDefaultSurfaceShader'] == 'Physical':
                        self.material_objects[name].surface_shader = ('Physical_surface_shader')
                        self.addSurfaceShader(self.material_objects[name], 'Physical_surface_shader', self.params['matDefaultSurfaceShader'])
                    else:
                        self.material_objects[name].surface_shader = (name + '_surface_shader')
                        self.addSurfaceShader(self.material_objects[name], name + '_surface_shader', self.params['matDefaultSurfaceShader'])

            #create bsdf
            if self.material_objects[name].shader_type == 'lambert':
                if not self.params['matLambertBSDF'] == 'None':
                    self.material_objects[name].bsdf = (name + '_bsdf')
                    self.addBSDF(self.material_objects[name], self.params['matLambertBSDF'])  
                      
            elif self.material_objects[name].shader_type == 'blinn':
                if not self.params['matBlinnBSDF'] == 'None':
                    self.material_objects[name].bsdf = (name + '_bsdf')
                    self.addBSDF(self.material_objects[name], self.params['matBlinnBSDF'])   
                      
            elif self.material_objects[name].shader_type == 'phong' or self.material_objects[name].shader_type == 'phongE':
                if not self.params['matPhongBSDF'] == 'None':
                    self.material_objects[name].bsdf = (name + '_bsdf')
                    self.addBSDF(self.material_objects[name], self.params['matPhongBSDF'])  
                      
            elif self.material_objects[name].shader_type == 'surfaceShader':
                if not self.params['matSurfaceShaderBSDF'] == 'None':
                    self.material_objects[name].bsdf = (name + '_bsdf')
                    self.addBSDF(self.material_objects[name], self.params['matSurfaceShaderBSDF'])  
                      
            else:
                if not self.params['matDefaultBSDF'] == 'None':
                    self.material_objects[name].bsdf = (name + '_bsdf')
                    self.addBSDF(self.material_objects[name], self.params['matDefaultBSDF'])  

            #create edf 
            if self.material_objects[name].shader_type == 'lambert':
                if not self.params['matLambertEDF'] == 'None':
                    self.material_objects[name].edf = (name + '_edf')
                    self.addEDF(self.material_objects[name], self.params['matLambertEDF'])

            elif self.material_objects[name].shader_type == 'blinn':
                if not self.params['matBlinnEDF'] == 'None':
                    self.material_objects[name].edf = (name + '_edf')
                    self.addEDF(self.material_objects[name], self.params['matBlinnEDF'])

            elif self.material_objects[name].shader_type == 'phong' or self.material_objects[name].shader_type == 'phongE':
                if not self.params['matPhongEDF'] == 'None':
                    self.material_objects[name].edf = (name + '_edf')
                    self.addEDF(self.material_objects[name], self.params['matPhongEDF'])

            elif self.material_objects[name].shader_type == 'surfaceShader':
                if not self.params['matSurfaceShaderEDF'] == 'None':
                    self.material_objects[name].edf = (name + '_edf')
                    self.addEDF(self.material_objects[name], self.params['matSurfaceShaderEDF'])
            else:
                if not self.params['matDefaultEDF'] == 'None':
                    self.material_objects[name].edf = (name + '_edf')
                    self.addEDF(self.material_objects[name], self.params['matDefaultEDF'])
        
    def writeXML(self, doc):
        self.log.info('writing assembly: {0}'.format(self.name))
        doc.startElement('assembly name="{0}"'.format(self.name))

        #write colors
        for col in self.color_objects:
             self.color_objects[col].writeXML(doc)

        #write texture objects
        for tex in self.texture_objects:
            self.texture_objects[tex].writeXMLObject(doc)
        #write texture instances
        for tex in self.texture_objects:
            self.texture_objects[tex].writeXMLInstance(doc)

        #write bsdfs
        for bsdf in self.bsdf_objects:
            self.bsdf_objects[bsdf].writeXML(doc)

        #write eddfs
        for edf in self.edf_objects:
            self.edf_objects[edf].writeXML(doc)

        #write surface shaders
        for surface_shader in self.surface_shader_objects:
            self.surface_shader_objects[surface_shader].writeXML(doc)

        #write materials
        for material in self.material_objects:
            self.material_objects[material].writeXML(doc)
        
        #write .obj object
        doc.startElement('object name="{0}" model="mesh_object"'.format(self.name))
        doc.appendElement('parameter name="filename" value="geo/{0}.obj"'.format(self.name))
        doc.endElement('object')
        
        #write lights
        for light_name in self.light_objects:
            light_name.writeXML(doc)
        
        #write geo object instances
        for geo in self.geo_objects:
            self.geo_objects[geo].writeXMLInstance(doc)
        
        doc.endElement('assembly')
        doc.startElement('assembly_instance name="{0}_inst" assembly="{1}"'.format(self.name, self.name))
        writeTransform(doc, self.params['scene_scale'])
        doc.endElement('assembly_instance')

        #create geo directory if it doesnt already exist
        self.log.info('exporting obj: ' + self.name + '.obj')
        if not os.path.exists(self.params['outputDir']+'/geo'):
            os.makedirs(self.params['outputDir']+'/geo')

        #create list of all the top level objects
        all_objects = []

        for geo in self.geo_objects:
            all_objects.append(self.geo_objects[geo].name)

        top_level_objects = []

        for object in all_objects:
            current_object = object
            while cmds.listRelatives(current_object, parent=True):
                current_object = cmds.listRelatives(current_object, parent=True)[0]
            if not current_object in top_level_objects:
                top_level_objects.append(current_object)
        cmds.select(cl=True)
        for geo_name in top_level_objects:
            cmds.select(geo_name, add=True)
        cmds.file(('{0}/{1}'.format(self.params['outputDir']+'/geo', (self.name + '.obj'))), force=True, options='groups=1;ptgroups=1;materials=0;smoothing=0;normals=1', type='OBJexport', pr=True, es=True)

        cmds.select(cl=True)

#
# scene class --
#

class scene():
    def __init__(self,params, log):
        self.params = params
        self.log = log
        self.assembly_list = []
    def writeXML(self, doc):
        self.log.info('writing scene element')
        doc.startElement('scene')

############################ multiple camera export not supported #############################
#        #write cameras
#        if self.params['sceneCameraExportAllCameras']:
#            #export all cameras
#            cam_list = []
#            for c in cmds.listCameras(p=True):
#                camera_instance = camera(self.params, self.log, c)
#                camera_instance.writeXML(doc)
#        else:
#            #export only camera selected in output
#            camera_instance = camera(self.params, self.log, self.params['outputCamera'])
#            camera_instance.writeXML(doc)
###############################################################################################
        
        #temp camera export - use until multiple camera is supported
        camera_instance = camera(self.params, self.log, self.params['outputCamera'])
        camera_instance.writeXML(doc)   
             
        #export assemblies
        #get maya geometry
        shape_list = cmds.ls(g=True, v=True) 
        geo_transform_list = []
        for g in shape_list:
            # add first connected transform to the list
            geo_transform_list.append(cmds.listRelatives(g, ad=True, ap=True)[0]) 

        #populate a list of assemblies
        for g in geo_transform_list:
            set = cmds.listSets(object=g)
            if set:
                if not set[0] in self.assembly_list:
                    self.assembly_list.append(cmds.listSets(object=g)[0])
        
        #create assemblys if any assembly names are present otherwise create default assembly
        if self.assembly_list:
            #for each assemply in assembly_list create an object and output its XML
            for a in self.assembly_list:
                new_assembly = assembly(self.params, self.log, a)
                new_assembly.writeXML(doc)
        else:
            self.log.info('no populated maya sets present, using default "main_assembly"')
            new_assembly = assembly(self.params, self.log, 'main_assembly')
            new_assembly.writeXML(doc)
        doc.endElement('scene')

#
# output class --
#

class output():
    def __init__(self, params):
        self.params = params
    def writeXML(self, doc):
        doc.startElement('output')
        doc.startElement('frame name="beauty"')
        doc.appendElement('parameter name="camera" value="{0}"'.format(self.params['outputCamera']))
        doc.appendElement('parameter name="color_space" value="{0}"'.format(self.params['outputColorSpace']))
        doc.appendElement('parameter name="resolution" value="{0} {1}"'.format(self.params['outputResWidth'], self.params['outputResHeight']))
        doc.endElement('frame')
        doc.endElement('output')

#
# configurations class --
#

class configurations():
    def __init__(self, params, log):
        self.log = log
        self.params = params
    def writeXML(self,doc):
        doc.startElement("configurations")
        self.log.info('writing configurations')
        #if 'customise interactive configuration' is set read customised values
        if self.params['customInteractiveConfigCheck']:
            self.log.info('writing custom interactive config')
            doc.startElement('configuration name="interactive" base="base_interactive"')
            engine = ''
            if self.params['customInteractiveConfigEngine'] == 'Path Tracing':
                engine = "pt"
            else:
                engine = "drt"
            doc.appendElement('parameter name="lighting_engine" value="{0}"'.format(engine))
            doc.appendElement('parameter name="min_samples" value="{0}"'.format(self.params['customInteractiveConfigMinSamples']))
            doc.appendElement('parameter name="max_samples" value="{0}"'.format(self.params['customInteractiveConfigMaxSamples']))
            doc.endElement('configuration')
        else:# otherwise add default configurations
            self.log.info('writing default interactive config')
            doc.appendElement('configuration name="interactive" base="base_interactive"')
  
        #if 'customise final configuration' is set read customised values
        if cmds.checkBox('m2s_customFinalConfigCheck', query=True, value=True) == True:
            self.log.info('writing custom final config')
            doc.startElement('configuration name="final" base="base_final"')
            engine = ''
            if cmds.optionMenu('m2s_customFinalConfigEngine', query=True, value=True) == "Path Tracing":
                engine = 'pt'
            else:
                engine = 'drt'
            doc.appendElement('parameter name="lighting_engine" value="{0}"'.format(engine))
            doc.appendElement('parameter name="min_samples" value="{0}"'.format(self.params['customFinalConfigMinSamples']))
            doc.appendElement('parameter name="max_samples" value="{0}"'.format(self.params['customFinalConfigMaxSamples']))
            doc.endElement("configuration")
        else:# otherwise add default configurations
            self.log.info('writing default final config')
            doc.appendElement('configuration name="final" base="base_final"')
        # begin adding custom configurations
        doc.endElement('configurations')
	
#
# writeXml class --
#

class writeXml(): #(file_path)
    spaces_per_indentation_level = 4    
    def __init__(self, f_path, log):
        self.log = log
        self.file_path = f_path
        self.indentation_level = 0
        self.file_object = None
        try:
            self.file_object = open(self.file_path, 'w') #open file for editing

        except IOError:
            self.log.err('IO error: file not accesable')
            raise RuntimeError('IO error: file not accesable')
            return
        
    def startElement(self,str):
        self.file_object.write(((self.indentation_level * self.spaces_per_indentation_level) * ' ') + "<" + str + '>\n')
        self.indentation_level += 1
        
    def endElement(self, str):
        self.indentation_level -= 1
        self.file_object.write(((self.indentation_level * self.spaces_per_indentation_level) * ' ') + '</' + str + '>\n')
        
    def appendElement(self, str):
        self.file_object.write(((self.indentation_level * self.spaces_per_indentation_level) * ' ') + '<' + str + '/>\n')
        
    def appendLine(self, str):
        self.file_object.write(((self.indentation_level * self.spaces_per_indentation_level) * ' ') + str + '\n')
        
    def close(self):
        self.file_object.close() #close file

#
# writeOut Class, used to write to the error pane and command prompt
#

class writeOut():
    def __init__(self):
        self.output = ''
        cmds.scrollField('m2s_log', edit=True, cl=True)
    def err(self, message):
        setExportError()
        self.output = self.output + '<span style="color:#dd0000">' + message + '</span><br>'
        cmds.scrollField('m2s_log', edit=True, text=self.output)
        print('ERROR: ' + message)
    def info(self, message):
        self.output = self.output + '<span style="color:#00dd00">' + message + '</span><br>'
        cmds.scrollField('m2s_log', edit=True, text=self.output) 
        print('INFO: ' + message)     

#
# writeTransform function --
#

def writeTransform(doc, scale = 1, transform = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]):
    doc.startElement('transform')
    doc.appendElement('scaling value="{0}"'.format(scale))
    doc.startElement('matrix')

    doc.appendLine('{0:.15f} {1:.15f} {2:.15f} {3:.15f}'.format(transform[0][0], transform[1][0], transform[2][0], transform[3][0]))
    doc.appendLine('{0:.15f} {1:.15f} {2:.15f} {3:.15f}'.format(transform[0][1], transform[1][1], transform[2][1], transform[3][1]))
    doc.appendLine('{0:.15f} {1:.15f} {2:.15f} {3:.15f}'.format(transform[0][2], transform[1][2], transform[2][2], transform[3][2]))
    doc.appendLine('{0:.15f} {1:.15f} {2:.15f} {3:.15f}'.format(transform[0][3], transform[1][3], transform[2][3], transform[3][3]))	

    doc.endElement('matrix')
    doc.endElement('transform')

#
# build and export
#

def export():
    log = writeOut()
    params = getMayaParams(log)
    if not params['error']:
        log.info('beginning export')
        log.info('opening output file: ' + params['fileName'])
        doc = writeXml('{0}/{1}'.format(params['outputDir'], params['fileName']), log)
        doc.appendLine('<?xml version="1.0" encoding="UTF-8"?>') # XML format string
        doc.appendLine('<!-- File generated by {0} version {1} visit {2} for more info and the latest super exciting release!-->'.format(script_name, version, more_info_url))
        log.info('writing project element')
        doc.startElement('project')
        scene_element = scene(params, log)
        scene_element.writeXML(doc)
        output_element = output(params)
        output_element.writeXML(doc)
        config_element = configurations(params, log)
        config_element.writeXML(doc)
    
        doc.endElement('project')
        doc.close()
        log.info('export finished')
        setExportSuccess()
    else:
        log.err('error validating ui attributes ')
        raise RuntimeError('check script editor for details')

#
# ui functions --
#

def setExportSuccess():
    for i in range(3):
        cmds.button('m2s_export', edit=True, bgc=[0.5,1,0.5])
        cmds.button('m2s_export', edit=True, ebg=False)
        time.sleep(0.1)
        cmds.refresh(f=True)
        cmds.button('m2s_export', edit=True, bgc=[0.5,0.5,0.5])
        cmds.button('m2s_export', edit=True, ebg=False)
        time.sleep(0.1)
        cmds.refresh(f=True)
def setExportError():
    for i in range(3):
        cmds.button('m2s_export', edit=True, bgc=[1,0.2,0.2])
        cmds.button('m2s_export', edit=True, ebg=False)
        time.sleep(0.1)
        cmds.refresh(f=True)
        cmds.button('m2s_export', edit=True, bgc=[0.5,0.5,0.5])
        cmds.button('m2s_export', edit=True, ebg=False)
        time.sleep(0.1)
        cmds.refresh(f=True)

def getDir(field_name):
    current_state = cmds.textField(field_name, query=True, text=True)
    new_state = cmds.fileDialog2(fileMode=3, okCaption='select', caption='Select a directory', dir=current_state)
    if new_state:
        cmds.textField(field_name, edit=True, text=new_state[0])

def hideLog():
    if cmds.scrollField('m2s_log', query=True, vis=True):
        cmds.button('m2s_hideLog', edit=True, label='Show log')
        cmds.scrollField('m2s_log', edit=True, vis=False)
    else:
        cmds.button('m2s_hideLog', edit=True, label='Hide log')
        cmds.scrollField('m2s_log', edit=True, vis=True)           

#
# initiallise and show ui --
#

def m2s():
    if cmds.window('m2sDial', query=True, exists=True):
        cmds.deleteUI('m2sDial')
    mayaToAppleseedUi = cmds.loadUI(f="{0}/mayaToAppleseed.ui".format(os.path.dirname(__file__)))    
    #if the file has been saved set default file name to <scene_name>.appleseed
    if cmds.file(query=True, sceneName=True, shortName=True):
        cmds.textField('m2s_fileName', edit=True, text=(os.path.splitext(cmds.file(query=True, sceneName=True, shortName=True))[0] + '.appleseed'))
    else:
        cmds.textField('m2s_fileName', edit=True, text='file.appleseed')
    #populate output > camera dropdown menu with maya cameras
    for camera in cmds.listCameras(p=True):
        cmds.menuItem(parent='m2s_outputCamera', label=camera)
    #set default resolution to scene resolution
    cmds.textField('m2s_outputResWidth', edit=True, text=cmds.getAttr('defaultResolution.width'))
    cmds.textField('m2s_outputResHeight', edit=True, text=cmds.getAttr('defaultResolution.height'))

    hideLog()
    #show window
    cmds.showWindow(mayaToAppleseedUi)






