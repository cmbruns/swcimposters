#!/bin/env python

# Author Christopher M. Bruns

# Copyright 2010 Howard Hughes Medical Institute.
# All rights reserved.
# Use is subject to Janelia Farm Research Campus Software Copyright 1.1
# license terms ( http://license.janelia.org/license/jfrc_copyright_1_1.html ).
 
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import shaders
import sys
import math

# Some api in the chain is translating the keystrokes to this octal string
# so instead of saying: ESCAPE = 27, we use the following.
ESCAPE = '\033'


class Vec3():
    def __init__(self, data):
        assert len(data) == 3
        self._data = data

    def cross(self, rhs):
        return Vec3([
            self[1]*rhs[2] - self[2]*rhs[1],
            self[2]*rhs[0] - self[0]*rhs[2],
            self[0]*rhs[1] - self[1]*rhs[0], ])
        
    def dot(self, other):
        return sum([a*b for a, b in zip(self, other)])
    
    def norm(self):
        return math.sqrt(self.normSquared())
    
    def normSquared(self):
        return self.dot(self)
    
    def __len__(self):
        return len(self._data)
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __add__(self, other):
        return Vec3( [l+r for l,r in zip(self, other)] )
    
    def __radd__(self, other):
        return Vec3( [r+l for l,r in zip(self, other)] )
    
    def __sub__(self, other):
        return Vec3( [l-r for l,r in zip(self, other)] )
    
    def __rsub__(self, other):
        return Vec3( [r-l for l,r in zip(self, other)] )
    
    def __mul__(self, other):
        return Vec3( [l*other for l in self] )

    def __rmul__(self, other):
        return Vec3( [other*l for l in self] )
    
    def __div__(self, other):
        return Vec3( [l/other for l in self] )
    

