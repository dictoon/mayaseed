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
import re

script_name = "mayaToAppleseed.py"
version = "0.01"
more_info_url = "https://github.com/jonathantopf/mayaToAppleseed"

inch_to_meter = 0.02539999983236

#
# load params function
#

def getMayaParams():
    #comile regular expression to check for non numeric chracters
    is_numeric = re.compile('^[0-9]+$')
    
    params = {'error':False}
    
    #main settings
    params['outputDir'] = cmds.textField('m2s_outputDir', query=True, text=True)
    params['fileName'] = cmds.textField('m2s_fileName', query=True, text=True)
    params['verbose'] = cmds.checkBox('m2s_verbose', query=True, value=True)
    params['scene_scale'] = 1
    #scene
    #cameras
    params['sceneCameraExportAllCameras'] = cmds.checkBox('m2s_sceneCameraExportAllCameras', query=True, value=True)
    params['sceneCameraDefaultThinLens'] = cmds.checkBox('m2s_sceneCameraDefaultThinLens', query=True, value=True)
    
    # output 
    params['outputCamera'] = cmds.optionMenu('m2s_outputCamera', query=True, value=True)
    params['outputColorSpace'] = cmds.optionMenu('m2s_outputColorSpace', query=True, value=True)
    params['outputResWidth'] = cmds.textField('m2s_outputResWidth', query=True, text=True)
    params['outputResHeight'] = cmds.textField('m2s_outputResHeight', query=True, text=True)
    
    # configurations
    # custom intercative config
    params['customInteractiveConfigCheck'] = cmds.checkBox('m2s_customInteractiveConfigCheck', query=True, value=True)
    params['customInteractiveConfigEngine'] = cmds.optionMenu('m2s_customInteractiveConfigEngine', query=True, value=True)
    params['customInteractiveConfigMinSamples'] = cmds.textField('m2s_customInteractiveConfigMinSamples', query=True, text=True)
    if not is_numeric.match(params['customInteractiveConfigMinSamples']):
        params['error'] = True
        print('ERROR: Custom Interactive Config Min Samples may only contain whole numbers')
    params['customInteractiveConfigMaxSamples'] = cmds.textField('m2s_customInteractiveConfigMaxSamples', query=True, text=True)
    if not is_numeric.match(params['customInteractiveConfigMaxSamples']):
        params['error'] = True
        print('ERROR: Custom Interactive Config Max Samples is non int')
    # custom Final config
    params['customFinalConfigCheck'] = cmds.checkBox('m2s_customFinalConfigCheck', query=True, value=True)
    params['customFinalConfigEngine'] = cmds.optionMenu('m2s_customFinalConfigEngine', query=True, value=True)
    params['customFinalConfigMinSamples'] = cmds.textField('m2s_customFinalConfigMinSamples', query=True, text=True)
    if not is_numeric.match(params['customFinalConfigMinSamples']):
        params['error'] = True
        print('ERROR: Custom Final Config Min Samples may only contain whole numbers')
    params['customFinalConfigMaxSamples'] = cmds.textField('m2s_customInteractiveConfigMaxSamples', query=True, text=True)
    if not is_numeric.match(params['customFinalConfigMaxSamples']):
        params['error'] = True
        print('ERROR: Custom Final Config Max Samples is non int')

    return(params)
    
#
# get directory function
#

def getDir(field_name):
    current_state = cmds.textField(field_name, query=True, text=True)
    new_state = cmds.fileDialog2(fileMode=3, okCaption='select', caption='Select a directory', dir=current_state)
    if new_state:
        cmds.textField(field_name, edit=True, text=new_state[0])

#
# color object ---
#

class color():
    def __init__(self, name, color, multiplier):
        self.name = name
        self.color = [color[0][0],color[0][1],color[0][2]]
        self.multiplier = multiplier
        self.color_space = 'srgb'
        self.wavelength_range = '400.0 700.0'
        self.alpha = 1.0
    def writeXML(self, doc):
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
# light object --
#

