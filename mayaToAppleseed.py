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

#
# maya camera object --
#

class mayaCamera():
    name = ""
    model = "pinhole_camera"
    controller_target = [0, 0, 0]
    film_dimensions = [1.417 , 0.945]
    focal_length = 35.000
    transform = [1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1] # XXX0, YYY0, ZZZ0, XYZ1
   
    def __init__(self, cam):
        self.name = cam
        self.film_dimensions[0] = cmds.getAttr(cam+'.horizontalFilmAperture')
        self.film_dimensions[1] = cmds.getAttr(cam+'.verticalFilmAperture')
        self.focal_length = cmds.getAttr(cam+'.focalLength')
        # transpose camera matrix -> XXX0, YYY0, ZZZ0, XYZ1
        m = cmds.getAttr(cam+'.matrix')
        self.transform = [m[0],m[1],m[2],m[3]], [m[4],m[5],m[6],m[7]], [m[8],m[9],m[10],m[11]], [m[12],m[13],m[14],m[15]]
    
    def info(self):
        print("name: {0}".format(self.name))
        print("camera model: {0}".format(self.model))
        print("controller_target: {0}".format(self.controller_target))
        print("film dimensions: {0}".format(self.film_dimensions))
        print("focal length: {0}".format(self.focal_length))
        print("transform matrix: {0} # XXX0 YYY0 ZZZ0 XYZ1\n".format(self.transform))

#
# maya geometry object --
#

class mayaGeometry():
    name = ""
    transform = [1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1] # XXX0, YYY0, ZZZ0, XYZ1
    outPutFile = ""
    assembly = "assembly"
    
    def __init__(self,obj):
        self.name = obj    
	
	


#
# read maya scene and generate objects --
#

# create and populate a list of mayaCamera objects
cam_list = []
for c in cmds.ls(ca=True, v=True):
    cam_list.append(mayaCamera(c))

# create and polulate a list of mayaGeometry objects
shape_list = cmds.ls(g=True, v=True) # get maya geometry
geo_transform_list = []
for g in shape_list:
    geo_transform_list.append(cmds.listRelatives(g, ad=True, ap=True)[0]) # add first connected transform to the list

    






#
# laod ui --
#

def m2s():
    mayaToAppleseedUi = cmds.loadUI(f="{0}/mayaToAppleseed.ui".format(os.path.dirname(__file__)))    
    cmds.showWindow(mayaToAppleseedUi)


#
# return list of assemblies
#