class ConeSegment():
    # Cone segment that exactly joins two spheres
    def __init__(self, sphere1, sphere2):
        self.sphere1 = sphere1
        self.sphere2 = sphere2
        cs1 = Vec3(sphere1.center)
        cs2 = Vec3(sphere2.center)
        rs1 = sphere1.radius
        rs2 = sphere2.radius
        # Swap so r2 is always the largest
        if rs2 < rs1:
            rs1, rs2 = rs2, rs1
            cs1, cs2 = cs2, cs1
        # Shift cone parts to fit radius offset
        d = (cs2 - cs1).norm() # distance between sphere centers
        # half cone angle, to just touch each sphere
        sinAlpha = (rs2 - rs1) / d;
        cosAlpha = math.sqrt(1 - sinAlpha*sinAlpha)
        # Actual cone terminal radii might be smaller than sphere radii
        r1 = cosAlpha * rs1
        r2 = cosAlpha * rs2
        # Cone termini might not lie at sphere centers
        aHat = (cs1 - cs2) / d
        dC1 = sinAlpha * rs1 * aHat
        dC2 = sinAlpha * rs2 * aHat
        # Cone termini
        c1 = cs1 + dC1
        c2 = cs2 + dC2
        # Final cone parameters
        self.axis = (c1 - c2) / 2.0
        self.length = self.axis.norm() * 2.0
        self.center = (c1 + c2) / 2.0
        self.taper = (r2 - r1) / self.length
        self.radius = (r1 + r2) / 2.0
        self.r1 = r1
        self.r2 = r2

    def generateBoundingGeometryImmediate(self):
        "This method should be developed into a host imposter geometry example"
        # TODO - correct this shape for cone
        
        # Compute principal axes of bounding geometry
        d = self.axis.norm()
        xHat = self.axis / d # X along cone axis
        # Y along any orthogonal axis
        # To avoid numerical problems, try two different ways to create first orthogonal vector
        yHat1 = xHat.cross([1.0, 0.0, 0.0])
        yHat2 = xHat.cross([0.0, 0.0, 1.0])
        if yHat1.normSquared() >= yHat2.normSquared():
            yHat = yHat1
        else:
            yHat = yHat2
        yHat = yHat / yHat.norm()
        zHat = xHat.cross(yHat) # Third and final axis is simple
        
        # Draw bounding box geometry, three faces at a time
        # Bottom front top
        x = self.center[0]
        y = self.center[1]
        z = self.center[2]
        glBegin(GL_TRIANGLE_STRIP)
        for corner in [
                    [-1, -1, -1], [1, -1, -1], [-1, -1, 1], [1, -1, 1], # bottom 
                    [-1, 1, 1], [1, 1, 1], # front
                    [-1, 1, -1], [1, 1, -1], # top
                     ]:
            # Encode imposter geometry offset from sphere center into normal attribute
            # X axis points toward smaller end of cone
            if corner[0] > 0:
                r = self.r1 # smaller end
            else:
                r = self.r2 # larger end
            p = (   corner[0] * xHat * d
                  + corner[1] * yHat * r
                  + corner[2] * zHat * r )
            glNormal3f(p[0], p[1], p[2])
            # Position attribute always contains cone centroid and central radius
            glVertex4f(x, y, z, self.radius)
            # Encode additional parameters, cone axis and taper, in 
            glTexCoord4f(self.axis[0], self.axis[1], self.axis[2], self.taper)
        glEnd()
        # left back right
        glBegin(GL_TRIANGLE_STRIP)
        for corner in [
                    [-1, -1, 1], [-1, 1, 1], [-1, -1, -1], [-1, 1, -1], # left 
                    [1, -1, -1], [1, 1, -1], # back 
                    [1, -1, 1], [1, 1, 1] # right,
                     ]:
            # Encode imposter geometry offset from sphere center into normal attribute
            # X axis points toward smaller end of cone
            if corner[0] > 0:
                r = self.r1 # smaller end
            else:
                r = self.r2 # larger end
            p = (   corner[0] * xHat * d
                  + corner[1] * yHat * r
                  + corner[2] * zHat * r )
            glNormal3f(p[0], p[1], p[2])
            # Position attribute always contains cone centroid and central radius
            glVertex4f(x, y, z, self.radius)        
            # Encode additional parameters, cone axis and taper, in 
            glTexCoord4f(self.axis[0], self.axis[1], self.axis[2], self.taper)
        glEnd()


class Sphere():
    "Class representing a sphere to be rendered"
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        
    def generateBoundingGeometryImmediate(self):
        "This method should be developed into a host imposter geometry example"
        # Draw bounding cube geometry, three faces at a time
        # Bottom front top
        x = self.center[0]
        y = self.center[1]
        z = self.center[2]
        glBegin(GL_TRIANGLE_STRIP)
        for corner in [
                    [-1, -1, -1], [1, -1, -1], [-1, -1, 1], [1, -1, 1], # bottom 
                    [-1, 1, 1], [1, 1, 1], # front
                    [-1, 1, -1], [1, 1, -1], # top
                     ]:
            # Encode imposter geometry offset from sphere center into normal attribute
            glNormal3f(corner[0]*self.radius, corner[1]*self.radius, corner[2]*self.radius)
            # Position attribute always contains sphere center and radius
            glVertex4f(x, y, z, self.radius)        
        glEnd()
        # left back right
        glBegin(GL_TRIANGLE_STRIP)
        for corner in [
                    [-1, -1, 1], [-1, 1, 1], [-1, -1, -1], [-1, 1, -1], # left 
                    [1, -1, -1], [1, 1, -1], # back 
                    [1, -1, 1], [1, 1, 1] # right,
                     ]:
            # Encode imposter geometry offset from sphere center into normal attribute
            glNormal3f(corner[0]*self.radius, corner[1]*self.radius, corner[2]*self.radius)
            # Position attribute always contains sphere center and radius
            glVertex4f(x, y, z, self.radius)        
        glEnd()


