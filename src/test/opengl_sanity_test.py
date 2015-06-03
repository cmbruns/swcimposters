#!/bin/env python

# Author Christopher M. Bruns

# Copyright 2012 HHMI. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
# 
#     Redistributions of source code must retain the above copyright notice, 
#     this list of conditions and the following disclaimer.
#     Redistributions in binary form must reproduce the above copyright notice, 
#     this list of conditions and the following disclaimer in the documentation 
#     and/or other materials provided with the distribution.
#     Neither the name of HHMI nor the names of its contributors may be used to 
#     endorse or promote products derived from this software without specific 
#     prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
import sys

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'


class SimpleImposterViewer:
		def __init__(self):
			# Rotation angle for animation
			self.yrot = 0.0
			# Number of the glut window.
			self.window = 0
			self.ambientOnly = False
			self.diffuseOnly = False
			
		# A general OpenGL initialization function.  Sets all of the initial parameters. 
		def InitGL(self, Width, Height):				# We call this right after our OpenGL window is created.
			glClearColor(0.5, 0.5, 0.5, 0.0)	# This Will Clear The Background Color To Black
			glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
			glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
			glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
			glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading
			
			glMatrixMode(GL_PROJECTION)
			glLoadIdentity()					# Reset The Projection Matrix
												# Calculate The Aspect Ratio Of The Window
			gluPerspective(45.0, float(Width)/float(Height), 0.1, 20.0)
		
			glMatrixMode(GL_MODELVIEW)
			
			glLightfv(GL_LIGHT1, GL_POSITION, GLfloat_4(-5,3,3,0) )
			# glLightfv(GL_LIGHT1, GL_POSITION, GLfloat_4(0, 0, 10, 0) )
			
			glLightfv( GL_LIGHT1, GL_AMBIENT, GLfloat_4(0.5,1,0.2, 1.0) )
			glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
			glEnable(GL_COLOR_MATERIAL)
			if self.diffuseOnly:
				glLightfv( GL_LIGHT1, GL_AMBIENT, GLfloat_4(0,0,0,0) )
				glLightfv(GL_LIGHT1, GL_DIFFUSE, GLfloat_3(.8,.8,.8))
				glLightfv(GL_LIGHT1, GL_SPECULAR, GLfloat_3(0,0,0) )
				glMaterialfv(GL_FRONT, GL_SPECULAR, GLfloat_4(0,0,0) )
				glMateriali(GL_FRONT, GL_SHININESS, 150)				
			elif self.ambientOnly:
				glLightfv( GL_LIGHT1, GL_AMBIENT, GLfloat_4(0.2,0.2,0.2, 1.0) )
				glLightfv(GL_LIGHT1, GL_DIFFUSE, GLfloat_3(0,0,0) )
				glLightfv(GL_LIGHT1, GL_SPECULAR, GLfloat_3(0,0,0) )
				glMaterialfv(GL_FRONT, GL_SPECULAR, GLfloat_4(0,0,0) )
				glMateriali(GL_FRONT, GL_SHININESS, 150)				
			else:
				glLightfv( GL_LIGHT1, GL_AMBIENT, GLfloat_4(0.2,0.2,0.2,0) )
				glLightfv(GL_LIGHT1, GL_DIFFUSE, GLfloat_3(.8,.8,.8))
				glLightfv(GL_LIGHT1, GL_SPECULAR, GLfloat_3(.8,.8,.8) )
				glMaterialfv(GL_FRONT, GL_SPECULAR, GLfloat_4(0.8, 0.8, 0.8, 1.0) )
				glMateriali(GL_FRONT, GL_SHININESS, 150)
			
			# Read utility functions from file
			with open ("../glsl/imposter_fns_frag.glsl", "r") as myfile:
				frag_fns_str = myfile.read()
				# print frag_fns_str
				frag_fns = shaders.compileShader(frag_fns_str, GL_FRAGMENT_SHADER)
				
			
			self.green_shader = shaders.compileProgram(
				shaders.compileShader(
						"""
						#version 120
						
						void main() { 
							gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
						}
						""", GL_VERTEX_SHADER), 
				shaders.compileShader(frag_fns_str, GL_FRAGMENT_SHADER),
				shaders.compileShader(
						"""
						#version 120
						
						void set_green_color();
						
						void main() { 
							set_green_color();
						}
						""", GL_FRAGMENT_SHADER)
			)
			
			self.light_rig_shader = shaders.compileProgram(
				shaders.compileShader(
						"""
						#version 120
						
						varying vec3 normal;
						varying vec4 pos1;
						varying vec3 surface_color;
						
						void main() { 
							pos1 = gl_ModelViewMatrix * gl_Vertex;
							normal = normalize(gl_NormalMatrix * gl_Normal);
							gl_Position = gl_ProjectionMatrix * pos1;
							surface_color = gl_Color.rgb;
						}
						""", GL_VERTEX_SHADER), 
				shaders.compileShader(frag_fns_str, GL_FRAGMENT_SHADER),
				shaders.compileShader(
						"""
						#version 120
						
						varying vec3 normal;
						varying vec4 pos1;
						varying vec3 surface_color;
						
						vec3 light_rig(vec4 pos, vec3 normal, vec3 color);
						
						void main() {
						    vec3 s2 = surface_color;
							gl_FragColor = vec4(light_rig(pos1, normalize(normal), s2), 1);
						}
						""", GL_FRAGMENT_SHADER)
			)
		
		# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
		def ReSizeGLScene(self, Width, Height):
			if Height == 0:						# Prevent A Divide By Zero If The Window Is Too Small 
				Height = 1
		
			glViewport(0, 0, Width, Height)		# Reset The Current Viewport And Perspective Transformation
			glMatrixMode(GL_PROJECTION)
			glLoadIdentity()
			gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
			glMatrixMode(GL_MODELVIEW)
		
		def drawTriangle(self):
			glBegin(GL_TRIANGLES)
			glColor3f(1.0,0.0,0.0)          # Red
			glVertex3f( 0.0, 1.0, 0.0)          # Top Of Triangle (Front)
			glColor3f(0.0,1.0,0.0)          # Green
			glVertex3f(-1.0,-1.0, 1.0)          # Left Of Triangle (Front)
			glColor3f(0.0,0.0,1.0)          # Blue
			glVertex3f( 1.0,-1.0, 1.0)          # Right Of Triangle (Front)
			glEnd()
		
		# The main drawing function. 
		def DrawGLScene(self):
			
			glEnable( GL_LIGHTING ) 
			glEnable(GL_LIGHT1)
			glDisable(GL_LIGHT0)
			
			# Clear The Screen And The Depth Buffer
			glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
			
			glLoadIdentity()					# Reset The View 
			glTranslatef(0.0,0.0,-6.0);             # MoveInto The Screen
			glRotatef(self.yrot, 0.0,1.0,0.0);             # Rotate The Pyramid On It's Y Axis
			
			# Leftmost sphere is shaded using the fixed function pipeline
			glTranslatef(-1.6,0.0,0);             # Move Left
			# drawTriangle()
			glColor3f(0.8, 0.5, 0.2)
			shaders.glUseProgram(0)
			glutSolidSphere(1.0, 150, 150)
			shaders.glUseProgram(0)

			# Middle sphere is (eventually) an imposter			
			glTranslatef( 1.6,0.0,0);             # Move Right
			glColor3f(0.2, 0.5, 0.8)
			# TODO - use as imposter
			# shaders.glUseProgram(self.green_shader)
			glutSolidCube(2.0)
			# drawTriangle()
			shaders.glUseProgram(0)
			
			# Right sphere is a standard mesh, shaded with GLSL
			glTranslatef( 1.6, 0.0, 0);             # Move Right
			glColor3f(0.2, 0.8, 0.5)
			# TODO - use as imposter
			shaders.glUseProgram(self.light_rig_shader)
			glColor3f(0.8, 0.5, 0.2)
			glutSolidSphere(1.0, 40, 40)
			# drawTriangle()
			shaders.glUseProgram(0)
			
			#  since this is double buffered, swap the buffers to display what just got drawn. 
			glutSwapBuffers()
			self.yrot += 1.00
			# print self.yrot
		
		
		# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
		def keyPressed(self, *args):
			# If escape is pressed, kill everything.
			if args[0] == ESCAPE:
				sys.exit()
		
		def show(self):
			# pass arguments to init
			glutInit(sys.argv)
		
			# Select type of Display mode:   
			#  Double buffer 
			#  RGBA color
			# Alpha components supported 
			# Depth buffer
			glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
			
			# get a 640 x 480 window 
			glutInitWindowSize(640, 480)
			
			# the window starts at the upper left corner of the screen 
			glutInitWindowPosition(0, 0)
			
			# Okay, like the C version we retain the window id to use when closing, but for those of you new
			# to Python (like myself), remember this assignment would make the variable local and not global
			# if it weren't for the global declaration at the start of main.
			self.window = glutCreateWindow("Jeff Molofee's GL Code Tutorial ... NeHe '99")
		
		   	# Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
			# set the function pointer and invoke a function to actually register the callback, otherwise it
			# would be very much like the C version of the code.	
			glutDisplayFunc(self.DrawGLScene)
			
			# Uncomment this line to get full screen.
			#glutFullScreen()
		
			# When we are doing nothing, redraw the scene.
			glutIdleFunc(self.DrawGLScene)
			
			# Register the function called when our window is resized.
			glutReshapeFunc(self.ReSizeGLScene)
			
			# Register the function called when the keyboard is pressed.  
			glutKeyboardFunc(self.keyPressed)
		
			# Initialize our window. 
			self.InitGL(640, 480)
		
			# Start Event Processing Engine	
			glutMainLoop()

# Print message to console, and kick off the main to get it rolling.
if __name__ == "__main__":
	print "Hit ESC key to quit."
	v = SimpleImposterViewer()
	v.show()
		
