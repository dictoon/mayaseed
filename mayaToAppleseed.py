# mayaToAppleseed.py 

# WORK IN PROGRESS!!

# uncomment the next few lines replace the path and run them in the maya script editor to launch the script 
#--------------------maya command (python)--------------------
#import sys
#sys.path.append('/projects/mayaToAppleseed')
#import mayaToAppleseed
#reload(mayaToAppleseed)
#mayaToAppleseed.m2s()
#-------------------------------------------------------------


import maya.cmds as cmds
import os
import re

script_name = "mayaToAppleseed.py"
version = "0.01"
more_info_url = "https://github.com/jonathantopf/mayaToAppleseed"

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
# maya shader object --
#

class mayaShader(): #object transform name
    name = ""
    color = [0.5,0.5,0.5]
    color_texture = ""
    specular_color = [0.5,0.5,0.5]
    specular_color_texture = ""
    
    def __init__(self, obj): 
        #get shader name from transform name
        shape = cmds.listRelatives(obj, s=True)[0]
        shadingEngine = cmds.listConnections(shape, t='shadingEngine')[0]
        shader = cmds.connectionInfo((shadingEngine + ".surfaceShader"),sourceFromDestination=True).split('.')[0] #find the attribute the surface shader is plugged into athen split off the attribute name to leave the shader name
        self.name = shader
        
#
# maya camera object --
#

class camera(): #(camera_name)
    params = None
    name = ''
    model = 'pinhole_camera'
    controller_target = [0, 0, 0]
    film_dimensions = [1.417 , 0.945]
    focal_length = 35.000
    transform = [1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1] # XXX0, YYY0, ZZZ0, XYZ1
    #thin lens only params
    f_stop = 8.0
    focal_distance = 1
    diaphragm_blades = 0
    diaphragm_tilt_angle = 0.0
   
    def __init__(self, params, cam):
        self.params = params
        if self.params['sceneCameraDefaultThinLens'] or cmds.getAttr(cam+'.depthOfField'):
            self.model = 'thinlens_camera'
            self.f_stop = cmds.getAttr(cam+'.fStop')
            self.focal_distance = cmds.getAttr(cam+'.focusDistance')
        self.name = cam
        self.film_dimensions[0] = cmds.getAttr(cam+'.horizontalFilmAperture')
        self.film_dimensions[1] = cmds.getAttr(cam+'.verticalFilmAperture')
        self.focal_length = cmds.getAttr(cam+'.focalLength')
        # transpose camera matrix -> XXX0, YYY0, ZZZ0, XYZ1
        m = cmds.getAttr(cam+'.matrix')
        self.transform = [m[0],m[1],m[2],m[3]], [m[4],m[5],m[6],m[7]], [m[8],m[9],m[10],m[11]], [m[12],m[13],m[14],m[15]]
    
    def writeXML(self, doc):
        doc.startElement('<camera name="{0}" model="{1}">'.format(self.name, self.model))
        doc.appendElement('<parameter name="film_dimensions" value="{0} {1}"/>'.format(self.film_dimensions[0], self.film_dimensions[1]))
        doc.appendElement('<parameter name="focal_length" value="{0}" />'.format(self.focal_length))
        if self.model == 'thinlens_camera':
            print('exporting thinlens camera attribs')
            doc.appendElement('<parameter name="focal_distance" value="{0}" />'.format(self.focal_distance))
            doc.appendElement('<parameter name="f_stop" value="{0}" />'.format(self.f_stop))
            doc.appendElement('<parameter name="diaphragm_blades" value="{0}" />'.format(self.diaphragm_blades))
            doc.appendElement('<parameter name="diaphragm_tilt_angle" value="{0}"/>'.format(self.diaphragm_tilt_angle))
        #output transform matrix
        writeTransform(doc, self.transform)
        doc.endElement('</camera>')

#
# maya geometry object --
#

