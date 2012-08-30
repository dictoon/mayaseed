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

import ms_read_params
import ms_export_read
import ms_export_translate
import time
import maya.cmds as cmds

# ms_export.py contains the entry point for the mayaseed export process, the export() function
# from here the three stages of the export are triggered, reading the maya scene, translating it into an appleseed project object heirarchy and writing it to disk

#****************************************************************************************************************************************************************************************************
# export() function *********************************************************************************************************************************************************************************
#****************************************************************************************************************************************************************************************************

def export(ms_rendersettings_node):

    #save start time of the export for later
    export_start_time = time.time()
    #get the parameters form the ms_rendersettings node
    params = ms_read_params.get(ms_rendersettings_node)

    if params['error']:
        cmds.error('en error occured whilst reading ' + ms_rendersettings_node)
        raise RuntimeError('check script editor for details')

    else:

        #set the current frame as the start_frame 
        start_frame = cmds.currentTime(query=True)
        end_frame = start_frame 

        #is animtion export is set, set the start end end frame
        if params['export_animation']:
            start_frame = params['animation_start_frame']
            end_frame = params['animation_end_frame']

        # instantiate a progress bar and add it to the params dict
        params['progress_bar'] = maya.mel.eval('$tmp = $gMainProgressBar');

        cmds.progressBar( params['progress_bar'], edit=True, beginProgress=True, isInterruptable=True, status='Exporting scene', maxValue=( 100 * ( (end_frame +  1) - start_frame) ) )

        #store the origibal time so we can return to it afte the export
        original_time = cmds.currentTime(query=True)

        #set the current time to the start frame of the animationn
        current_frame = start_frame
        
        #loop through frames and perform export
        while (current_frame  <= end_frame):

            #set the current maya time to the start time of the frame
            cmds.currentTime(current_frame)






            #begin exporting scene data
            print '*** exporting frame ', current_frame, '*************************'            

            frame_start_time = time.time()

            print 'exporting scene'
            maya_scene_data = ms_export_read.read(params)

            read_end_time = time.time()
            print 'read maya scene in', (read_end_time - frame_start_time), 'seconds'

            appleseed_object_heirarchy = ms_export_translate.render()
            #appleseed_object_heirarchy = ms_export_translate.translate(params, maya_scene_data)

            translate_end_time = time.time()
            print 'translated scene in', (translate_end_time - read_end_time), 'seconds'

            #ms_export_write.write()
            #ms_export_write.write(params, appleseed_object_heirarchy)

            write_end_time = time.time()
            print 'file written to disk in', (write_end_time - translate_end_time), 'seconds'

            print '*** finished exporting frame', current_frame, 'in', (frame_start_time - write_end_time), 'seconds *************************'






            #once the first frame has exported textures set exportTetures to false to prevent future frames from exporting
            if not params['animated_textures']:
                params['skip_textures'] = True
            
            current_frame += 1

        #finish export    
        export_time = time.time() - export_start_time

        #end the progress bar
        cmds.progressBar(params['progress_bar'], edit=True, endProgress=True)

        cmds.confirmDialog(message=('Export finished in ' + str(export_time) + ' seconds'), button='ok')
