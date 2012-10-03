Mayaseed docs - Node Reference
==============================

This section contains information on the nodes that make up the Mayaseed plugin and their attributes.


ms_renderSettings node
----------------------

The ms\_renderSettings (render settings) node is the biggest node in the Mayaseed plugin and contains most of the attributes that you will use to control your export. 

It is also one of the places where you can start your export from, at the top of the render settings node's attribute editor there is a blue button marked **Export**. Use this button to start your export.

The following section is a list of attributes in the render settings node and a description of their functions.

>Note: The ms_renderSettings node's attributes are organised in a way that mirrors the internal file structure, so if an attribute seems like its in a strange place there is a good reason. By using Mayaseed you are also learning about appleseed at the same time.


###Export settings section###

####Output Directory####

This is where you tell Mayaseed where to export the appleseed scene file and other relevant files to. Any occurrence of `<ProjectDir>` will be replaced with the path to your current Maya project.

####Output File####

This is where you choose the name of your output file, the `#` character will be replaced with the frame number padded to 4 characters. So `my_scene.#.appleseed` will export as my_scene.0001.appleseed`. Any occurrence of `<FileName>` will be replaced with the name of the current Maya file.

####Convert Shading Nodes To Textures####

Use this checkbox to convert Maya shading networks to textures on export. If a color attribute has a shading network attached Mayaseed will check to see the shading network is a texture node. If not, with this option checked Mayaseed will bake the shading network to an .exr image. 

####Overwrite Existing Texture Files####

If this checkbox is checked then Maya will convert and overwrite texture files with every export.

####Export Camera Transformation Motion Blur####

This attribute turns camera transformation blur on.

####Export Assembly Transformation Motion Blur####

This attribute turns transformation blur on for all objects in the scene.

####Export Object Deformation Motion Blur####

This attribute turns deformation blur on for all mesh objects in the scene.

####Motion Samples####

Sets the number of motion samples to be used in motion blur to give the appearance of curved motion.

####Shutter Open Time####

This attribute is only a placeholder at this point.

####Shutter Close Time####

This attribute is only a placeholder at this point.

####Export Animation####

This attribute is only a placeholder at this point.

####Animation Start Frame####

This attribute is only a placeholder at this point.

####Animation End Frame####

This attribute is only a placeholder at this point.

####Export Animated Textures####

This attribute tells Mayaseed whether to export textures for every frame or only the first one. If animated textures is turned on, a textures directory will be present in the frame's sub directory otherwise a texture directory will be present in the frame's parent directory.


###Output Settings Section###

####Camera####

Use this attribute to select the camera you would like to export.

> Note: If you do not select a camera the export will fail.

####Resolution Width####

This attribute sets the width in pixels of the framebuffer.

####Resolution Height####

This attribute sets the height in pixels of the framebuffer.

####Color Space####

This sets the color space that appleseed will use, the default is **sRGB**.


###Environment Settings section###

####Environment####

A Maya scene can contain many environment nodes, here you can select which environment node to use in your export and also create new ones.


###Camera Settings Section###

####Export All Cameras####

Although appleseed can only use one camera at a time it is possible to have more than one included in the scene file, use this checkbox to export all the maya cameras. 

####Export All Cameras As Thinlens####

appleseed has two types of cameras: **pinhole** and **thin lens**, the main difference being that a thin lens camera can simulate depth of field and the pinhole cannot. By default Mayaseed will export cameras with depth of field turned off as pinhole and with cameras with depth of field turned on as thin lens. Use this option to force Mayaseed to export all cameras as thin lens.


###Configuration Settings Section###

appleseed configurations contain information on the rendering method and quality settings of a render. appleseed can have arbitrarily many of these render settings but must contain at least two, an **interactive** configuration and a **final** configuration. These configurations control the quality of appleseed's default interactive render and final render. Use this section to customize the settings for the **final** render configuration.

###Advanced settings###

This section contains attributes that are beyond normal export settings.

####Profile export####

This attribute turns on export profiling using the cProfile python module, see the script editor for the resulting information.


ms_environment node
-------------------

The ms\_environment (environment) node is used to control the environment settings for your export. Right now it could easily be implemented in the render settings node but when environment transformations are implemented in appleseed it will be useful to have the environment node as a separate entity with its own transform node.

Below is a list of the node's attributes and their functions.

####Model####

This drop down menu contains the different types of environment models that appleseed provides (below).

+ Constant Environment
+ Gradient Environment
+ Latitude-Longitude Map
+ Mirrorball Map

####Constant Exitance####

Use this attribute if you have selected **Constant Environment** as your model. 

> Note: only modify the color of this attribute, connecting a shading network will have no effect.

####Gradient Horizon Exitance####

Use this attribute to set the horizon color of the evironment if you have selected **Gradient Environment** as your model. 

> Note: only modify the color of this attribute, connecting a shading network will have no effect.

####Gradient Zenith Exitance####

Use this attribute to set the zenith (highest point) color of the environment if you have selected **Gradient Environment** as your model. 

> Note: only modify the color of this attribute, connecting a shading network will have no effect.

####Latitude Longitude Exitance####

Attach a texture node to this attribute if you have selected **Latitude-Longitude Map** as your environment model. The image should be in latitude-longitude format for correct results.

####Mirror Ball Exitance####

Attach a texture node to this attribute if you have selected **Mirror Ball Map** as your environment model.


ms\_appleseed\_material
---------------------

The `ms_appleseed_material` is a generic material that all objects that will be exported must have assigned. In appleseed you have a separate material slot for the front and back of an object but as Maya doesn't implement front and back materials in the same way the ms_appleseed_material has slots for front and back attributes in one material.

####Enable Front material####

This setting turns on generation of the front material.

####BSDF front colour####

Use this attribute to connect the outColor attribute from an appleseed BSDF.

####EDF front colour####

Use this attribute to connect the outColor attribute from an appleseed EDF.

####surface_shader front color####

Use this attribute to connect the outColor attribute from an appleseed surface shader.

####normal map front colour####

Use this attribute to connect the outColor attribute from a Maya File node.

####enable back material####

This setting turns on generation of the back material.

####duplicate front materials on back####

Use this material to turn on simple double sided shading mapping all the front attributes onto the back attributes.

####BSDF back colour####

Use this attribute to connect the outColor attribute from an appleseed BSDF.

####EDF back colour####

Use this attribute to connect the outColor attribute from an appleseed EDF.

####surface_shader back color####

Use this attribute to connect the outColor attribute from an appleseed surface_shader.

####normal map back colour####

Use this attribute to connect the outColor attribute from a Maya File node.

####alpha map colour####

Use this attribute to connect the outColor attribute from a Maya File node.


ms\_appleseed\_shading\_node
-------------------------

This is a generic container node and only has one output attribute `outColor` which is for connecting to an `ms_appleseed_material` or other `ms_appleseed_shading_node`'s. When one of the appleseed\_shading\_node's is created from the Mayaseed menu one of these nodes is instantiated with dynamic attributes generated from the `appleseedEntityDefs.xml`. 
