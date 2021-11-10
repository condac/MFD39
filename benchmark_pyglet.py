import math
import pyglet
import numpy as np
from pyglet.gl import *

import json
import socket
import time

import math
from math import sin, cos, sqrt, atan2, radians
import numpy as np
import keyboard
import argparse

#glEnable(GL_TEXTURE_2D)         # enable textures
#glShadeModel(GL_SMOOTH)         # smooth shading of polygons

radie = 45

ballsize = 10.0
balldepth = 122.0

localPort = 34556

heading = 0.0
tilt = 0.0
rota = 0.0
aoa = 0.0
speedbrake = 1.0


speed = 0
machspeed = 0.0
altitude = 0
fuel = 1.0
fuel0 = 0.0
fuel1 = 0.0
fuel2 = 0.0
fuel3 = 0.0
totalFuel = 1182.0*2
rawFuel = 1.0
gload = 1.0

gearratio = 0.0
geardown = True

connection = False

full = False
# main loop

#platform = pyglet.window.get_platform()
#display = platform.get_default_display()
display = pyglet.canvas.get_display()
screens = display.get_screens()
if (len(screens) >1):
  screen = screens[1]
  full = True
else:
  screen = screens[0]


config = pyglet.gl.Config(sample_buffers=1, samples=1, depth_size=24, double_buffer=True)
#window = pyglet.window.Window(config=config, resizable=True, width = 1024, height=768, screen=screen, fullscreen=full)
window = pyglet.window.Window(config=config, resizable=True,  screen=screen, fullscreen=full)
glEnable(GL_LINE_SMOOTH)
glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
glEnable(GL_BLEND)                                  # transparency
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # transparency
glEnable(GL_DEPTH_TEST)

#glClearColor(0.0, 0.0, 0.0, 0.0)

#glClearDepth(0.0)

#glDepthFunc(GL_LEQUAL)
#glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)   # make stuff look nice
#pyglet.graphics.glEnable(pyglet.graphics.GL_DEPTH_TEST)
#glDepthFunc(GL_LESS)

fps_display = pyglet.window.FPSDisplay(window=window)


def update(banan):
    return
def draw_sphere():
    global heading, radie, tilt, rota
    global ballsize

    pan = 4.0
    glLoadIdentity();
    roll =   np.deg2rad(rota)
    tiltrad = np.deg2rad(tilt)
    #gluLookAt (math.cos(tiltrad)*radie, 0.0, math.sin(tiltrad)*radie+pan, 0.0, 0.0, pan,0.0 , math.sin(roll), math.cos(roll));

    gluLookAt (0.0, radie, pan, 0.0, 0.0, pan,0.0 , 0.0, 1.0);
    glRotatef(rota, 0.0, 1.0, 0.0)
    glRotatef(-tilt+5, 1.0, 0.0, 0.0)
    glRotatef(-heading+179, 0.0, 0.0, 1.0)

    setColor(colorGreenLight)
    glEnable(texture.target)        # typically target is GL_TEXTURE_2D
    glBindTexture(texture.target, texture.id)

    q = gluNewQuadric()
    gluQuadricOrientation(q,GLU_OUTSIDE)
    gluQuadricDrawStyle(q,GLU_FILL)
    gluQuadricTexture(q, GL_TRUE)

    gluSphere(q,ballsize,50,50)

    glDisable(texture.target)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glTranslatef(100.0, 0.0, 0.0)


def setColor(color):
    (r,g,b,a) = color
    glColor4f(r, g, b, a)


def set3d():
    #glClearDepth(0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
             # enable depth testing

    # reset modelview matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    #aspectRatio = window.height / window.width
    #1.0 * width / height
    #gluPerspective(45, aspectRatio, 0.1, 100)
    gluPerspective(40, 1.0 * window.width / window.height, 1, balldepth)


    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #glTranslatef(0,0,-40)


def set2d():

    # store the projection matrix to restore later
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()

    # load orthographic projection matrix
    glLoadIdentity()
    glOrtho(0, float(window.width),0, float(window.height), 0, 10)

    # reset modelview
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #glClear(GL_COLOR_BUFFER_BIT)
def unSet2d():

    # load back the projection matrix saved before
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()


@window.event
def on_draw():
    window.clear()
    set3d()
    #draw_sphere()
    set2d()

    glColor4f(1.0,1.0,1.0,1.0)
    fps_display.draw()

    unSet2d()
    
@window.event
def on_resize(width, height):
        print ('on resize')
        if height == 0:
            height = 1
        glViewport(0, 0, width, height) # specify viewport

        # load perspective projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.0 * width / height, 1, balldepth)

        #glLoadIdentity()

# every 1/10 th get the next frame
#pyglet.clock.schedule(update_frame, 1/100.0)
pyglet.clock.schedule_interval(update, 1/120.0)
pyglet.app.run()
