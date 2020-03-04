import math
import pyglet
import numpy as np
from pyglet.gl import *
from ctypes import byref, sizeof, POINTER

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

from sharedDrawFunctions import *

#glEnable(GL_TEXTURE_2D)         # enable textures
#glShadeModel(GL_SMOOTH)         # smooth shading of polygons

localPort = 34557

heading = 0.0
tilt = 0.0
rota = 0.0

currentTileX = 0
currentTileY = 0
currentTileZ = 1

speed = 0
altitude = 0
fuel = 1.0
totalFuel = 1000.0
rawFuel = 1.0
gload = 1.0

gearratio = 0.0
geardown = True

radarx = 640
radary = 480
zoomlevel = 9

lon = 16.9158608
lat = 58.7806412

targets = []
t = {}
t["lat"] = 58.7806412
t["lon"] = 16.9158608
targets.append(t)


# Create the framebuffer (rendering target).
buf = gl.GLuint(0)
glGenFramebuffers(1, byref(buf))
glBindFramebuffer(GL_FRAMEBUFFER, buf)

# Create the texture (internal pixel data for the framebuffer).
tex = gl.GLuint(0)
glGenTextures(1, byref(tex))
glBindTexture(GL_TEXTURE_2D, tex)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, radarx, radary, 0, GL_RGBA, GL_FLOAT, None)

# Bind the texture to the framebuffer.
#glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0)

# Something may have gone wrong during the process, depending on the
# capabilities of the GPU.
res = glCheckFramebufferStatus(GL_FRAMEBUFFER)
if res != GL_FRAMEBUFFER_COMPLETE:
  raise RuntimeError('Framebuffer not completed')

full = False
# main loop
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', localPort))
s.setblocking(0)
#platform = pyglet.window.get_platform()
#display = platform.get_default_display()
display = pyglet.canvas.get_display()
screens = display.get_screens()
if (len(screens) >2):
  screen = screens[2]
  full = True
else:
  screen = screens[0]

config = pyglet.gl.Config(sample_buffers=1, samples=1, depth_size=24)
window = pyglet.window.Window(config=config, resizable=True, width = 1024, height=768, screen=screen, fullscreen=full)
glEnable(GL_LINE_SMOOTH)
glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
glEnable(GL_BLEND)                                  # transparency
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # transparency
glEnable(GL_DEPTH_TEST)


colorGreenMedium = (0.0/255.0, 200.0/255.0, 0.0/255.0, 255.0)
colorGreenLight = (0.0/255.0, 255.0/255.0, 0.0/255.0, 255.0)
colorGreenDark = (0.0/255.0, 83.0/255.0, 0.0/255.0, 255.0)
colorGreenIntense = (210.0/255.0, 255.0/255.0, 60.0/255.0, 255.0)
colorGreenSky = (94.0/255.0, 153.0/255.0, 35.0/255.0, 255.0)

colorRBG = (1.0, 1.0, 1.0, 1.0)
colorBlack = (0.0, 0.0, 0.0, 1.0)

colorGreen1 = (0.0/255.0, 0.1, 0.0/255.0, 255.0)
colorGreen2 = (0.0/255.0, 0.2, 0.0/255.0, 255.0)
colorGreen3 = (0.0/255.0, 0.3, 0.0/255.0, 255.0)
colorGreen4 = (0.0/255.0, 0.4, 0.0/255.0, 255.0)
colorGreen5 = (0.0/255.0, 0.5, 0.0/255.0, 255.0)
colorGreen6 = (0.0/255.0, 0.6, 0.0/255.0, 255.0)
colorGreen7 = (0.0/255.0, 0.7, 0.0/255.0, 255.0)
colorGreen8 = (0.0/255.0, 0.8, 0.0/255.0, 255.0)
colorGreen9 = (0.0/255.0, 0.9, 0.0/255.0, 255.0)
colorGreen10 = (0.0/255.0, 1.0, 0.0/255.0, 255.0)

def xfscale(x):

    refscale = 1000
    f = window.height/refscale
    x2 = x*f
    x2 = x2 + window.width/2
    return x2

def xiscale(x):

    return int(xfscale(x))

def yfscale(y):

    refscale = 1000
    f = window.height/refscale
    y2 = y*f
    return y2
