#!/bin/env python

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'

# Number of the glut window.
window = 0

# A general OpenGL initialization function.  Sets all of the initial parameters. 
def InitGL(Width, Height):				# We call this right after our OpenGL window is created.
	glClearColor(0.5, 0.5, 0.5, 0.0)	# This Will Clear The Background Color To Black
	glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
	glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
	glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
	glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading
	
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()					# Reset The Projection Matrix
										# Calculate The Aspect Ratio Of The Window
	gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)

	glMatrixMode(GL_MODELVIEW)
	
	glLightfv( GL_LIGHT1, GL_AMBIENT, GLfloat_4(0.2, .2, .2, 1.0) )
	glLightfv(GL_LIGHT1, GL_DIFFUSE, GLfloat_3(.8,.8,.8))
	glLightfv(GL_LIGHT1, GL_POSITION, GLfloat_4(-2,0,3,1) )
	glColorMaterial(GL_FRONT, GL_DIFFUSE)
	glEnable(GL_COLOR_MATERIAL)

# The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
def ReSizeGLScene(Width, Height):
	if Height == 0:						# Prevent A Divide By Zero If The Window Is Too Small 
		Height = 1

	glViewport(0, 0, Width, Height)		# Reset The Current Viewport And Perspective Transformation
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
	glMatrixMode(GL_MODELVIEW)

def drawTriangle():
	glBegin(GL_TRIANGLES)
	glColor3f(1.0,0.0,0.0)          # Red
	glVertex3f( 0.0, 1.0, 0.0)          # Top Of Triangle (Front)
	glColor3f(0.0,1.0,0.0)          # Green
	glVertex3f(-1.0,-1.0, 1.0)          # Left Of Triangle (Front)
	glColor3f(0.0,0.0,1.0)          # Blue
	glVertex3f( 1.0,-1.0, 1.0)          # Right Of Triangle (Front)
	glEnd()

def drawCube():
	glBegin(GL_TRIANGLES)
	glColor3f(1.0,0.0,0.0)          # Red
	glVertex3f( 0.0, 1.0, 0.0)          # Top Of Triangle (Front)
	glColor3f(0.0,1.0,0.0)          # Green
	glVertex3f(-1.0,-1.0, 1.0)          # Left Of Triangle (Front)
	glColor3f(0.0,0.0,1.0)          # Blue
	glVertex3f( 1.0,-1.0, 1.0)          # Right Of Triangle (Front)
	glEnd()

# The main drawing function. 
yrot = 0.00
def DrawGLScene():
	global yrot
	
	glEnable( GL_LIGHTING ) 
	glEnable(GL_LIGHT1)
	glDisable(GL_LIGHT0)
	
	# Clear The Screen And The Depth Buffer
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	
	glLoadIdentity()					# Reset The View 
	glTranslatef(0.0,0.0,-6.0);             # MoveInto The Screen
	glRotatef(yrot, 0.0,1.0,0.0);             # Rotate The Pyramid On It's Y Axis
	
	glTranslatef(-0.8,0.0,0);             # Move Left
	# drawTriangle()
	glColor3f(0.8, 0.5, 0.2)
	glutSolidSphere(1.0, 10, 10)
	
	glTranslatef( 1.6,0.0,0);             # Move Right
	glColor3f(0.2, 0.5, 0.8)
	glutSolidCube(2.0)
	drawTriangle()
	
	#  since this is double buffered, swap the buffers to display what just got drawn. 
	glutSwapBuffers()
	yrot += 1.00
	# print yrot


# The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
def keyPressed(*args):
	global window
	# If escape is pressed, kill everything.
	if args[0] == ESCAPE:
		sys.exit()

def main():
	global window
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
	window = glutCreateWindow("Jeff Molofee's GL Code Tutorial ... NeHe '99")

   	# Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
	# set the function pointer and invoke a function to actually register the callback, otherwise it
	# would be very much like the C version of the code.	
	glutDisplayFunc(DrawGLScene)
	
	# Uncomment this line to get full screen.
	#glutFullScreen()

	# When we are doing nothing, redraw the scene.
	glutIdleFunc(DrawGLScene)
	
	# Register the function called when our window is resized.
	glutReshapeFunc(ReSizeGLScene)
	
	# Register the function called when the keyboard is pressed.  
	glutKeyboardFunc(keyPressed)

	# Initialize our window. 
	InitGL(640, 480)

	# Start Event Processing Engine	
	glutMainLoop()

# Print message to console, and kick off the main to get it rolling.
if __name__ == "__main__":
	print "Hit ESC key to quit."
	main()
		
