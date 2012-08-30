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

import sys
import ms_commands
import signal
import math
import threading

sys.path.append(ms_commands.ROOT_DIRECTORY)

import appleseed as asr



class RendererController( asr.IRendererController):
    def __init__( self):
        super( RendererController, self).__init__()

        # catch Control-C
        signal.signal(signal.SIGINT, lambda signal, frame: self.__signal_handler( signal, frame))
        self.__abort = False
        self.__count = 0

    def __signal_handler( self, signal, frame):
        print "Ctrl+C!, aborting."
        self.__abort = True

    # This method is called before rendering begins.
    def on_rendering_begin( self):
        print "rendering begin"

    # This method is called after rendering has succeeded.
    def on_rendering_success( self):
        print "rendering success"

    # This method is called after rendering was aborted.
    def on_rendering_abort( self):
        print "rendering abort"

    # This method is called before rendering a single frame.
    def on_frame_begin( self):
        print "frame begin"

    # This method is called after rendering a single frame.
    def on_frame_end( self):
        print "frame end"

    def on_progress( self):
        self.__count += 1

        if self.__count == 200:
            sys.stdout.write('.')
            self.__count = 0

        if self.__abort:
            return asr.IRenderControllerStatus.AbortRendering

        return asr.IRenderControllerStatus.ContinueRendering



class TileCallback( asr.ITileCallback):
    def __init__( self):
        super( TileCallback, self).__init__()

    def pre_render( self, x, y, width, height):
        print "pre_render: x = %s, y = %s, width = %s, height = %s" % ( x, y, width, height)

    def post_render_tile( self, frame, tile_x, tile_y):
        print "post_render_tile: tile_x = %s, tile_y = %s" % ( tile_x, tile_y)

    def post_render( self, frame):
        print "post_render: frame = %s" & frame



class RenderThread( threading.Thread):
    def __init__( self, renderer):
        super( RenderThread, self).__init__()
        self.__renderer = renderer

    def run( self):
        self.__renderer.render()




def render():

    project = asr.Project( 'test project')
    project.add_default_configurations()

    renderer_controller = RendererController()

    renderer = asr.MasterRenderer( project, project.configurations()['final'].get_inherited_parameters(), renderer_controller )

    render_thread = RenderThread( renderer)
    render_thread.start()
    render_thread.join()

    # project.get_frame().write( "/projects/test/output/test.png")
    # asr.ProjectFileWriter().write( project, "/projects/test/output/test.appleseed")







