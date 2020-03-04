import math
import pyglet
import os
from pyglet.gl import *
from pathlib import Path
from stat import *
from math import sin, cos, sqrt, atan2, radians
import numpy as np

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

def getDistanceGPS(lat1,lon1, lat2, lon2):


    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    #print("Result:", distance)
    return distance

def getHeadingGPS(lat1,lon1,lat2,lon2):
    dLon = lon2 - lon1;
    y = math.sin(dLon) * math.cos(lat2);
    x = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon);
    brng = np.rad2deg(math.atan2(y, x));
    #if brng < 0:
    #    brng+= 360
    return brng

def getHeadingGPS2(lat1,lon1,lat2,lon2):
    teta1 = np.deg2rad(lat1)
    teta2 = np.deg2rad(lat2)
    delta1 = np.deg2rad(lat2-lat1)
    delta2 = np.deg2rad(lon2-lon1)


    y = sin(delta2) * cos(teta2)
    x = cos(teta1)*sin(teta2) - sin(teta1)*cos(teta2)*cos(delta2)
    brng = atan2(y,x)
    brng = np.rad2deg(brng)
    brng =  brng + 360
    if brng > 360:
        brng-= 360
    return brng


def setColor(color):
    (r,g,b,a) = color
    glColor4f(r, g, b, a)
    return (int(r*255), int(g*255), int(b*255), int(a*255))

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

def circle_line(x, y, radius,width, segments = 64):
    glLineWidth(width)
    glBegin(GL_LINE_LOOP);
    
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
    glBegin(GL_QUADS)                      # Draw A Quad
    glVertex2f( x   , y+dy)              # Top Left
    glVertex2f( x+dx, y+dy)              # Top Right
    glVertex2f( x+dx, y)              # Bottom Right
    glVertex2f( x   , y)              # Bottom Left
    glEnd()

def rect_line(x, y, dx, dy, w):
    glLineWidth(w)
    glBegin(GL_LINE_LOOP)
    #glBegin(GL_QUADS)                      # Draw A Quad
    glVertex2f( x   , y+dy)              # Top Left
    glVertex2f( x+dx, y+dy)              # Top Right
    glVertex2f( x+dx, y)              # Bottom Right
    glVertex2f( x   , y)              # Bottom Left
    glEnd()

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
