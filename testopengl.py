import math
import pyglet
import numpy as np
from pyglet.gl import *

import os
import json
import random
import socket
import sys
from pprint import pprint
from PIL import Image
import time

import imageio
import math
from math import sin, cos, sqrt, atan2, radians
import numpy as np
import scipy
import scipy.misc
import scipy.ndimage.interpolation


#glEnable(GL_TEXTURE_2D)         # enable textures
#glShadeModel(GL_SMOOTH)         # smooth shading of polygons
glClearColor(0.0, 0.0, 0.0, 0.0)

glClearDepth(1.0)

glDepthFunc(GL_LEQUAL)
glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)   # make stuff look nice
pyglet.graphics.glEnable(pyglet.graphics.GL_DEPTH_TEST)
config = pyglet.gl.Config(sample_buffers=1, samples=4)
window = pyglet.window.Window(config=config, resizable=True)
fps_display = pyglet.window.FPSDisplay(window=window)
label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

src = imageio.imread('arrow.png')

pic = pyglet.image.load('512.png')
texture = pic.get_texture()


screenwidth = 480
screenheight = 320
localPort = 34556

def xscale(x):

    refscale = 1000
    f = screenheight/refscale
    x2 = int(x*f)
    return x2


# get all the points in a circle centered at 0.
def PointsInCircum(r, n=25, pi=3.14):
    return [(math.cos(2*pi/n*x)*r,math.sin(2*pi/n*x)*r) for x in range(0,n+1)]
pts = np.array(PointsInCircum(20))

# function that increments to the next
# point along a circle
frame = 0

heading = 0.0
tilt = 0.0
rota = 0.0

radie = 30

def update_frame(x, y):
    global frame
    global heading
    if frame == None or frame == pts.shape[0]-1:
        frame = 0
    else:
        frame += 1
    #heading = heading + 0.1

def draw_sphere():
    global heading, radie, tilt, rota
    glLoadIdentity();
    gluLookAt (radie, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0);

    glRotatef(heading, 0.0, 0.0, 1.0)
    glRotatef(tilt, 1.0, 0.0, 0.0)
    glRotatef(rota, 0.0, 1.0, 0.0)
    #gluLookAt(radie, radie, radie, 0.0, 0, 0, 0, 0, 1)
    glColor3f(1.0, 1.0, 1.0)
    glEnable(texture.target)        # typically target is GL_TEXTURE_2D
    glBindTexture(texture.target, texture.id)

    q = gluNewQuadric()
    gluQuadricOrientation(q,GLU_OUTSIDE)
    gluQuadricOrientation(q, GLU_INSIDE);
    gluQuadricDrawStyle(q,GLU_LINE)
    gluQuadricDrawStyle(q,GLU_FILL)
    gluQuadricTexture(q, GL_TRUE)

    #glTranslatef(0.0, 0.0, -50.0)

    gluSphere(q,10.0,50,50)

    glDisable(texture.target)




def set3d():
    glClearDepth(0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
             # enable depth testing
    glDepthFunc(GL_LESS  )
    # reset modelview matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    #aspectRatio = window.height / window.width
    #1.0 * width / height
    #gluPerspective(45, aspectRatio, 0.1, 100)
    gluPerspective(45, 1.0 * window.width / window.height, 1, 1000.0)


    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)
    #glTranslatef(0,0,-40)


def set2d():

    glDisable(GL_DEPTH_TEST)
    # store the projection matrix to restore later
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()

    # load orthographic projection matrix
    glLoadIdentity()
    glOrtho(0, float(window.width),0, float(window.height), 0, 1)
    far = 8192
    #glOrtho(-window.width / 2., window.width / 2., -window.height / 2., window.height / 2., 0, far)

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
    glClearColor (0.0, 0.0, 0.0, 0.0);
    glClear(GL_COLOR_BUFFER_BIT)
    glEnable(GL_BLEND)
    set3d()
    draw_sphere()
    set2d()


    glColor4f(1.0,0,0,1.0)
    fps_display.draw()
    label.draw()
    #banan = createGlobe(0.0,0.0,0.0)
    # clear the screen

    #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    #ball_image = pyglet.image.ImageData(100, 100, 'RGBA', banan, -100*3)
    #ball = pyglet.sprite.Sprite(ball_image, x=50, y=50)
    #ball.draw()
    #draw_sphere()
    # draw the next line
    # in the circle animation
    # circle centered at 100,100,0 = x,y,z
    glBegin(GL_LINES)
    glVertex3f(100,100,0)
    glVertex3f(pts[frame][1]+100,pts[frame][0]+100,0)
    glEnd()

    glColor4f(1.0,0,0,1.0)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable (GL_BLEND)
    glEnable (GL_LINE_SMOOTH);
    glHint (GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
    glLineWidth (3)
    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,('v2i', (10, 15, 300, 305)))

    unSet2d()

@window.event
def on_key_press(s,m):

    global heading, tilt, radie, rota

    if s == pyglet.window.key.W:
        tilt -= 1.1
    if s == pyglet.window.key.S:
        tilt += 1.1
    if s == pyglet.window.key.A:
        heading += 1.1
    if s == pyglet.window.key.D:
        heading -= 1.1
    if s == pyglet.window.key.R:
        radie -= 1
    if s == pyglet.window.key.F:
        radie += 1
    if s == pyglet.window.key.Q:
        rota += -1
    if s == pyglet.window.key.E:
        rota += 1


@window.event
def on_resize(width, height):
        print ('on resize')
        if height == 0:
            height = 1
        glViewport(0, 0, width, height) # specify viewport

        # load perspective projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.0 * width / height, 1, 1000.0)
        #glLoadIdentity()
# every 1/10 th get the next frame
pyglet.clock.schedule(update_frame, 1/10.0)
pyglet.app.run()
