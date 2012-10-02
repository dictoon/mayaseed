Mayaseed docs - Plugin structure
================================

Plugin point of entry
---------------------

In order for Maya to find the Mayaseed plugin it must be installed in one of the default maya **plugin MAYA\_SCRIPT\_PATH** variables (you can view them by using this MEL command `getenv MAYA_PLUGIN_PATH`). As Mayaseed consists of more than file that makes up the plugin its impractical so what we do is edit/create the **userSetup.mel** maya file that maya runs on startup to add the Mayaseed plugin path to MAYA_PLUGIN_PATH. We also need to add the Mayaseed scrips and Graphics paths to the **MAYA\_SCRIPT\_PATH** variable at this time. Now when maya starts it sees that the **mayaseed.py** script in the Plugins directory contains a node definition and automatically adds the plugin to the maya plugin manager. Once the user enables the plugin the `initializePlugin()` function is called from **mayaseed.py**. The `initializePlugin()` function registers the new Mayaseed nodes with maya and also calls `ms_menu.createMenu()` and `ms_menu.buildMenu()` to create the Mayaseed menu. Now the new nodes are registered with maya and the scripts directory is in the PATH you can create any of the Mayaseed nodes using the regular MEL or Python commands and use any of the Mayaseed modules using regular old `import ms_commands` etc. At this point the plugin would work just fine but the nodes' attribute editor would look confusing so we have **AETemplate.mel** files to make the layout a bit more sensible. These are MEL files that Maya looks for in the **MAYA\_SCRIPT\_PATH** using the pattern `AE<node name>Template.mel`. This contains a simple script to layout the nodes attributes and also lets you define some more complicated functions to handle any special drop down menus etc; this is where the export button is added to the attribute editor.

Directories and files
---------------------

You will find the following files and folders inside the Mayaseed directory that make up the Mayaseed plugin. 

+ graphics (directory)
 + mayaseed_graphic.png
+ INSTALL.txt
+ docs
 + Mayaseed_Docs....html
 + SRC
  + Mayaseed_Docs....md
+ open\_me\_to\_install.ma
+ plugins (directory)
 + mayaseed.py
+ README.txt
+ scripts
 + about.txt
 + AEms\_environmentTemplate.mel
 + AEms\_renderSettingsTemplate.mel
 + AEms\_appleseed\_shading\_nodeTemplate.mel
 + AEms\_appleseed\_materialTemplate.mel
 + appleseedEntityDefs.xml
 + mayaseed.ui
 + ms_commands.py
 + ms_export.py
 + ms_menu.py
+ tools
 + ms\_export\_obj (directory)
     + src (directory)
 	     + cmake (directory)
 	 + ms\_export\_obj.cpp
 + render\_sequence.py
 + watch\_folder.py
 
***graphics (directory)***

The **graphics** directory contains any graphics used in the ui. 


***INSTALL.txt***

This file contains instructions on how to install Mayaseed, the instructions are mirrored in the Mayaseed docs but are included here just in case.


***docs (directory)***

Contains all the Mayaseed documentation


***Mayaseed_Docs….html & Mayaseed\_Docs.md***

The **Mayaseed\_Docs.html** faile are generated from the **Mayaseed\_Docs.md** files that you can find in the docs/src directory. The .md file is a plain text file formatted using the markdown language.


***open\_me\_to\_install.ma***

**open\_me\_to\_install.ma** is a regular maya file that contains a python script node that executes on opening. The python script adds the Mayaseed plugins and scripts directory to the maya PATH so that maya can find the source files.


***plugins (directory)***

This directory contains the main plugin python file meaning it contains a single file that defines the Mayaseed nodes.


***mayaseed.py***

This file contains the code that defines the ms_renderSettings node and the ms_environment node.


***README.txt***

Simple text file containing information about Mayaseed.


***scripts (directory)***

The scripts directory contain all the functions, classes and attribute editor templates plus a few other things. 


***about.txt***

**about.txt** contains the text that the **About Mayaseed** dialogue displays.


***AEms\_environmentTemplate.mel***

This file describes how the ms_environment node is displayed in the attribute editor.


***AEms\_renderSettingsTemplate.mel***

This file describes how the ms_renderSettings node is displayed in the attribute editor.

****AEms\_appleseed\_shading\_nodeTemplate.mel***

This file describes how the AEms\_appleseed\_shading\_node node is displayed in the attribute editor.

****AEms\_appleseed\_materialTemplate.mel***

This file describes how the AEms\_appleseed_\materialTemplate node is displayed in the attribute editor.

***appleseedEntityDefs.xml***

The appleseed entity defs file contains the material, bsdf, edf and surface_shader definitions. Mayaseed parses this file to create the translated material nodes in maya.

***ms\_commands.py***

**ms\_commands.py** contains commands used in the Mayaseed menu and utility variables,functions and classes for the **ms\_export** module. 


***ms\_export.py***

**ms\_export.py** contains the **export()** function that does most of the hard work in translating the maya scene to the .appleseed format. Broadly speaking a **writeXML** object is handed down through each XML entity in the appleseed scene description writing to the file as it goes.


***ms\_menu.py***

This python script sets up the Mayaseed menu and is called by **mayaseed.py** in the **initializePlugin()** function. The **uninitializePlugin()** function also calls this module to delete the Mayaseed menu when the plugin is unloaded.

***tools (directory)***

Contains any scripts that are not directly used within Mayaseed.

***ms\_export\_obj (directory)***

Contains the source code for the c++ obj exporter

***render\_sequence.py***

This script builds a gui for batch rendering multiple .appleseed scenes. It requires pyside Qt bindings to run. If you don't have these installed you can download them here:

http://qt-project.org/wiki/PySideDownloads

***watch\_folder.py***

This script is still in development but it can be used together with dropbox to create a simple renderfarm. 