class geometry(): # (object_transfrm_name, obj_file)
    name = ""
    output_file =""
    shader = ""
    transform = [1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1] # XXX0, YYY0, ZZZ0, XYZ1
    
    def __init__(self, name, output_file):
        self.name = name
        self.output_file = output_file
        self.assembly = cmds.listSets(object=name)[0]
        # get shader name
        shape = cmds.listRelatives(name, s=True)[0]
        shadingEngine = cmds.listConnections(shape, t='shadingEngine')[0]
        shader_name = cmds.connectionInfo((shadingEngine + ".surfaceShader"),sourceFromDestination=True).split('.')[0] #find the attribute the surface shader is plugged into athen split off the attribute name to leave the shader name
        self.shader = shader_name
        # transpose camera matrix -> XXX0, YYY0, ZZZ0, XYZ1
        m = cmds.getAttr(name+'.matrix')
        self.transform = [m[0],m[1],m[2],m[3]], [m[4],m[5],m[6],m[7]], [m[8],m[9],m[10],m[11]], [m[12],m[13],m[14],m[15]]
        
    def writeXMLObject(self, doc):
        doc.startElement('<object name="{0}" model="mesh_object">'.format(self.name))
        doc.appendElement('<parameter name="filename" value="{0}"/>'.format(self.output_file))
        doc.endElement('</object>')
    def writeXMLInstance(self, doc):
        doc.startElement('<object_instance name="{0}_inst" object="{1}.{2}">'.format(self.name, self.name, self.name))
        writeTransform(doc)
        doc.endElement('</object_instance>')
#
# assembly object --
#

class assembly():
    def __init__(self, params, name):
        self.params = params
        self.name = name
        self.geo_objects = []
        for obj in cmds.listConnections(self.name, sh=True):
            print obj
            self.geo_objects.append(geometry(obj, (self.name+'.obj')))
            
        
    def writeXML(self, doc):
        doc.startElement('<assembly name="{0}">'.format(self.name))
        
        #write geo objects and object instances
        for geo in self.geo_objects:
            geo.writeXMLObject(doc)
        for geo in self.geo_objects:
            geo.writeXMLInstance(doc)
        
        doc.endElement('</assembly>')
        doc.startElement('<assembly_instance name="{0}_inst" assembly="{1}">'.format(self.name, self.name))
        writeTransform(doc)
        doc.endElement('</assembly_instance>')
        
        #select and export objects
        cmds.select(cl=True)
        for geo in self.geo_objects:
            cmds.select(geo.name, add=True)
        cmds.file(('{0}/{1}'.format(self.params['outputDir'], (self.name + '.obj'))), force=True, options='groups=1;ptgroups=0;materials=0;smoothing=0;normals=1', type='OBJexport', exportSelected=True)
        cmds.select(cl=True)

#
# scene object --
#

class scene():
    params = None
    assembly_list = []
    def __init__(self,params):
        self.params = params
    def writeXML(self, doc):
        doc.startElement('<scene>')
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
        # get maya geometry
        shape_list = cmds.ls(g=True, v=True) 
        geo_transform_list = []
        for g in shape_list:
            # add first connected transform to the list
            geo_transform_list.append(cmds.listRelatives(g, ad=True, ap=True)[0]) 

        for g in geo_transform_list:
            if not cmds.listSets(object=g)[0] in self.assembly_list:
                self.assembly_list.append(cmds.listSets(object=g)[0])
        
        #create assemblys is any assembly names are present otherwise create default assembly
        if self.assembly_list:
            #for each assemply in assembly_list create an object and output its XML
            for a in self.assembly_list:
                new_assembly = assembly(self.params, a)
                new_assembly.writeXML(doc)
        else:
            new_assembly = asembly(self.params, 'main_assembly')
            new_assembly.writeXML(doc)
        doc.endElement('</scene>')


#
# output object --
#

class output():
    params = None
    def __init__(self, params):
        self.params = params
    def writeXML(self, doc):
        doc.startElement('<output>')
        doc.startElement('<frame name="beauty">')
        doc.appendElement('<parameter name="camera" value="{0}" />'.format(self.params['outputCamera']))
        doc.appendElement('<parameter name="color_space" value="{0}" />'.format(self.params['outputColorSpace']))
        doc.appendElement('<parameter name="resolution" value="{0} {1}" />'.format(self.params['outputResWidth'], self.params['outputResHeight']))
        doc.endElement('</frame>')
        doc.endElement('</output>')

#
# configurations object --
#

