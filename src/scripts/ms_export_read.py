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



#****************************************************************************************************************************************************************************************************
# maya MClasses *************************************************************************************************************************************************************************************
#****************************************************************************************************************************************************************************************************


# MTransform ****************************************************************************************************************************************************************************************

class MTransform():
    def __init__(self, transform_name):
        self.transform_name = transform_name
        self.matrix = [cmds.xform(self.transform_name, query=True, ws=True, matrix=True)] #store in list se we can add motion samples

    def addTransformSample(self):
        self.matrix.append(cmds.xform(self.transform_name, query=True, ws=True, matrix=True)])

 
# MGeo *********************************************************************************************************************************************************************************************

class MGeo():
    def __init__(self, params, mesh_name):
        self.type = 'Mgeo'
        self.params = params
        self.shape_name = mesh_name
        self.safe_name = ms_commands.legalise)(self.shape_name)

        #create list of thransfrom parents, e.g. instances
        geo_transforms = cmds.listRelatives(mesh_name, ad=True, ap=True)
        self.transforms = []
        for transform in geo_transforms:
            self.transforms.append(MTransform(transform))

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

        #check if the shader is an ms_appleseed_material
        self.ms_shader = False
        if cmds.nodeType(shader) == 'ms_appleseed_material':
            self.ms_shader = True

    def addDeformSample(self, sample_number):
        file_path = os.path.join( params['output_dir'], params['geo_dir'], ('{0}.{1:03}.obj'.format(self.safe_name, sample_number)))
        self.obj_file_path.apend(file_path)
        ms_commands.export_obj(self.safe_name, file_path)

    def addTransformSample(self):
        for transform in self.transforms:
            transform.addTransformSample()


# MCam **********************************************************************************************************************************************************************************************

class MCam():
    def __init__(self, params, cam_name):
        self.type = 'MCam'
        self.params = params
        self.cam_name = cam_name
        self.transform = cmds.listRelatives(cam_name, ad=True, ap=True)[0]
        self.safe_name = legalise(cam_name)

        self.matrix = [cmds.xform(self.transform_name, query=True, ws=True, matrix=True)]
        
        self.focal_length = float(cmds.getAttr(cam_name + '.focalength')) / 1000
        self.f_stop = cmds.getAttr(self.cam_name + '.fStop')

        maya_resolution_aspect = float(params['output_res_width'])/float(params['output_res_height'])
        maya_film_aspect = cmds.getAttr(cam + '.horizontalFilmAperture') / cmds.getAttr(cam + '.verticalFilmAperture')

        if maya_resolution_aspect > maya_film_aspect:
            self.film_width = float(cmds.getAttr(self.cam_name + '.horizontalFilmAperture')) * inch_to_meter
            self.film_height = self.film_width / maya_resolution_aspect  
        else:
            self.film_height = float(cmds.getAttr(self.cam_name + '.verticalFilmAperture')) * inch_to_meter
            self.film_width = self.film_height * maya_resolution_aspect 

    def addTransformSample(self):
        self.matrix.append(cmds.xform(self.transform_name, query=True, ws=True, matrix=True)])


# MLight *******************************************************************************************************************************************************************************************

class MLight():
    def __init__(self, params, light_name):
        self.type = 'MLight'
        self.params = params
        self.light_name = light_name
        self.transform_name = cmds.listRelatives(light_name, ad=True, ap=True)[0]
        self.safe_name = legalise(transform_name)
        self.matrix = [cmds.xform(self.transform_name, query=True, ws=True, matrix=True)]

        self.color = cmds.getAttr(light_name + '.color')
        self.multiplier = cmds.getAttr(self.name+'.intensity')
        self.decay = cmds.getAttr(self.name+'.decayRate')
        self.inner_angle = cmds.getAttr(object + '.coneAngle')
        self.outer_angle = cmds.getAttr(object + '.coneAngle') + cmds.getAttr(object + '.penumbraAngle')

        if cmds.nodeType(object) == 'pointLight':
            self.model = 'pointLight'
        elif cmds.nodeType(object) == 'spotLight':
            self.model = 'spotLight'

    def addTransformSample(self):
        self.matrix.append(cmds.xform(self.transform_name, query=True, ws=True, matrix=True)])

# MMaterial *****************************************************************************************************************************************************************************************

class MMaterial():
	def __init__(self, material_name):
		pass


#****************************************************************************************************************************************************************************************************
# read() function ***********************************************************************************************************************************************************************************
#****************************************************************************************************************************************************************************************************

def get(params):

    maya_geo = []
    maya_lights = []
    maya_camera = MCam(params, params['output_camera'])

    #create MObjects and first sample of the scene data
    for geo in cmds.ls(typ='mesh'):
        if ms_commands.isExportable(geo):
            maya_geo.append(MGeo(params, geo))

    for light in cmds.ls(lt=True):
        maya_lights.append(MLight(params, light))


    if params['export_transformation_blur'] or params['export_camera_blur'] or params['export_deformation_blur']:

        #create following n samples for the scene date

        #store the star time of the export
        start_time = cmds.currentTime(query=True)
        motion_samples = self.params['motion_samples']

        if motion_samples < 2:
            cmds.warning('motion samples is set too low, must be atleast 2, using 2')
            motion_samples = 2

        sample_interval = 1.0/(motion_samples - 1)

        cmds.currentTime(start_time - 1)
        for i in range(motion_samples):
            new_time = start_time + (sample_interval * i)
            cmds.currentTime(new_time)
            cmds.refresh()

            #add transform sampels
            for geo in maya_geo:
                geo.addTransformSample()

            for light in maya_lights:
                light.addTransformSample()

            #add camera samples
            if params[exportCameraBlur]:
                maya_camera.addTransformSample()

            #add deform samples
            for geo in maya_geo:
                geo.addDeformSample(i)

    return (maya_geo, maya_lights, maya_camera)









