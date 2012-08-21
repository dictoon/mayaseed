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

# ms_export_readpy contains definitions of a set of classes designed to mirror the nodes in a maya scene
# there are two main reaons for the intermediate step of building a representation of the maya scene in the program
#     1: the script can gather all motion samples for the scene in one go meaning the time slider doesnt need to jump back and forth for each object during export
#     2: to cut down on querying maya through the maya api, querying the maya api is slower than reading values from memory, this way we only have to query maya once per attribute

#****************************************************************************************************************************************************************************************************
# maya MClasses *************************************************************************************************************************************************************************************
#****************************************************************************************************************************************************************************************************


# MTransform ****************************************************************************************************************************************************************************************

class MTransform():
    def __init__(self, params, parent=False, transform_name):
        self.params = params
        self.parent = parent
        self.name = transform_name
        self.matrix = [cmds.xform(self.name, query=True, matrix=True)] #store in list se we can add motion samples
        self.rotate_pivot = cmds.getAttr(self.name + '.rotatePivot') 
        self.scale_pivot = cmds.getAttr(self.name + '.scalePivot') 
        self.child_meshs = []
        self.child_transforms = []
        self.child_lights = []
        #self.child_cameras = []


        for child in cmds.listRelatives(self.name):
        	nodeType = cmds.nodeType(child)
            if ms_commands.isExportable(child)
            	if nodeType == 'mesh':
            		self.child_meshs.append(MGeo(self.params, self, child))
            	elif nodeType == 'transform':
            		self.child_transforms.append(MTransform(, self.params, self, child))
            	elif nodeType == 'pointLight' or 'spotLight':
            		self.child_lights.append(MLight(self.params, self, child))

                # still deciding how cameras shoud be handled...

                # elif nodeType == 'camera':
                #     if not cmds.getAttr(child + '.orthographic'):
                #         self.child_cameras.append(MCam(self.params, self, child))


    def addTransformSample(self):
        self.matrix.append(cmds.xform(self.transform_name, query=True, matrix=True))

        for child in self.child_transforms:
        	child.addTransformSample()

    def addDeformSample(self, sample_number):
        for mesh in self.child_meshs:
            mesh.addDeformSample(sample_number):
        for transform in self.child_transforms:
            transform.addDeformSample(sample_number)
 
# MGeo *********************************************************************************************************************************************************************************************

class MGeo():
    def __init__(self, params, parent=False, mesh_name):
        self.instance_of = False
        self.params = params
        self.parent = parent
        self.name = mesh_name
        self.safe_name = ms_commands.legalise)(self.name)

        self.obj_file_path = [os.path.join( params['output_dir'], params['geo_dir'], ('{0}.{1:03}.obj'.format(self.safe_name, 0) ) )]
        ms_commands.export_obj(self.safe_name, self.obj_file_path[0])

        #get shader name
        self.shader_name = ""
        shading_engine = cmds.listConnections(shape_node, t='shadingEngine')
        if shading_engine:
            connected_shaders = cmds.listConnections(shading_engine[0] + ".surfaceShader")
            if connected_shaders:
                #if its an appleseed material
                shader_name = connected_shaders[0]
        self.shader_safe_name = ms_commands.legalise(self.shader_name)

        #check if the shader is an ms_appleseed_material
        self.ms_appleseed_material = False
        if cmds.nodeType(shader) == 'ms_appleseed_material':
            self.ms_appleseed_material = MAsMaterial(shader_name)

    def addDeformSample(self, sample_number):
        file_path = os.path.join( params['output_dir'], params['geo_dir'], ('{0}.{1:03}.obj'.format(self.safe_name, sample_number)))
        self.obj_file_path.apend(file_path)
        ms_commands.export_obj(self.safe_name, file_path)



# MCam **********************************************************************************************************************************************************************************************

# although maya cameras exist in the maya node graph they are not instantiated like this in the read process
# this is because appleseed places them outside of the assembly heirarchy and because if this they must have a world space matrix, this also allows for easy seperation of camera and transformation blur