class configurations():
    params = None
    def __init__(self, params):
        self.params = params
    def writeXML(self,doc):
        doc.startElement("<configurations>")
        #if 'customise interactive configuration' is set read customised values
        if self.params['customInteractiveConfigCheck']:
            doc.startElement('<configuration name="interactive" base="base_interactive">')
            engine = ''
            if self.params['customInteractiveConfigEngine'] == 'Path Tracing':
                engine = "pt"
            else:
                engine = "drt"
            doc.appendElement('<parameter name="lighting_engine" value="{0}"/>'.format(engine))
            doc.appendElement('<parameter name="min_samples" value="{0}" />'.format(self.params['customInteractiveConfigMinSamples']))
            doc.appendElement('<parameter name="max_samples" value="{0}" />'.format(self.params['customInteractiveConfigMaxSamples']))
            doc.endElement('</configuration>')
        else:# otherwise add default configurations
            doc.appendElement('<configuration name="interactive" base="base_interactive" />')
  
        #if 'customise final configuration' is set read customised values
        if cmds.checkBox('m2s_customFinalConfigCheck', query=True, value=True) == True:
            doc.startElement('<configuration name="final" base="base_final">')
            engine = ''
            if cmds.optionMenu('m2s_customFinalConfigEngine', query=True, value=True) == "Path Tracing":
                engine = 'pt'
            else:
                engine = 'drt'
            doc.appendElement('<parameter name="lighting_engine" value="{0}"/>'.format(engine))
            doc.appendElement('<parameter name="min_samples" value="{0}" />'.format(self.params['customFinalConfigMinSamples']))
            doc.appendElement('<parameter name="max_samples" value="{0}" />'.format(self.params['customFinalConfigMaxSamples']))
            doc.endElement("</configuration>")
        else:# otherwise add default configurations
            doc.appendElement('<configuration name="final" base="base_final" />')
        # begin adding custom configurations
        doc.endElement('</configurations>')
	

#
# writeXml Object --
#

class writeXml(): #(file_path)
    file_path = '/'
    indentation_level = 0
    spaces_per_indentation_level = 4
    file_object = None
    
    def __init__(self, f_path):
        self.file_path = f_path
        try:
            self.file_object = open(self.file_path, 'w') #open file for editing

        except IOError:
            raise RuntimeError('IO error: file not accesable')
            return
        
    def startElement(self,str):
        self.file_object.write(((self.indentation_level * self.spaces_per_indentation_level) * " ") + str + "\n")
        self.indentation_level += 1
        
    def endElement(self, str):
        self.indentation_level -= 1
        self.file_object.write(((self.indentation_level * self.spaces_per_indentation_level) * " ") + str + "\n")
        
    def appendElement(self, str):
        self.file_object.write(((self.indentation_level * self.spaces_per_indentation_level) * " ") + str + "\n")
        
    def close(self):
        self.file_object.close() #close file

#
# writeTransform function --
#

def writeTransform(doc, transform = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]):
    doc.startElement('<transform>')
    doc.startElement('<matrix>')

    doc.appendElement('{0:.16f} {1:.16f} {2:.16f} {3:.16f}'.format(transform[0][0], transform[1][0], transform[2][0], transform[3][0]))
    doc.appendElement('{0:.16f} {1:.16f} {2:.16f} {3:.16f}'.format(transform[0][1], transform[1][1], transform[2][1], transform[3][1]))
    doc.appendElement('{0:.16f} {1:.16f} {2:.16f} {3:.16f}'.format(transform[0][2], transform[1][2], transform[2][2], transform[3][2]))
    doc.appendElement('{0:.16f} {1:.16f} {2:.16f} {3:.16f}'.format(transform[0][3], transform[1][3], transform[2][3], transform[3][3]))	

    doc.endElement('</matrix>')
    doc.endElement('</transform>')

#
# build and export
#

def export():
    params = getMayaParams()
    if not params['error']:
        print('--exporting to appleseed--')
        doc = writeXml('{0}/{1}'.format(params['outputDir'], params['fileName']))
        doc.appendElement('<?xml version="1.0" encoding="UTF-8"?>') # XML format string
        doc.appendElement('<!-- File generated by {0} version {1} visit {2} for more info -->'.format(script_name, version, more_info_url))
        doc.startElement('<project>')
        scene_element = scene(params)
        scene_element.writeXML(doc)
        output_element = output(params)
        output_element.writeXML(doc)
        config_element = configurations(params)
        config_element.writeXML(doc)
    
        doc.endElement('</project>')
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

#
# read maya scene and generate objects --
#

# create and populate a list of mayaCamera objects
#cam_list = []
#for c in cmds.ls(ca=True, v=True):
#    cam_list.append(camera(getMayaParams(), c))

# create and polulate a list of mayaGeometry objects
shape_list = cmds.ls(g=True, v=True) # get maya geometry
geo_transform_list = []
for g in shape_list:
    geo_transform_list.append(cmds.listRelatives(g, ad=True, ap=True)[0]) # add first connected transform to the list

 