def yiscale(y):

    return int(yfscale(y))

def afscale(a):

    refscale = 1000
    f = window.height/refscale
    a2 = a*f
    return a2
def aiscale(a):

    return int(afscale(a))


def fuelscale(percent, height):
    #percent is value 0-2.0 for 200 percent fuel with external tanks

    scale = (2.0**0.5)
    out = (percent**0.5)*height/scale
    return out

def linescale(value, maxValue, height):
    #percent is value 0-2.0 for 200 percent fuel with external tanks

    percent = value / maxValue
    out = (percent)*height
    return out


def createLabels():
    global speedlabel, smalllabel, speedlabels, altlabels, fuellabel, altlabel
    speedlabel = pyglet.text.Label(str("speed"),
                          font_name='Arial',
                          font_size=aiscale(32),
                          color=(0,255,0,255),
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center',
                          group=None)
    smalllabel = pyglet.text.Label(str("speed"),
                          font_name='Arial',
                          font_size=aiscale(16),
                          color=(0,255,0,255),
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center',
                          group=None)
    fuellabel = pyglet.text.Label(str("speed"),
                        font_name='Monospace',
                        font_size=aiscale(25),
                        color=(0,255,0,255),
                        x=window.width//2, y=window.height//2,
                        anchor_x='right', anchor_y='center',
                        group=None)
    speedlabels = []
    for i in range(10):
        new = pyglet.text.Label(str(i),
                              font_name='Arial',
                              font_size=aiscale(30),
                              color=(0,255,0,255),
                              x=window.width//2, y=window.height//2,
                              anchor_x='center', anchor_y='center',
                              group=None)
        speedlabels.append(new)
    altlabels = []
    for i in range(10):
        new = pyglet.text.Label(str(i),
                              font_name='Arial',
                              font_size=aiscale(30),
                              color=(0,255,0,255),
                              x=window.width//2, y=window.height//2,
                              anchor_x='center', anchor_y='center',
                              group=None)
        altlabels.append(new)
    altlabel = pyglet.text.Label(str("speed"),
                        font_name='Consolas',
                        font_size=aiscale(15),
                        color=(0,200,0,255),
                        x=window.width//2, y=window.height//2,
                        anchor_x='left', anchor_y='center',
                        group=None)
createLabels()
#glClearColor(0.0, 0.0, 0.0, 0.0)

#glClearDepth(0.0)

#glDepthFunc(GL_LEQUAL)
#glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)   # make stuff look nice
#pyglet.graphics.glEnable(pyglet.graphics.GL_DEPTH_TEST)
#glDepthFunc(GL_LESS)

fps_display = pyglet.window.FPSDisplay(window=window)

pic = pyglet.image.load('512.png')
texture = pic.get_texture()

screenwidth = 480
screenheight = window.height

# function that increments to the next
# point along a circle
frame = 0




radie = 30

ballsize = 10.0
balldepth = 22.0



