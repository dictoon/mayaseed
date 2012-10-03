Mayaseed docs - Plugin structure
================================

Plugin point of entry
---------------------

In order for Maya to find the Mayaseed plugin, it must be installed in one of the default Maya **plugin MAYA\_SCRIPT\_PATH** variables (you can view them by using the `getenv MAYA_PLUGIN_PATH` MEL command). As Mayaseed is made up of many files, it's impractical so what we do is edit/create the **userSetup.mel** file that Maya runs on startup to add the Mayaseed plugin path to MAYA_PLUGIN_PATH. We also need to add the Mayaseed scripts and graphics paths to the **MAYA\_SCRIPT\_PATH** variable at this time.

Now when Maya starts it sees that the **mayaseed.py** script in the plugins directory contains a node definition and automatically adds the plugin to the Maya plugin manager. Once the user enables the plugin the `initializePlugin()` function from **mayaseed.py** is called. The `initializePlugin()` function registers the new Mayaseed nodes with Maya and also calls `ms_menu.createMenu()` and `ms_menu.buildMenu()` to create the Mayaseed menu. Now the new nodes are registered with Maya and the scripts directory is in the PATH you can create any of the Mayaseed nodes using the regular MEL or Python commands and use any of the Mayaseed modules using the regular old `import ms_commands` etc.

At this point the plugin would work just fine but the nodes' attribute editor would look confusing so we have **AE...Template.mel** files to make the layout a bit more sensible. These are MEL files that Maya looks for in the **MAYA\_SCRIPT\_PATH** using the pattern `AE<node name>Template.mel`. This contains a simple script to layout the nodes attributes and also lets you define some more complicated functions to handle any special drop down menus etc; this is also where the Export button is added to the attribute editor.

Miscellaneous Utilities
-----------------------

Inside the **tools** subdirectory there are a few useful scripts for rendering your .appleseed scenes which are listed below. 


***render\_sequence.py***

This script builds a UI for batch rendering multiple .appleseed scenes. It requires the PySide Python Qt bindings to run. If you don't have these installed you can download them here:

http://qt-project.org/wiki/PySideDownloads

***watch\_folder.py***

This script is still in development but it can be used together with Dropbox to create a simple renderfarm. 
