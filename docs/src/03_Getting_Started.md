Mayaseed docs - Getting started
===============================


The Mayaseed menu
-----------------

The Mayaseed menu will appear when the plugin is correctly installed, if you can't see it make sure the plugin installed correctly and is enabled.


The Render Settings node
------------------------

The ms\_renderSettings (render settings) node is the workhorse of Mayaseed, it contains most of the settings to control your export and is also one of the places where you can launch the export. To export your scene you only need one ms\_renderSettings node but it is also possible to have many per scene, this can be useful for making proxy resolution renders or exporting for different render passes. 

>Note: The ms_renderSettings node's attributes are organised in a way that mirrors the internal file structure, so if an attribute seems like its in a strange place there is a good reason. By using Mayaseed you are also learning about appleseed at the same time.

Your first export
-----------------

To export a scene you first need to create a render settings node, to do this choose **Mayaseed -> create render settings node**.

With the latest release of Mayaseed this is all you need to do, your exports will be sent to a directory named *Mayaseed* on your Maya project. Of course there many customisations available in the *ms_rendersettings_node* but I'll leave you to explore them…