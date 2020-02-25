import math
import pyglet
import os
from pyglet.gl import *
from pathlib import Path
from stat import *

def PathToDict(path):
    st = os.stat(path)
    result = {}
    #result['stat'] = st
    result['full_path'] = path
    if S_ISDIR(st.st_mode):
        result['type'] = 'd'
        result['items'] = {
            name : PathToDict(path+os.sep+name)
            for name in os.listdir(path)}
    else:
        result['type'] = 'f'
    return result

def setColor(color):
    (r,g,b,a) = color
    glColor4f(r, g, b, a)

def pie_circle(x, y, radius, percent):

    iterations = int(2*radius*math.pi /4)
    iterations = 128
    if (percent <0.0) :
        percent = 0.0
    if (percent >1.0) :
        percent = 1.0
    percent = 1.0 - percent

    per = int( (iterations*percent) )
    s = sin(2*math.pi / iterations)
    c = cos(2*math.pi / iterations)

    dx, dy = radius, 0

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(iterations+1 - per):
        glVertex2f(x-dx, y+dy)
        dx, dy = (dx*c - dy*s), (dy*c + dx*s)
    glEnd()

def circle(x, y, radius):

    iterations = int(2*radius*math.pi)
    iterations = 128

    s = sin(2*math.pi / iterations)
    c = cos(2*math.pi / iterations)

    dx, dy = radius, 0

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(iterations+1):
        glVertex2f(x-dx, y+dy)
        dx, dy = (dx*c - dy*s), (dy*c + dx*s)
    glEnd()

def circle_line(x, y, radius,width):
    glLineWidth(width)
    glBegin(GL_LINE_LOOP);
    segments = 64
    for i in range(segments):

        theta = 2.0 * math.pi * i / segments

        cx = radius * math.cos(theta)
        cy = radius * math.sin(theta)

        glVertex2f(x + cx, y + cy)

    glEnd();

def line(x1, y1, x2, y2, w):

    glLineWidth(w)
    glBegin(GL_LINES)


    glVertex3f(float(x1),float(y1),0.0)
    glVertex3f(float(x2),float(y2),0.0)
    glEnd()

def arc(x, y, radius,width, startangle, endangle):
    glLineWidth(width)
    glBegin(GL_LINE_STRIP);
    segments = 64
    starttheta = startangle * 1.0
    for i in range(segments):

        theta = endangle * i / segments

        cx = radius * math.cos(starttheta+theta)
        cy = radius * math.sin(starttheta+theta)

        glVertex2f(x + cx, y + cy)

    glEnd();

def rect(x, y, dx, dy):
    pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', [x, y, x+dx, y, x+dx, y+dy, x, y+dy]))

def jas(x, y, size):
    pyglet.graphics.draw(9, pyglet.gl.GL_POLYGON, ('v2f', [x, y,
                                                        x-size*0.5, y,
                                                        x-size*0.1, y+size*0.7,
                                                        x-size*0.25, y+size*0.7,
                                                        x, y+size*1.0,
                                                        x+size*0.25, y+size*0.7,
                                                        x+size*0.1, y+size*0.7,
                                                        x+size*0.5, y,
                                                        x, y]))
