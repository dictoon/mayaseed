Mayaseed docs - Python Module reference
=======================================

With Mayaseed correctly installed you also have the following new Python modules available to you:

+ ms_commands
+ ms_export

This document lists some of the more useful functions in these modules.

ms_commands module
------------------

**ms_commands** is where all the common functions, classes and variables reside, this section describes them. 

###Variable: ms\_commands.MAYASEED_VERSION####

This variable will return the current Mayaseed version.

###Variable: ms\_commands.MAYASEED_URL###

This variable will return the URL of the Mayaseed website.

###Variable: ms\_commands.APPLESEED_URL###

This variable will return the URL of the appleseed website.

###Variable: ms\_commands.ROOT_DIRECTORY###

This variable will return the URL of the Mayaseed install's root directory.

###Function: ms\_commands.convertConnectionToImage(String:shader, String:attribute, String:dest\_file, Int:resolution=1024, Boolean:pass_through=False) Returns String:dest\_file###

This function will bake a given shading connection to an image file. 

####Argument: String:shader####

Name of the shader. e.g. "Lambert1".

####Argument: String:attribute####

The name of the attribute you want to bake. e.g. "Color".

####Argument: String:dest\_file####

The destination of the file you'd like to export.

####Argument: Int:resolution####

The resolution of the image you would like to bake. Images are always square.

####Argument: Boolean:pass_through=False####

Set this argument to True if you'd like to skip connection baking.

###Function: convertTexToExr(String:file\_path, String:dest\_dir, Boolean: overwrite=True, Boolean: pass_through=False) Returns String:dest_file###

Use this function to convert an image to an .exr file using the **imf_copy** utility that ships with Maya. The function returns a string containing the path to the destination file.

####Argument: String:file\_path####

File path of the image to be converted.

####Argument: String:dest\_dir####

The directory that you would like to save the converted image to. 

> Note: The converted image will have the same name as the source file but with the .exr extension.

####Argument: Boolean:overwrite = True####

By default Mayaseed will overwrite any images that have the same name as the output file, set this argument to False if you want to cancel image conversion for existing images.

####Argument: Boolean:pass_through=False####

Set this argument to True if you'd like to skip export of the textures but still return a file path. Useful if you want to skip the actual file conversion for non animated textures.


###Function: ms\_commands.getEntityDefs(String:xml\_file\_path) Returns Dict###

This function is used to retrieve a dict containing definitions of all the available appleseed nodes.

####Argument: String:xml\_file\_path####

This argument is a string pointing to the path of the appleseed exported **appleseedEntityDefs.xml**. 

###Function: createShadingNode(String:Model, Bool:entity_defs_obj=False) Returns String:shading_node_name###

This function looks up the model argument in the appleseedEntityDefs.xml file and returns an ms_appleseed_shading_node initialized with the correct attributes.

###Function: convertAllMaterials():###

This function converts all translatable materials in the scene to ms_appleseed_materials and assigns them a random hardware render color.

###Function: convertSelectedMaterials()###

This function converts all eligible materials in the current selection list to ms_appleseed_materials.


ms_export module
----------------

This module contains the main bulk of the code that handles the export and essentially only has one useful function.

###Function: ms_export.export(String:render_settings_node)###

This function is the workhorse of Mayaseed and does all the work in translating, exporting and writing your scene to disk based on the settings from your render settings node.

####Argument: String:String:render_settings_node####

This string is the name of the render settings node that contains the settings of your export.