def readNetwork():
    global tilt, heading, rota, speed, altitude, fuel, gload, gearratio
    global rawFuel, totalFuel, connection, lon, lat, groundspeed
    global targets
    moredata = True
    while moredata:
        try:
            message, address = s.recvfrom(4098)
            stringdata = message.decode('utf-8', "ignore").split("}")[0]
            #print(stringdata)
            if "A1=" in stringdata:
                a1 = stringdata.split("A1=")
                a1 = a1[1].replace(";","")

                tilt = float(a1)
                connection = True

            if "A2=" in stringdata:
                a1 = stringdata.split("A2=")
                a1 = a1[1].replace(";","")
                #print(a1)
                heading = float(a1)
            if "A3=" in stringdata:
                a1 = stringdata.split("A3=")
                a1 = a1[1].replace(";","")
                #print(a1)
                rota = float(a1)
            if "A4=" in stringdata:
                a1 = stringdata.split("A4=")
                a1 = a1[1].replace(";","")
                #print(a1)
                speed = float(a1)
            if "A5=" in stringdata:
                a1 = stringdata.split("A5=")
                a1 = a1[1].replace(";","")
                #print(a1)
                altitude = float(a1)
                connection = True
            if "A6=" in stringdata:
                a1 = stringdata.split("A6=")
                a1 = a1[1].replace(";","")
                #print(a1)
                rawFuel = float(a1)
                fuel = rawFuel / totalFuel
            if "A7=" in stringdata:
                a1 = stringdata.split("A7=")
                a1 = a1[1].replace(";","")
                #print(a1)
                gload = float(a1)
            if "A8=" in stringdata:
                a1 = stringdata.split("A8=")
                a1 = a1[1].replace(";","")
                #print(a1)
                gearratio = float(a1)
            if "A9=" in stringdata:
                a1 = stringdata.split("A9=")
                a1 = a1[1].replace(";","")
                #print(a1)
                lon = float(a1)
            if "A10=" in stringdata:
                a1 = stringdata.split("A10=")
                a1 = a1[1].replace(";","")
                #print(a1)
                lat = float(a1)
            if "A11=" in stringdata:
                a1 = stringdata.split("A11=")
                a1 = a1[1].replace(";","")
                #print(a1)
                groundspeed = float(a1)
            if "T01=" in stringdata:
                a1 = stringdata.split("T01=")
                a1 = a1[1].replace(";","")
                #print(a1)
                targets[0]["lat"] = float(a1)
            if "T02=" in stringdata:
                a1 = stringdata.split("T02=")
                a1 = a1[1].replace(";","")
                print(a1)
                targets[0]["lon"] = float(a1)
        except socket.error:
            moredata = False

def updateTile(lat_deg,lon_deg,zoom):
    global currentTileX, currentTileY, currentTileZ

    (xtile, ytile) = deg2num(lat_deg, lon_deg, zoom)
    if (xtile != currentTileX or ytile != currentTileY or zoom != currentTileZ) :

        print("change tile")
        loadingMap = False
        currentTileX = xtile
        currentTileY = ytile
        currentTileZ = zoom



def update_frame(x, y):
    global gearratio, geardown, lat, lon, zoomlevel

    fakevalues()
    readNetwork()
    updateTile(lat,lon,zoomlevel)

    if (gearratio >=0.9):
        geardown = True
    else:
        geardown = False


def fakevalues():
    global speed
    speed = speed +1
    if speed > 1000:
        speed = 900
    global altitude
    altitude = altitude +1
    if altitude > 50000:
        altitude = 900
