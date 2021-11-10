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
frames = 0
t0 = time.time()
w = 1024
h = 768

def square():
    glBegin(GL_QUADS)
    glVertex2f(100+frames, 100+frames)
    glVertex2f(200, 100)
    glVertex2f(200, 200)
    glVertex2f(100, 200)
    glEnd()

def iterate():
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()
    
def update(banan):
    return

@window.event
def on_draw():
    global t0, frames
    #window.clear()

    #glColor4f(1.0,1.0,1.0,1.0)
    #fps_display.draw()
    
    
        
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    glColor3f(1.0, 0.0, 3.0)
    square()
    #glutSwapBuffers()
    frames += 1
    t = time.time()
    if t-t0 >=5.0:
        sec = t -t0
        fps = frames / sec
        print(f"fps {fps}")
        t0 = t
        frames = 0


@window.event
def on_resize(width, height):
        print ('on resize')
        if height == 0:
            height = 1
        glViewport(0, 0, width, height) # specify viewport

        # load perspective projection matrix
        #glMatrixMode(GL_PROJECTION)
        #glLoadIdentity()
        #gluPerspective(45, 1.0 * width / height, 1, balldepth)

        #glLoadIdentity()

# every 1/10 th get the next frame
#pyglet.clock.schedule(update_frame, 1/100.0)
pyglet.clock.schedule_interval(update, 1/120.0)
pyglet.app.run()