class SimpleImposterViewer:
        def __init__(self):
            # Rotation angle for animation
            self.yrot = 0.0
            # Number of the glut window.
            self.window = 0
            self.ambientOnly = False
            self.diffuseOnly = False
            
        # A general OpenGL initialization function.  Sets all of the initial parameters. 
        def InitGL(self, Width, Height):                # We call this right after our OpenGL window is created.
            glClearColor(0.5, 0.5, 0.5, 0.0)    # This Will Clear The Background Color To Black
            glClearDepth(1.0)                    # Enables Clearing Of The Depth Buffer
            glDepthFunc(GL_LESS)                # The Type Of Depth Test To Do
            glEnable(GL_DEPTH_TEST)                # Enables Depth Testing
            glShadeModel(GL_SMOOTH)                # Enables Smooth Color Shading
            glEnable(GL_CULL_FACE) # use face culling, so I can verify that imposter geometry uses front faces
            
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()                    # Reset The Projection Matrix
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
            with open ("../glsl/imposter_fns_frag120.glsl", "r") as myfile:
                frag_fns_str = myfile.read()
            with open ("../glsl/imposter_fns120.glsl", "r") as myfile:
                glsl_fns_str = myfile.read()
                
            # Create a test shader for debugging, which just colors everything green.
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

            # Create another shader that illuminates standard mesh geometry with             
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
                shaders.compileShader(glsl_fns_str, GL_FRAGMENT_SHADER),
                shaders.compileShader(
                        """
                        #version 120
                        
                        varying vec3 normal;
                        varying vec4 pos1;
                        varying vec3 surface_color;
                        
                        vec3 light_rig(vec4 pos, vec3 normal, vec3 color);
                        
                        void main() {
                            vec3 s2 = surface_color;
                            gl_FragColor = vec4(
                                light_rig(pos1, normalize(normal), surface_color),
                                1);
                        }
                        """, GL_FRAGMENT_SHADER)
            )

            # Create shader for sphere imposters        
            self.sphere_shader = shaders.compileProgram(
                shaders.compileShader(glsl_fns_str, GL_VERTEX_SHADER),
                shaders.compileShader(
                        """
                        #version 120
                        
                        varying vec4 pos1;
                        varying vec4 surface_color;
                        
                        varying float radius;
                        varying vec2 pc_c2;
                        varying vec3 center;
                        
                        // defined in imposter_fns120.glsl
                        vec2 sphere_linear_coeffs(vec3 center, float radius, vec3 pos);

                        void main() {
                            // imposter geometry is sum of sphere center and normal
                            vec4 pos_local = vec4(gl_Vertex.xyz + gl_Normal.xyz, 1);
                            radius = gl_Vertex.w;
                            
                            pos1 = gl_ModelViewMatrix * pos_local;
                            gl_Position = gl_ProjectionMatrix * pos1;
                            surface_color = gl_Color.rgba;
                            
                            // TODO - hard coding sphere parameters for the moment...
                            // radius = 1.0; // TODO - test non-1.0 values
                            vec4 c = gl_ModelViewMatrix * vec4(gl_Vertex.xyz, 1);
                            center = c.xyz/c.w;
                            pc_c2 = sphere_linear_coeffs(center, radius, pos1.xyz/pos1.w);
                        }
                        """, GL_VERTEX_SHADER), 
                shaders.compileShader(glsl_fns_str, GL_FRAGMENT_SHADER),
                shaders.compileShader(
                        """
                        #version 120

                        varying vec4 pos1;
                        varying vec4 surface_color;
                        varying float radius;
                        varying vec3 center;
                        varying vec2 pc_c2;
                        
                        // defined in imposter_fns120.glsl
                        vec2 sphere_nonlinear_coeffs(vec3 pos, vec2 pc_c2);
                        vec3 sphere_surface_from_coeffs(vec3 pos, vec2 pc_c2, vec2 a2_d);
                        vec3 light_rig(vec4 pos, vec3 normal, vec3 color);
                        float fragDepthFromEyeXyz(vec3 eyeXyz);
                        
                        void main() {
                            vec3 pos = pos1.xyz/pos1.w;
                            vec2 a2_d = sphere_nonlinear_coeffs(pos, pc_c2);
                            if (a2_d.y <= 0)
                                discard; // Point does not intersect sphere
                            vec3 s = sphere_surface_from_coeffs(pos, pc_c2, a2_d);
                            vec3 normal = 1.0 / radius * (s - center);
                            gl_FragColor = vec4(
                                light_rig(vec4(s, 1), normal, surface_color.rgb),
                                1);
                            gl_FragDepth = fragDepthFromEyeXyz(s);
                        }
                        """, GL_FRAGMENT_SHADER)
            )
            
            # Create shader for sphere imposters        
            self.cone_shader = shaders.compileProgram(
                shaders.compileShader(glsl_fns_str, GL_VERTEX_SHADER),
                shaders.compileShader(
                        """
                        #version 120
                        
                        varying vec4 pos1;
                        varying vec4 surface_color;
                        
                        varying float radius;
                        varying vec3 tap_qec_qeb;
                        varying vec3 qe_undot_half_a;
                        varying vec3 center;
                        
                        // defined in imposter_fns120.glsl
                        vec3 cone_linear_coeffs1(vec3 center, float radius, vec3 axis, float taper, vec3 pos);
                        vec3 cone_linear_coeffs2(vec3 center, float radius, vec3 axis, float taper, vec3 pos);

                        void main() {
                            // imposter geometry is sum of sphere center and normal
                            vec4 pos_local = vec4(gl_Vertex.xyz + gl_Normal.xyz, 1);
                            radius = gl_Vertex.w;
                            
                            pos1 = gl_ModelViewMatrix * pos_local;
                            gl_Position = gl_ProjectionMatrix * pos1;
                            surface_color = gl_Color.rgba;

                            vec4 c = gl_ModelViewMatrix * vec4(gl_Vertex.xyz, 1);
                            center = c.xyz/c.w;
                            // Cone axis and taper are shoehorned into the texture coordinate
                            vec3 axis = gl_MultiTexCoord0.xyz;
                            float taper = gl_MultiTexCoord0.w;
                            tap_qec_qeb = cone_linear_coeffs1(center, radius, axis, taper, pos1.xyz/pos1.w);
                            qe_undot_half_a = cone_linear_coeffs2(center, radius, axis, taper, pos1.xyz/pos1.w);
                        }
                        """, GL_VERTEX_SHADER), 
                shaders.compileShader(glsl_fns_str, GL_FRAGMENT_SHADER),
                shaders.compileShader(
                        """
                        #version 120

                        varying vec4 pos1;
                        varying vec4 surface_color;
                        varying float radius;
                        varying vec3 center;
                        varying vec3 tap_qec_qeb;
                        varying vec3 qe_undot_half_a;
                        
                        // defined in imposter_fns120.glsl
                        vec2 cone_nonlinear_coeffs(vec3 pos, vec3 tap_qec_qeb, vec3 qe_undot_half_a);
                        vec3 cone_surface_from_coeffs(vec3 pos, vec3 tap_qec_qeb, vec2 a2_d);
                        vec3 light_rig(vec4 pos, vec3 normal, vec3 color);
                        float fragDepthFromEyeXyz(vec3 eyeXyz);
                        
                        void main() {
                            vec3 pos = pos1.xyz/pos1.w;
                            
                            // gl_FragColor = vec4(0.5*pos + 0.5*vec3(1,1,1), 1); return;
                            gl_FragColor = vec4(0.2, 0.2, 0.2, 1); return;
                            // TODO
                            
                            vec2 a2_d = cone_nonlinear_coeffs(pos, tap_qec_qeb, qe_undot_half_a);
                            if (a2_d.y <= 0)
                                discard; // Point does not intersect cone

                            gl_FragColor = vec4(0.2, 0.2, 0.2, 1); return;
                            
                            vec3 s = cone_surface_from_coeffs(pos, tap_qec_qeb, a2_d);
                            vec3 normal = 1.0 / radius * (s - center);
                            gl_FragColor = vec4(
                                light_rig(vec4(s, 1), normal, surface_color.rgb),
                                1);
                            gl_FragDepth = fragDepthFromEyeXyz(s);
                        }
                        """, GL_FRAGMENT_SHADER)
            )
            
            
        # The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
        def ReSizeGLScene(self, Width, Height):
            if Height == 0:                        # Prevent A Divide By Zero If The Window Is Too Small 
                Height = 1
        
            glViewport(0, 0, Width, Height)        # Reset The Current Viewport And Perspective Transformation
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)
            glMatrixMode(GL_MODELVIEW)
        
        # The main drawing function. 
        def DrawGLScene(self):
            
            glEnable( GL_LIGHTING ) 
            glEnable(GL_LIGHT1)
            glDisable(GL_LIGHT0)
            
            # Clear The Screen And The Depth Buffer
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            glLoadIdentity()                    # Reset The View 
            glTranslatef(0.0,0.0,-6.0);             # MoveInto The Screen
            glRotatef(self.yrot, 0.0, 1.0, 0.0);             # Rotate The Pyramid On It's Y Axis
            
            # Leftmost sphere is shaded using the fixed function pipeline
            glTranslatef(-1.6,0.0,0);             # Move Left
            # drawTriangle()
            glColor3f(0.8, 0.5, 0.2)
            shaders.glUseProgram(0)
            glutSolidSphere(1.0, 20, 20)
            shaders.glUseProgram(0)

            # Middle sphere is an imposter            
            glTranslatef( 1.6,0.0,0);
                         # Move Right
            glColor3f(0.2, 0.5, 0.8)
            self.renderSphereImposterImmediate(Sphere( [0, -0.2, 0], 1.1) )

            glColor3f(0.1, 0.7, 0.1)
            self.renderSphereImposterImmediate(Sphere( [-0.5, -1.2, 0], 0.8) )

            sph1 = Sphere([0, 1.1, 0], 1.0)
            sph2 = Sphere([1.2, 1.5, 0], 0.2)
            self.renderSphereImposterImmediate(sph1)
            self.renderSphereImposterImmediate(sph2)
            cone = ConeSegment(sph1, sph2)
            self.renderConeImposterImmediate(cone)

            # Right sphere is a standard mesh, shaded with GLSL
            glTranslatef( 1.6, 0.0, 0);             # Move Right
            glColor3f(0.2, 0.8, 0.5)
            # TODO - use as imposter
            shaders.glUseProgram(self.light_rig_shader)
            glColor3f(0.8, 0.5, 0.2)
            glutSolidSphere(1.0, 20, 20)
            # drawTriangle()
            shaders.glUseProgram(0)
            
            #  since this is double buffered, swap the buffers to display what just got drawn. 
            glutSwapBuffers()
            self.yrot += 1.00
            # print self.yrot
        
        def renderConeImposterImmediate(self, cone):
            shaders.glUseProgram(self.cone_shader)
            cone.generateBoundingGeometryImmediate()
        
        def renderSphereImposterImmediate(self, sphere):
            shaders.glUseProgram(self.sphere_shader)
            sphere.generateBoundingGeometryImmediate()
        
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
            
            # glutInitContextVersion(3, 1);
            # glutInitContextProfile(GLUT_CORE_PROFILE)
            
            # get a 640 x 480 window 
            glutInitWindowSize(640, 480)
            
            # the window starts at the upper left corner of the screen 
            glutInitWindowPosition(0, 0)
            
            # Okay, like the C version we retain the window id to use when closing, but for those of you new
            # to Python (like myself), remember this assignment would make the variable local and not global
            # if it weren't for the global declaration at the start of main.
            self.window = glutCreateWindow("SWC imposter demo")
        
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
    