def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def deg2numfloat(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = (lon_deg + 180.0) / 360.0 * n
    ytile = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
    return (xtile, ytile)

def whereInTile(lat_deg,lon_deg,zoom):
    tileSize = 256
    (xtile, ytile) = deg2num(lat_deg, lon_deg, zoom)
    (xtilef, ytilef) = deg2numfloat(lat_deg, lon_deg, zoom)

    ox = (tileSize * (xtilef - xtile))
    oy = tileSize - (tileSize * (ytilef - ytile))
    #print((ox,oy))
    return (ox,oy)

def whereInMap(lat_deg,lon_deg,zoom):
    global currentTileX, currentTileY
    tileSize = 256
    (ox1, oy1) = whereInTile(lat_deg,lon_deg,zoom)
    (xtile, ytile) = deg2num(lat_deg, lon_deg, zoom)
    ofx = (currentTileX - xtile) * tileSize
    ofy = (currentTileY - ytile) * tileSize
    (cx, cy) = whereInTile(lat,lon,zoom)

    ox = ox1 - cx - ofx
    oy = oy1 - cy + ofy

    #print((ox,oy))
    return (ox,oy)

def drawAtext(x,y,r1,text,angle, w=1):
    global speedlabel
    a = -np.radians(angle)
    x1 = int( x + (sin(a)*r1) )
    y1 = int( y + (cos(a)*r1) )

    speedlabel.text = str(text)
    speedlabel.x = x1
    speedlabel.y = y1
    speedlabel.draw()

def drawRadar(x, y):
    global heading
    fov = 90
    range = afscale(750)
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glTranslatef(x, y , -0.0 ) #x,y,z,

    glRotatef(-90+fov/2, 0.0, 0.0, 1.0) #by 10 degrees around the x, y or z axis


    setColor((0.0/255.0, 200.0/255.0, 0.0/255.0, 30/255.0))

    pie_circle(0,0,range, fov/360)
    drawTargets(x,y)

    glPopMatrix()
    return

def drawFlightDirector(x, y):
    global geardown
    wingspan = afscale(100/2)
    body = afscale(35/2)
    linewidth = afscale(3)


    setColor(colorGreenMedium)

    #pygame.draw.circle(sb, self.colorGreen10, (x, y), body, xscale(10))
    circle_line(x,y,body, linewidth)
    #pygame.draw.line(sb, self.colorGreen10,(x+body , y),(x+wingspan, y), xscale(10))
    line(x+body , y, x+wingspan, y, linewidth, colorGreenMedium)
    #pygame.draw.line(sb, self.colorGreen10,(x-body , y),(x-wingspan, y), xscale(10))
    line(x-body , y, x-wingspan, y, linewidth, colorGreenMedium)
    if (geardown):
        line(x, y-body, x, y-wingspan, linewidth, colorGreenMedium)
    else:
        line(x, y+body, x, y+wingspan, linewidth, colorGreenMedium)
    #pygame.draw.line(sb, self.colorGreen10,(x , y+body),(x, y+wingspan), xscale(10))


def drawFlightDirectorLines(x, y):
    global tilt, rota, altitude
    length = afscale(400)
    offset = afscale(75)
    linewidth = afscale(3)

    tiltoffset = afscale(-tilt*10.0)

    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #moving object left and right
    glTranslatef(x, y , -0.0 ) #x,y,z,

    #line(-math.sin(visare)*size2, -math.cos(visare)*size2, -math.sin(visare)*size, -math.cos(visare)*size, xfscale(10), (0.0,1.0,0.0,1.0) )
    #rotating object

    glRotatef(rota, 0.0, 0.0, 1.0) #by 10 degrees around the x, y or z axis

    line(offset , tiltoffset, length, tiltoffset, linewidth, colorGreenMedium)
    line(-offset , tiltoffset, -length, tiltoffset, linewidth, colorGreenMedium)
    altstr = ""
    if (altitude<1000):
        altstr = "{:03d}".format(int(altitude) )
    else:
        altstr = "{:.1f}".format(altitude/1000)
    altlabel.text = str(altstr)
    altlabel.x = offset*2
    altlabel.y = tiltoffset+altlabel.font_size*0.8
    altlabel.draw()
    glPopMatrix()

    return



def drawCompass(x, y, width):
    global heading
    ahead = heading /360.0 * math.pi*2


    linewidth = afscale(5)
    marklength = afscale(15)
    radius = width

    setColor(colorGreenMedium)
    arc(x, y-radius, radius,linewidth, (math.pi/2)- math.pi/6, math.pi/3)

    for i in range(36):
        ihead = i*10 /360.0 * math.pi*2
        #move one rotation for more simble angle compare when it loops from 0 to 360 deg
        if ((ihead > ahead-math.pi/6 and ihead < ahead+math.pi/6) or
            (ihead-math.pi*2 > ahead-math.pi/6 and ihead-math.pi*2 < ahead+math.pi/6) or
            (ihead+math.pi*2 > ahead-math.pi/6 and ihead+math.pi*2 < ahead+math.pi/6)):
            #it is visible draw it
            ihead = ihead +math.pi/2 - ahead
            line(x-math.cos(ihead)*radius, y-radius+math.sin(ihead)*radius, x-math.cos(ihead)*(radius+marklength), y-radius+math.sin(ihead)*(radius+marklength), afscale(5), colorGreenMedium )

            #text
            if (i % 2) == 0:
                if i < 10:
                    s = "0"+str(i)
                else:
                    s = str(i)
                speedlabels[1].text = s
                speedlabels[1].x = x-math.cos(ihead)*(radius+marklength*3)
                speedlabels[1].y = y-radius+math.sin(ihead)*(radius+marklength*3)
                speedlabels[1].draw()

    speedlabel.text = str(int(heading))
    speedlabel.x = x
    speedlabel.y = y-afscale(30)
    speedlabel.draw()

def drawTargets(x, y):
    global zoomlevel, lon, lat, targets
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #moving object left and right
    glTranslatef(x, y , -0.0 ) #x,y,z,

    glRotatef(heading, 0.0, 0.0, 1.0) #by 10 degrees around the x, y or z axis

    setColor((1.0,1.0,0.0,1.0))
    glPushMatrix()

    for xx in targets:
        (ox, oy) = whereInMap(xx["lat"],xx["lon"],zoomlevel)
        #circle_line(ox,oy,afscale(3), afscale(3))
        # draw romb
        glLineWidth(1.5)
        dy = afscale(8)
        dx = afscale(4)
        glBegin(GL_LINE_LOOP)

        glVertex2f( ox   , oy+dy)              # Top
        glVertex2f( ox+dx, oy)              #  Right
        glVertex2f( ox, oy-dy)              # Bottom
        glVertex2f( ox-dx   , oy)              #  Left
        glEnd()
        altlabel.text = "t1"
        altlabel.x = ox + altlabel.font_size/2
        altlabel.y = oy
        altlabel.draw()

    glPopMatrix()

    glPopMatrix()


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

def line(x1, y1, x2, y2, w, color):
    (r ,g,b,a)=color
    glColor4f(r,g,b,a)
    glLineWidth(w)
    glBegin(GL_LINES)


    glVertex3f(float(x1),float(y1),0.0)
    glVertex3f(float(x2),float(y2),0.0)
    glEnd()


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
    gluPerspective(45, 1.0 * window.width / window.height, 1, balldepth)


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

def drawRadarTexture():
    glBindFramebuffer(GL_FRAMEBUFFER, buf)
    glViewport(0,0,radarx,radary)

    setColor((0.0, 0.0, 0.0, 1.5/255.0))
    rect(0,0,1000,1000)

    #glClearColor(0.0,0.0,0.0,0.1)
    #glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    drawCompass(xfscale(0), yfscale(910), afscale(900))

    drawRadar(xfscale(0), yfscale(50))

    # Restore normal buffer
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glViewport(0,0,window.width,window.height)


@window.event
def on_draw():

    set3d()
    #draw_sphere()
    set2d()

    drawRadarTexture()


    glColor4f(1.0,0,0,1.0)
    #draw_speed()
    #draw_altitude()

    #drawFuelGauge(xfscale(475), yfscale(128))
    #drawGLoad(xfscale(-385), yfscale(128))


    glColor4f(1.0,0,0,1.0)
    fps_display.draw()


    drawFlightDirector(xfscale(0), yfscale(500))
    drawFlightDirectorLines(xfscale(0), yfscale(500))


    setColor((1.0, 1.0, 1.0, 1.0))
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex)

    glBegin(GL_QUADS);
    glTexCoord2i(0, 0)
    glVertex2i(0, 0)
    glTexCoord2i(1, 0)
    glVertex2i(window.width, 0)
    glTexCoord2i(1, 1)
    glVertex2i(window.width, window.height)
    glTexCoord2i(0, 1)
    glVertex2i(0, window.height)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    unSet2d()

