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

With the latest release of Mayaseed this is all you need to do, your exports will be sent to a directory named *Mayaseed* on your Maya project. Of course there many customisations available in the *ms\_rendersettings\_node* but I'll leave you to explore them…

Materials
---------

Appleseed has a small number of powerful materials and shading models available which are deceptively difficult to translate to from the Maya shading nodes. Because of this rather attempting to translate the maya materials during export Mayaseed instead adds Maya equivalents of all the appleseed shading nodes. Appleseed also differs from Maya in how it deals with sidedness of an object so this we provide a generic *ms\_appleseed\_material* which you can create from the *Mayaseed menu* and must attach to any object you wish to render. 

The *ms\_appleseed\_material* node contains a lot of attributes the ones you are mainly concerned with are the BSDF, EDF and Surrface Shader. 

**BSDF**

This stands for Bidirectional Scattering Distribution Function and is where you define how light is reflects off a surface. To define the materials BSDF you can select a BSDF node from the *Create BSDF* menu and connect the *outColor* attribute to the BSDF attribute of your *ms\_applesed\_material* node.

**EDF**

This stands for Emission Distribution Function and is where you define how light is emitted from a surface. To define the materials EDF select an EDF node from the *Create EDF* menu and connect the *outColor* attribute to the EDF attribute of your *ms\_applesed\_material* node.

**Surface Shader**

The Surface Shader controls how an object is rendered when it is directly visible to the camera, you will more often than not want to use a *physical* surface shader which you can create from the *Create Surface Shader* menu item. The surface shader in the only attribute that needs to be defined, without this connection appleseed will throw an error. 