class MCam():
    def __init__(self, params, cam_name):
        self.params = params
        self.name = cam_name
        self.transform_name = cmds.listRelatives(self.name, ap=True)[0]
        self.safe_name = legalise(cam_name)        
        self.focal_length = float(cmds.getAttr(cam_name + '.focalength')) / 1000
        self.f_stop = cmds.getAttr(self.name + '.fStop')
        self.matrix = [cmds.xform(self.transform_name, query=True, ws=True, matrix=True)]

        maya_resolution_aspect = float(params['output_res_width'])/float(params['output_res_height'])
        maya_film_aspect = cmds.getAttr(cam + '.horizontalFilmAperture') / cmds.getAttr(cam + '.verticalFilmAperture')

        if maya_resolution_aspect > maya_film_aspect:
            self.film_width = float(cmds.getAttr(self.name + '.horizontalFilmAperture')) * inch_to_meter
            self.film_height = self.film_width / maya_resolution_aspect  
        else:
            self.film_height = float(cmds.getAttr(self.name + '.verticalFilmAperture')) * inch_to_meter
            self.film_width = self.film_height * maya_resolution_aspect 

    def addTransformSample(self):
        self.matrix.append(cmds.xform(self.transform_name, query=True, ws=True, matrix=True))

# MLight *******************************************************************************************************************************************************************************************

class MLight():
    def __init__(self, params, parent=False, light_name):
        self.params = params
        self.parent = parent
        self.name = light_name
        self.safe_name = legalise(self.name)

        self.color = cmds.getAttr(light_name + '.color')
        self.multiplier = cmds.getAttr(self.name+'.intensity')
        self.decay = cmds.getAttr(self.name+'.decayRate')
        self.inner_angle = cmds.getAttr(object + '.coneAngle')
        self.outer_angle = cmds.getAttr(object + '.coneAngle') + cmds.getAttr(object + '.penumbraAngle')

        if cmds.nodeType(object) == 'pointLight':
            self.model = 'pointLight'
        elif cmds.nodeType(object) == 'spotLight':
            self.model = 'spotLight'


# MAsMaterial *****************************************************************************************************************************************************************************************

class MAsMaterial():
	def __init__(self, params, parent=False, material_name):
		self.params = params
		self.name = material_name
		self.safe_name = legalise(self.name)
		self.shading_nodes = []

		self.bsdf_front = self.getMayaAttr(material_name + '.BSDF_front_color')
		self.edf_front = self.getMayaAttr(material_name + '.EDF_front_color')
		self.surface_shader_front = self.getMayaAttr(material_name + '.surface_shader_front_color')
		self.normal_map_front = self.getMayaAttr(material_name + '.normal_map_front_color')
		self.alpha_map = self.getMayaAttr(material_name + '.alpha_map_color')

		#only use front shaders on back if box is checked
        duplicate_shaders = cmds.self.getMayaAttr(name + '.duplcated_front_attributes_on_back')
		if not duplicate_shaders:
			self.bsdf_back = self.getMayaAttr(material_name + '.BSDF_back_color')
			self.edf_back = self.getMayaAttr(material_name + '.EDF_back_color')
			self.surface_shader_back = self.getMayaAttr(material_name + '.surface_shader_back_color')
			self.nornal_map_back = self.getMayaAttrz(material_name + '.normal_map_back_color')

            self.shader_connections = [self.bsdf_front,
                                  self.bsdf_back,
                                  self.edf_front,
                                  self.edf_back,
                                  self.surface_shader_front,
                                  self.surface_shader_back]

            self.texture_connections = [self.normal_map_front,
                                   self.normal_map_back,
                                   self.alpha_map]

		else: 
			self.bsdf_back, self.edf_back, self.surface_shader_back, self.normal_map_back = self.bsdf_front, self.edf_front, self.surface_shader_front, self.normal_map_front

            self.shader_connections = [self.bsdf_front,
                                       self.edf_front,
                                       self.surface_shader_front]

            self.texture_connections = [self.normal_map_front,
                                        self.alpha_map]

    def getMayaAttr(self, attr_name):
        connection = cmds.listConnections(attr_name)
        if connection:
            if cmds.nodeType(connection[0]) == 'ms_appleseed_shading_node':
                return MAsShadingNode(self.params, connection[0])
            elif cmds.nodeType(connection[0]) == 'file':
                return MTextureNode(self.params, connection[0])

        else:
            return False
        
# MAsShadingNode *****************************************************************************************************************************************************************************************