class light():
    def __init__(self, params, name):
        self.params = params
        self.name = name
        self.color_name = self.name + '_exitance'
        self.color = cmds.getAttr(self.name+'.color')
        self.multiplier = cmds.getAttr(self.name+'.intensity')
        self.decay = cmds.getAttr(self.name+'.decayRate')
        m = cmds.getAttr(self.name+'.matrix')
        self.transform = [m[0],m[1],m[2],m[3]], [m[4],m[5],m[6],m[7]], [m[8],m[9],m[10],m[11]], [m[12],m[13],m[14],m[15]]
    def writeXML(self, doc):
        doc.startElement('light name="{0}" model="point_light"'.format(self.name))
        doc.appendElement('parameter name="exitance" value="{0}"'.format(self.color_name))
        writeTransform(doc, 1, self.transform)
        doc.endElement('light')

#
# shader object --
#

class material(): #object transform name
    def __init__(self, name): 
        #get shader name from transform name
        self.name = name
        self.shader_type = cmds.nodeType(self.name)
        print self.shader_type
        #for shaders with color & incandescence attributes interpret them as bsdf and edf
        if (self.shader_type == 'lambert') or (self.shader_type == 'blinn') or (self.shader_type == 'phong') or (self.shader_type == 'phongE'):
            self.bsdf_color = cmds.getAttr(self.name+'.color')
            try:
                self.bsd_texture = cmds.getAttr((cmds.connectionInfo((shader+'.color'), sourceFromDestination=True).split('.')[0]) + '.fileTextureName') #get connected texture file name
            except:
                self.bsd_texture = None
                print('no texture connected to {0} color'.format(self.name))
            self.edf_color = cmds.getAttr(self.name+'.incandescence')
            try:
                self.edf_texture = cmds.getAttr((cmds.connectionInfo((shader+'.incandescence'), sourceFromDestination=True).split('.')[0]) + '.fileTextureName') #get connected texture file name
            except:
                self.edf_texture = None
                print('no texture connected to {0} incandescence'.format(self.name))
        #for surface shaders interpret outColor as bsdf and edf
        elif self.shader_type == 'surfaceShader':
            self.bsdf_color = cmds.getAttr(self.name+'.outColor')
            try:
                self.bsd_texture = cmds.getAttr((cmds.connectionInfo((shader+'.outColor'), sourceFromDestination=True).split('.')[0]) + '.fileTextureName') #get connected texture file name
            except:
                self.bsd_texture = None
                print('no texture connected to {0} outColor'.format(self.name))
            self.edf_color = cmds.getAttr(self.name+'.outColor')
            try:
                self.edf_texture = cmds.getAttr((cmds.connectionInfo((shader+'.outColor'), sourceFromDestination=True).split('.')[0]) + '.fileTextureName') #get connected texture file name
            except:
                self.edf_texture = None
        #else use default shader
        else:
            self.name = 'default_texture'
            self.bsdf_color = [0.5, 0.5, 0.5]
            self.bsdf_texture = None
            self.edf_color = [0,0,0]
            self.edf_texture = None
            
#
# camera object --
#

class camera(): #(camera_name)
    def __init__(self, params, cam):
        self.params = params
        if self.params['sceneCameraDefaultThinLens'] or cmds.getAttr(cam+'.depthOfField'):
            self.model = 'thinlens_camera'
            self.f_stop = cmds.getAttr(cam+'.fStop')
            self.focal_distance = cmds.getAttr(cam+'.focusDistance') /10
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
        doc.startElement('camera name="{0}" model="{1}"'.format(self.name, self.model))
        doc.appendElement('parameter name="film_dimensions" value="{0} {1}"'.format(self.horizontal_fov, self.vertical_fov))
        doc.appendElement('parameter name="focal_length" value="{0}"'.format(self.focal_length))
        if self.model == 'thinlens_camera':
            print('exporting ' + self.name + ' as thinlens camera attribs')
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
    def __init__(self, name, output_file, assembly='main_assembly'):
        self.name = name
        self.output_file = output_file
        self.assembly = assembly
        # get material name
        shape = cmds.listRelatives(self.name, s=True)[0]
        shadingEngine = cmds.listConnections(shape, t='shadingEngine')[0]
        self.material = cmds.connectionInfo((shadingEngine + ".surfaceShader"),sourceFromDestination=True).split('.')[0] #find the attribute the surface shader is plugged into athen split off the attribute name to leave the shader name
        print('material = '+self.material)
        # transpose camera matrix -> XXX0, YYY0, ZZZ0, XYZ1
        m = cmds.getAttr(name+'.matrix')
        self.transform = [m[0],m[1],m[2],m[3]], [m[4],m[5],m[6],m[7]], [m[8],m[9],m[10],m[11]], [m[12],m[13],m[14],m[15]]
        
    def writeXMLObject(self, doc):
        doc.startElement('object name="{0}" model="mesh_object"'.format(self.assembly))
        doc.appendElement('parameter name="filename" value="{0}"'.format(self.output_file))
        doc.endElement('object>')
    def writeXMLInstance(self, doc):
        doc.startElement('object_instance name="{0}_inst" object="{1}.{2}"'.format(self.name, self.assembly, self.name,))
        writeTransform(doc)
        #doc.appendElement('<assign_material slot="0" material="{0}"/>'.format(self.material))
        doc.endElement('object_instance')