@window.event
def on_key_press(s,m):

    global heading, tilt, radie, rota, geardown, totalFuel, rawFuel, lat, lon

    if s == pyglet.window.key.W:
        tilt -= 1.1
    if s == pyglet.window.key.S:
        tilt += 1.1
    if s == pyglet.window.key.A:
        heading += 1.1
        if (heading > 360.0):
            heading = heading - 360.0
    if s == pyglet.window.key.D:
        heading -= 1.1
        if (heading < 0.0):
            heading = heading + 360.0
    if s == pyglet.window.key.R:
        radie -= 1
    if s == pyglet.window.key.F:
        radie += 1
    if s == pyglet.window.key.Q:
        rota += -1
    if s == pyglet.window.key.E:
        rota += 1
    if s == pyglet.window.key.G:
        if (geardown):
            geardown = False
        else:
            geardown = True
    if s == pyglet.window.key.F5:
        totalFuel = rawFuel

    if s == pyglet.window.key.UP:
        lat += 0.1
    if s == pyglet.window.key.DOWN:
        lat -= 0.1
    if s == pyglet.window.key.LEFT:
        lon -= 0.1
    if s == pyglet.window.key.RIGHT:
        lon += 0.1

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
        createLabels()
        #glLoadIdentity()
# every 1/10 th get the next frame
pyglet.clock.schedule(update_frame, 1/10.0)
pyglet.app.run()