class MAsShadingNode():
	def __init__(self, params, node_name):
		self.params = params
		self.name = node_name
		self.safe_name = legalise(self.name)

        self.type = cmds.getAttr(self.name + '.node_type')      #bsdf, edf etc
        self.model = cmds.getAttr(self.name + '.node_model')    #lambertian etc
        self.child_shading_nodes = []
        self.attributes = dict()
        self.colors = []
        self.textures = []

        #add the correct attributes based on the entity defs xml
        for attribute_key in params['entityDefs'][self.model].attributes.keys():
            self.attributes[attribute_key] = ''

        for attribute_key in self.attributes.keys():
            maya_attribute = self.name + '.' + attribute_key

            #create variable to story the final string value
            attribute_value = ''

            #if the attribute is a color/entity 

            if params['entityDefs'][self.model].attributes[attribute_key].type == 'entity_picker':

                #get attribute color value
                attribute_color = cmds.getAttr(maya_attribute)[0]
                connected_node = False

                #check for connected node
                connection = cmds.listConnections(maya_attribute)
                if connection:
                    connected_node = connection[0]

                #if tehre is a node connected
                if connected_node:

                    #if the node is an appleseed shading node
                    if cmds.nodeType(connected_node) == 'ms_appleseed_shading_node':
                        attribute_value = MAsShadingNode(self.params, connected_node)
                        self.child_shading_nodes = self.child_shading_nodes + [attribute_value] + attribute_value.child_shading_nodes
                        self.colors = self.colors + attribute_value.colors
                        self.textures = self.textures + attribute_value.textures

                    #else if its a maya texture node
                    elif cmds.nodeType(connected_node) == 'file':
                        attribute_value = MTextureNode(self.params, connected_node)
                        self.textures = self.textures + [attribute_value]

                    #if the node is unrecignised bake take an exception to the rule of rebuilding the maya scene exactly and return an MTextureNode instead
                    else:
                        if self.params['convertShadingNodes']:
                            #convert texture and get path
                            output_texture = os.path.join(params['tex_dir'], (connected_node + '.exr'))
                            texture = convertConnectionToImage(self.name, self.attribute_key, output_texture, resolution=1024)
                            attribute_value = MTextureNode((connected_node + '_texture'), (os.path.join(params['tex_dir'], os.path.split(texture)[1])))
                            self.textures = self.textures + [attribute_value]

                #no node is connecetd just use the color value
                else:
                    #if its not black it must be a color so create a color node
                    if attribute_color != (0,0,0):
                        color_name = self.name + '_' + attribute_key + '_color'
                        attribute_value = MColor(color_name, attribute_color)
                        self.colors = self.colors + [attribute_value]

            #skip any attribute that is a drop down menu, its not implimented yet
            elif params['entityDefs'][self.model].attributes[attribute_key].type == 'dropdown_list': 
                pass
            #the node must be a text entity
            else:
                attribute_value = str(cmds.getAttr(maya_attribute))

            #add attribute to dict
            self.attributes[attribute_key] = attribute_value    

# MTextureNode **************************************************************************************************************************************************************************************


class MTexureNode():
	def __init__(self, params, node_name, file_name=False):
		self.params = params
		self.name = node_name
		self.safe_name = legalise(self.name)
        self.color_space = 'srgb'
        self.texture_path = ms_commands.getFileTextureName(self.name)

# MColor ********************************************************************************************************************************************************************************************

# MColor is one of the few of these clases that does not have a direct maya node equivilent
# this is helpful for later on when translating colors 
# for this reason the the word 'Node' is not included in the name
class MColor():
    def __init__(self, name, color):
        self.name = name
        self.color = color


#****************************************************************************************************************************************************************************************************
# read() function ***********************************************************************************************************************************************************************************
#****************************************************************************************************************************************************************************************************

# the get() function is the entry point for this script, starts the process of creating a object model of the maya scene

def read(params):
    #get the camera
    maya_camera = MCam(params['output_camera'])

    #the maya scene is stored as a list of root transforms that contain mesh's/geometry/lights as children
    maya_root_transforms = []
    start_time = cmds.currentTime(query=True)

    #find all root transforms and create Mtransforms from them
    for maya_transform in cmds.ls(tr=True):
        if ms_commands.isExportable(maya_transform):
            if not cmds.listRelatives(maya_transform, ap=True):
                transform_object = MTransform(params, False, maya_transform)

    if params['export_transformation_blur'] or params['export_camera_blur'] or params['export_deformation_blur']:
        #store the star time of the export
        start_time = cmds.currentTime(query=True)
        motion_samples = self.params['motion_samples']

        #make sure that there is > 1 motion samples
        if motion_samples < 2:
            cmds.warninig('Motion samples is set too low, must be atleast 2, using 2')
            motion_samples = 2

        sample_interval = 1.0/(motion_samples - 1)

        for i in range(motion_samples):
            new_time = start_time + (sample_interval * i)
            cmds.currentTime(new_time)
            cmds.refresh()

            for transform in maya_root_transforms:
                if params['export_transformation_blur'] or params['export_camera_blur']:
                    transform.addTransformSample()
                if params['export_deformation_blur']:
                    transform.addDeformSample(i)


    # put playhead back at start of frame
    cmds.currentTime(start_time)


    return {'root_transforms' : maya_root_transforms, 'camera' : maya_camera}