#
# assembly object --
#

class assembly():
    def __init__(self, params, name='main_assembly'):
        self.params = params
        self.name = name
        self.light_objects = []
        self.geo_objects = []
        self.mat_list = []
        self.mat_objects = []
        self.color_objects = []
        self.shader_objects = []
        self.bsdf_objects = []
        self.edf_objects = []

        #if name is default populate list with all lights otherwise just lights from set with the same name as the object
        if (self.name == 'main_assembly'):
            for light_shape in cmds.ls(lights=True):
                self.light_objects.append(light(self.params, cmds.listRelatives(light_shape, ad=True, ap=True)[0]))
        else:
            for light_shape in cmds.listRelatives('set1', typ='light'):
                self.light_objects.append(light(self.params, cmds.listRelatives(light_shape, ad=True, ap=True)[0]))
        #add light colors to list
        for light_object in self.light_objects:
            self.color_objects.append(color((light_object.color_name), light_object.color, light_object.multiplier))
        
        
        #if name is default populate list with all geometry otherwise just geometry from set with the same name as the object
        if (self.name == 'main_assembly'):
            #create a list of all geometry objects and itterate over them
            for obj in cmds.ls(g=True):
                #find the name of the transform connected to the shape and append a new geometry object to the list based on it
                self.geo_objects.append(geometry(cmds.listRelatives(obj, ad=True, ap=True)[0],('geo/'+self.name+'.obj'), self.name))
        else:
            for obj in cmds.listConnections(self.name, sh=True):
                self.geo_objects.append(geometry(obj, ('geo/'+self.name+'.obj'), self.name	))
                
        #populate list with individual materials
        for geo in self.geo_objects:
            if not geo.material in self.mat_list:
                print ('adding ' + geo.material + ' to mat_list')
                self.mat_list.append(geo.material)
                
        #populate list with material objects        
        for mat in self.mat_list:
            self.mat_objects.append(material(mat))
        
    def writeXML(self, doc):
        doc.startElement('assembly name="{0}"'.format(self.name))

        #write colors
        for col in self.color_objects:
             col.writeXML(doc)
        
        #write .obj object
        doc.startElement('object name="{0}" model="mesh_object"'.format(self.name))
        doc.appendElement('parameter name="filename" value="geo/{0}.obj"'.format(self.name))
        doc.endElement('object')
        
        #write lights
        for light_name in self.light_objects:
            light_name.writeXML(doc)
        
        #write geo object instances
        for geo in self.geo_objects:
            geo.writeXMLInstance(doc)
        
        doc.endElement('assembly')
        doc.startElement('assembly_instance name="{0}_inst" assembly="{1}"'.format(self.name, self.name))
        writeTransform(doc, self.params['scene_scale'])
        doc.endElement('assembly_instance')
        
        #select and export objects
        cmds.select(cl=True)
        for geo in self.geo_objects:
            cmds.select(geo.name, add=True)
        #create geo directory if it doesnt already exist
        if not os.path.exists(self.params['outputDir']+'/geo'):
            os.makedirs(self.params['outputDir']+'/geo')
        cmds.file(('{0}/{1}'.format(self.params['outputDir']+'/geo', (self.name + '.obj'))), force=True, options='groups=1;ptgroups=0;materials=0;smoothing=0;normals=1', type='OBJexport', exportSelected=True)
        cmds.select(cl=True)

