'''
Created on Jun 4, 2015

@author: Christopher M. Bruns

Simple example using GLFW
'''

import glfw
from OpenGL.GL import *
import sys

class GlfwExample:
    "Hello world example of OpenGL window using glfw"
    def __init__(self):
        print "Hello"
        self.renderLoop()
        
    def initGL(self):
        if not glfw.init():
            sys.exit(1)
        self.window = glfw.create_window(640, 480, "Hello", None, None)
        print self.window
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)
        glfw.set_key_callback(self.window, self.key_callback)
        glClearColor(0.5, 0.5, 0.5, 1)
    
    def destroyGL(self):
        glfw.destroy_window(self.window)
        glfw.terminate()
        
    def key_callback(self, window, key, scancode, action, mods):
        print "key_callback"
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)

    def renderFrame(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
    def renderLoop(self):
        self.initGL()
        while not glfw.window_should_close(self.window):
            w, h = glfw.get_framebuffer_size(self.window)
            self.renderFrame()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        self.destroyGL()


if __name__ == '__main__':
    GlfwExample()
    