#
# scene object --
#

class scene():
    def __init__(self,params):
        self.params = params
        self.assembly_list = []
    def writeXML(self, doc):
        doc.startElement('scene')
        #write cameras
        if self.params['sceneCameraExportAllCameras']:
            #export all cameras
            cam_list = []
            for c in cmds.listCameras(p=True):
                camera_instance = camera(self.params, c)
                camera_instance.writeXML(doc)
        else:
            #export only camera selected in output
            camera_instance = camera(self.params, self.params['outputCamera'])
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
        
        #create assemblys is any assembly names are present otherwise create default assembly
        if self.assembly_list:
            #for each assemply in assembly_list create an object and output its XML
            for a in self.assembly_list:
                new_assembly = assembly(self.params, a)
                new_assembly.writeXML(doc)
        else:
            new_assembly = assembly(self.params, 'main_assembly')
            new_assembly.writeXML(doc)
        doc.endElement('scene')

#
# output object --
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
# configurations object --
#

class configurations():
    def __init__(self, params):
        self.params = params
    def writeXML(self,doc):
        doc.startElement("configurations")
        #if 'customise interactive configuration' is set read customised values
        if self.params['customInteractiveConfigCheck']:
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
            doc.appendElement('configuration name="interactive" base="base_interactive"')
  
        #if 'customise final configuration' is set read customised values
        if cmds.checkBox('m2s_customFinalConfigCheck', query=True, value=True) == True:
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
            doc.appendElement('configuration name="final" base="base_final"')
        # begin adding custom configurations
        doc.endElement('configurations')
	
#
# writeXml Object --
#

class writeXml(): #(file_path)
    spaces_per_indentation_level = 4    
    def __init__(self, f_path):
        self.file_path = f_path
        self.indentation_level = 0
        self.file_object = None
        try:
            self.file_object = open(self.file_path, 'w') #open file for editing

        except IOError:
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
    params = getMayaParams()
    if not params['error']:
        print('--exporting to appleseed--')
        doc = writeXml('{0}/{1}'.format(params['outputDir'], params['fileName']))
        doc.appendLine('<?xml version="1.0" encoding="UTF-8"?>') # XML format string
        doc.appendLine('<!-- File generated by {0} version {1} visit {2} for more info and the latest super exciting release!-->'.format(script_name, version, more_info_url))
        doc.startElement('project')
        scene_element = scene(params)
        scene_element.writeXML(doc)
        output_element = output(params)
        output_element.writeXML(doc)
        config_element = configurations(params)
        config_element.writeXML(doc)
    
        doc.endElement('project')
        doc.close()
        print ('--export finished--')
    else:
        raise RuntimeError('check script editor for details')

#
# initiallise and show ui --
#

def m2s():
    mayaToAppleseedUi = cmds.loadUI(f="{0}/mayaToAppleseed.ui".format(os.path.dirname(__file__)))    
    #if the file has been saved set default file name to <scene_name>.appleseed
    if cmds.file(query=True, sceneName=True, shortName=True):
        cmds.textField('m2s_fileName', edit=True, text=(os.path.splitext(cmds.file(query=True, sceneName=True, shortName=True))[0] + '.appleseed'))
    else:
        cmds.textField('m2s_fileName', edit=True, text='file.xml')
    #populate output > camera dropdown menu with maya cameras
    for camera in cmds.listCameras(p=True):
        cmds.menuItem(parent='m2s_outputCamera', label=camera)
    #set default resolution to scene resolution
    cmds.textField('m2s_outputResWidth', edit=True, text=cmds.getAttr('defaultResolution.width'))
    cmds.textField('m2s_outputResHeight', edit=True, text=cmds.getAttr('defaultResolution.height'))
    #show window
    cmds.showWindow(mayaToAppleseedUi)
