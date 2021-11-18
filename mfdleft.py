import math
import pyglet
import numpy as np
from pyglet.gl import *

#import os
import json
#import random
import socket
#import sys
#from pprint import pprint
#from PIL import Image
import time
import threading

#import imageio
import math
from math import sin, cos, sqrt, atan2, radians
import numpy as np
#import scipy
#import scipy.misc
#import scipy.ndimage.interpolation
import keyboard
import argparse

# Create the parser
my_parser = argparse.ArgumentParser(description='MFD39')


# Add the arguments
my_parser.add_argument('-f', action='store_true', help="Fullscreen")
# Execute the parse_args() method
args = my_parser.parse_args()

fullscreen = args.f

#glEnable(GL_TEXTURE_2D)         # enable textures
#glShadeModel(GL_SMOOTH)         # smooth shading of polygons

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
running = True

full = False
# main loop
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', localPort))
s.setblocking(0)
#platform = pyglet.window.get_platform()
#display = platform.get_default_display()
display = pyglet.canvas.get_display()
screens = display.get_screens()
if (len(screens) >1):
  screen = screens[1]
  full = True
else:
  screen = screens[0]

if fullscreen:
    screen = screens[0]
    full = True

config = pyglet.gl.Config( depth_size=24, double_buffer=True)
#window = pyglet.window.Window(config=config, resizable=True, width = 1024, height=768, screen=screen, fullscreen=full)
window = pyglet.window.Window(config=config, resizable=True,  screen=screen, fullscreen=full)
#glEnable(GL_LINE_SMOOTH)
#glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
#glEnable(GL_BLEND)                                  # transparency
#glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # transparency
glEnable(GL_DEPTH_TEST)

colorGreenMedium = (0.0/255.0, 200.0/255.0, 0.0/255.0, 255.0)
colorGreenLight = (0.0/255.0, 255.0/255.0, 0.0/255.0, 255.0)
colorGreenDark = (0.0/255.0, 83.0/255.0, 0.0/255.0, 255.0)
colorGreenIntense = (210.0/255.0, 255.0/255.0, 60.0/255.0, 255.0)
colorGreenSky = (94.0/255.0, 153.0/255.0, 35.0/255.0, 255.0)

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


batchText = pyglet.graphics.Batch()

def createLabelsBatch():
    global batchLabels, batchText
    batchText = pyglet.graphics.Batch()
    batchLabels = []
    label = pyglet.text.Label(str("s"), font_name='Arial', font_size=aiscale(32),color=(0,255,0,255), x=-10, y=0, anchor_x='center', anchor_y='center', group=None, batch=batchText)
    batchLabels.append(label)
    label = pyglet.text.Label(str("a"), font_name='Arial', font_size=aiscale(32),color=(0,255,0,255), x=-10, y=0, anchor_x='center', anchor_y='center', group=None, batch=batchText)
    batchLabels.append(label)
    
    # speed dial text
    size = afscale(350/2)
    size2 = afscale(128/2)
    x = xfscale(-360)
    y = yfscale(1000-230)
    for i in range(10):
        r1 = size-afscale(30)
        a = i/10*math.pi*2


        x1 =  x - (sin(a)*r1)
        y1 =  y - (cos(a)*r1)

        #speedlabels[i].text = str(i)
        #speedlabels[i].x = x1
        #speedlabels[i].y = y1
        #speedlabels[i].draw()
        label = pyglet.text.Label(str(i), font_name='Arial', font_size=aiscale(32),color=(0,255,0,255), x=x1, y=y1, anchor_x='center', anchor_y='center', group=None, batch=batchText)
        batchLabels.append(label)
    
    # altitude dial text
    
    size = afscale(350/2)
    size2 = afscale(220/2)
    x = xfscale(360)
    y = yfscale(1000-230)
    for i in range(10):
        r1 = size-afscale(30)
        a = i/10*math.pi*2

        x1 =  x - (sin(a)*r1)
        y1 =  y - (cos(a)*r1)

        # altlabels[i].text = str(i)
        # altlabels[i].x = x1
        # altlabels[i].y = y1
        # altlabels[i].draw() 
        label = pyglet.text.Label(str(i), font_name='Arial', font_size=aiscale(32),color=(0,255,0,255), x=x1, y=y1, anchor_x='center', anchor_y='center', group=None, batch=batchText)
        batchLabels.append(label)   
    
    
createLabelsBatch()

def createLabels():
    global speedlabel, smalllabel, speedlabels, altlabels, fuellabel
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
localPort = 34556
# function that increments to the next
# point along a circle
frame = 0




radie = 45

ballsize = 10.0
balldepth = 122.0

def parseNetData(stin, stringdata, old):

    if stin in stringdata:
        a1 = stringdata.split(stin)
        a1 = a1[1].replace(";","")
        connection = True
        return float(a1)
    return old


def readNetwork():
    global tilt, heading, rota, speed, altitude, fuel, gload, gearratio, rawFuel, totalFuel, connection
    global machspeed, aoa, speedbrake
    global fuel0, fuel1, fuel2, fuel3
    while running:
        moredata = True
        while moredata:
            try:
                message, address = s.recvfrom(4098)
                stringdata = message.decode('utf-8', "ignore").split("}")[0]
                #print(stringdata)
                speedbrake = parseNetData("A14=", stringdata, speedbrake)


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

                if "F0=" in stringdata:
                    a1 = stringdata.split("F0=")
                    a1 = a1[1].replace(";","")
                    #print(a1)
                    fuel0 = float(a1)
                if "F1=" in stringdata:
                    a1 = stringdata.split("F1=")
                    a1 = a1[1].replace(";","")
                    #print(a1)
                    fuel1 = float(a1)
                if "F2=" in stringdata:
                    a1 = stringdata.split("F2=")
                    a1 = a1[1].replace(";","")
                    #print(a1)
                    fuel2 = float(a1)
                if "F3=" in stringdata:
                    a1 = stringdata.split("F3=")
                    a1 = a1[1].replace(";","")
                    #print(a1)
                    fuel3 = float(a1)

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
                if "A12=" in stringdata:
                    a1 = stringdata.split("A12=")
                    a1 = a1[1].replace(";","")
                    #print(a1)
                    try:
                        machspeed = float(a1)
                    except:
                        print(".")
                if "A13=" in stringdata:
                    a1 = stringdata.split("A13=")
                    a1 = a1[1].replace(";","")
                    #print(a1)
                    aoa = float(a1)
            except socket.error:
                moredata = False
                
def update_frame(x, y):
    global gearratio, geardown, connection

    if (connection == False):
        fakevalues()
    #readNetwork()

    if (gearratio >=0.9):
        geardown = True
    else:
        geardown = False



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

    gluSphere(q,ballsize,20,20)

    glDisable(texture.target)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glTranslatef(100.0, 0.0, 0.0)

def fakevalues():
    global speed, machspeed
    speed = speed +1
    if speed > 1000:
        speed = 900
    global altitude
    altitude = altitude +1
    if altitude > 50000:
        altitude = 900
    machspeed = speed*2/1000



def drawAtext(x,y,r1,text,angle, w=1):
    global speedlabel
    a = -np.radians(angle)
    x1 = int( x + (sin(a)*r1) )
    y1 = int( y + (cos(a)*r1) )

    speedlabel.text = str(text)
    speedlabel.x = x1
    speedlabel.y = y1
    speedlabel.draw()

def draw_speed():

    global speed, speedlabels, machspeed
    maxspeed = 1000
    size = afscale(350/2)
    size2 = afscale(128/2)
    x = xfscale(-360)
    y = yfscale(1000-230)

    per = speed/maxspeed
    visare = per *math.pi*2
    #glColor4f(0.0, 1.0, 0.0, 1.0)
    setColor(colorGreenMedium)
    #glTranslatef(0.0, 0.0 , -0.2 )

    if (machspeed > 0.5) :
        textS = "M{:0.2f}".format(machspeed)
        #speedlabel.text = "M{:0.2f}".format(machspeed)
    else:
        textS = str(int(speed) )
        #speedlabel.text = str(int(speed) )
    #speedlabel.text = textS
    batchLabels[0].text = textS
    
    batchLabels[0].x = x
    batchLabels[0].y = y
    glDisable(GL_DEPTH_TEST)
    #speedlabel.draw()

    #glTranslatef(0.0, 0.0 , 0.2 )
    #Setting Matrix Mode
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #moving object left and right
    glTranslatef(x, y , -0.0 ) #x,y,z,

    #line(-math.sin(visare)*size2, -math.cos(visare)*size2, -math.sin(visare)*size, -math.cos(visare)*size, xfscale(10), (0.0,1.0,0.0,1.0) )
    #rotating object

    glRotatef(90.0, 0.0, 0.0, 1.0) #by 10 degrees around the x, y or z axis

    #glTranslatef(0.0, 0.0 , -0.1 )
    #colorGreenDark
    #glColor4f(0.0, 0.5, 0.0, 1.0)
    setColor(colorGreenDark)
    pie_circle(0,0,size, per)
    glColor4f(0.0, 0.0, 0.0, 1.0)
    circle(0,0,size2)
    #glColor4f(0.0, 1.0, 0.0, 1.0)
    setColor(colorGreenMedium)
    circle_line(0,0,size, afscale(5))
    circle_line(0,0,size2, afscale(5))
    #Undo rotations after we are done
    glRotatef(-90.0, 0.0, 0.0, 1.0)
    setColor(colorGreenIntense)
    line(-math.sin(visare)*size2, -math.cos(visare)*size2, -math.sin(visare)*size, -math.cos(visare)*size, afscale(10), colorGreenIntense )

    #gradering
    for i in range(10):
        l = afscale(15)
        a = i/10 *math.pi*2
        sizel = size -l
        #self.drawAline(sb, x, y, size, size-l, a, w=1)
        setColor(colorGreenMedium)
        line(-math.sin(a)*sizel, -math.cos(a)*sizel, -math.sin(a)*size, -math.cos(a)*size, afscale(5), colorGreenMedium )
    #gradering text



    glPopMatrix()
    glColor4f(0.0, 1.0, 0.0, 1.0)
    for i in range(10):
        r1 = size-afscale(30)
        a = i/10*math.pi*2


        x1 =  x - (sin(a)*r1)
        y1 =  y - (cos(a)*r1)

        #speedlabels[i].text = str(i)
        #speedlabels[i].x = x1
        #speedlabels[i].y = y1
        #speedlabels[i].draw()

    #speedlabel.draw()
    glEnable(GL_DEPTH_TEST)

def draw_altitude():

    global altitude, speedlabels
    maxspeed = 1000
    size = afscale(350/2)
    size2 = afscale(220/2)
    x = xfscale(360)
    y = yfscale(1000-230)

    per1 = altitude/1000
    visare1 = per1 *math.pi*2
    per2 = altitude/10000
    visare2 = per2 *math.pi*2
    per3 = altitude/100000
    visare3 = per3 *math.pi*2
    glColor4f(0.0, 1.0, 0.0, 1.0)
    #glTranslatef(0.0, 0.0 , -0.2 )

    batchLabels[1].text = str(int(altitude) )
    batchLabels[1].x = x+size
    batchLabels[1].y = y+size
    glDisable(GL_DEPTH_TEST)
    #speedlabel.draw()

    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glTranslatef(x, y , -0.0 ) #x,y,z,

    glRotatef(90.0, 0.0, 0.0, 1.0) #by 10 degrees around the x, y or z axis



    #glTranslatef(0.0, 0.0 , -0.1 )
    setColor(colorGreenDark)
    pie_circle(0,0,size, per3)

    setColor((0,0,0,255))
    circle(0,0,size2)
    #setColor(colorGreenMedium)
    #pie_circle(0,0,size2, per3)
    setColor(colorGreenMedium)
    circle_line(0,0,size, afscale(5))
    circle_line(0,0,size2, afscale(5))
    #Undo rotations after we are done
    glRotatef(-90.0, 0.0, 0.0, 1.0)
    line(-math.sin(visare1)*0.0, -math.cos(visare1)*0.0, -math.sin(visare1)*size, -math.cos(visare1)*size, afscale(10), colorGreenIntense )
    line(-math.sin(visare2)*0.0, -math.cos(visare2)*0.0, -math.sin(visare2)*size2, -math.cos(visare2)*size2, afscale(10), colorGreenIntense )

    #gradering
    for i in range(10):
        l = afscale(15)
        a = i/10 *math.pi*2
        sizel = size -l
        #self.drawAline(sb, x, y, size, size-l, a, w=1)
        line(-math.sin(a)*sizel, -math.cos(a)*sizel, -math.sin(a)*size, -math.cos(a)*size, afscale(5), colorGreenMedium )
    #gradering text

    glPopMatrix()
    glColor4f(0.0, 1.0, 0.0, 1.0)
    # for i in range(10):
    #     r1 = size-afscale(30)
    #     a = i/10*math.pi*2
    # 
    #     x1 =  x - (sin(a)*r1)
    #     y1 =  y - (cos(a)*r1)

        #altlabels[i].text = str(i)
        #altlabels[i].x = x1
        #altlabels[i].y = y1
        #altlabels[i].draw()
    #speedlabel.draw()
    glEnable(GL_DEPTH_TEST)

def drawFlightDirector(x, y):
    global geardown, speedbrake
    wingspan = afscale(100/2)
    body = afscale(35/2)
    linewidth = afscale(3)


    setColor(colorGreenIntense)

    #pygame.draw.circle(sb, self.colorGreen10, (x, y), body, xscale(10))
    circle_line(x,y,body, afscale(5))
    #pygame.draw.line(sb, self.colorGreen10,(x+body , y),(x+wingspan, y), xscale(10))
    line(x+body , y, x+wingspan, y, afscale(5), colorGreenIntense)
    #pygame.draw.line(sb, self.colorGreen10,(x-body , y),(x-wingspan, y), xscale(10))
    line(x-body , y, x-wingspan, y, afscale(5), colorGreenIntense)
    if (geardown):
        line(x, y-body, x, y-wingspan, afscale(5), colorGreenIntense)
    else:
        line(x, y+body, x, y+wingspan, afscale(5), colorGreenIntense)
    if (speedbrake >0):
        line(x, y, x+body, y+body, linewidth, colorGreenIntense)
        line(x, y, x-body, y+body, linewidth, colorGreenIntense)
    #pygame.draw.line(sb, self.colorGreen10,(x , y+body),(x, y+wingspan), xscale(10))

def drawFuelGauge(x,y):
    global fuel, fuellabel, totalFuel
    global fuel0, fuel1, fuel2, fuel3
    height = afscale(440)
    longline = afscale(20)
    shortline = afscale(10)

    fuelTotal = fuel0 + fuel1 + fuel2 + fuel3

    fuel = fuelTotal / totalFuel

    glDisable(GL_DEPTH_TEST)

    line(x , y, x, y+fuelscale(2.0, height), afscale(5), colorGreenMedium)

    #Line at 2.0
    line(x , y+fuelscale(2.0, height), x-longline, y+fuelscale(2.0, height), afscale(5), colorGreenMedium)

    #Line at 1.5 long
    line(x , y+fuelscale(1.5, height), x-longline, y+fuelscale(1.5, height), afscale(5), colorGreenMedium)

    #Line at 1.0
    line(x , y+fuelscale(1.0, height), x-longline, y+fuelscale(1.0, height), afscale(5), colorGreenMedium)

    #Line at 0.5
    line(x , y+fuelscale(0.5, height), x-longline, y+fuelscale(0.5, height), afscale(5), colorGreenMedium)

    #Small lines 0 to 1

    for i in range(10):
        iy = float(i/10.0)
        line(x , y+fuelscale(iy, height), x-shortline, y+fuelscale(iy, height), afscale(5), colorGreenMedium)

    #fuel bar
    if (fuel >2.0):
        fuel = 2.0
    #lien at top of fuelbar
    line(x , y+fuelscale(fuel, height), x+longline, y+fuelscale(fuel, height), afscale(5), colorGreenIntense)
    #bar
    line(x+longline/2 , y, x+longline/2, y+fuelscale(fuel, height), longline, colorGreenMedium)

    #texts
    fuellabel.text = str(2)
    fuellabel.x = x-longline
    fuellabel.y = y + fuelscale(2.0, height)
    fuellabel.draw()

    fuellabel.text = str(1)
    fuellabel.x = x-longline
    fuellabel.y = y + fuelscale(1.0, height)
    fuellabel.draw()

    fuellabel.text = str(".5")
    fuellabel.x = x-longline
    fuellabel.y = y + fuelscale(0.5, height)
    fuellabel.draw()

    fuellabel.text = str("B")
    fuellabel.x = x-longline
    fuellabel.y = y + (fuellabel.font_size+2)*3
    fuellabel.draw()

    fuellabel.text = str("R")
    fuellabel.x = x-longline
    fuellabel.y = y + (fuellabel.font_size+2)*2
    fuellabel.draw()

    fuellabel.text = str("Ä")
    fuellabel.x = x-longline
    fuellabel.y = y + (fuellabel.font_size+2)*1
    fuellabel.draw()
    glEnable(GL_DEPTH_TEST)


def drawGLoad(x,y):
    global gload, fuellabel
    height = afscale(380)
    longline = afscale(20)
    shortline = afscale(10)
    maxg = 9.0

    line(x , y, x, y+linescale(maxg, maxg, height), afscale(5), colorGreenMedium)

    #Line at 9.0
    line(x , y+linescale(9.0, maxg, height), x-longline, y+linescale(9.0, maxg, height), afscale(5), colorGreenMedium)


    #Small lines 0 to 9

    for i in range(int(maxg)):

        line(x , y+linescale(float(i), maxg, height), x-longline, y+linescale(float(i), maxg, height), afscale(5), colorGreenMedium)

    #G bar
    if (gload >10.0):
        gload = 10.0
    #lien at top of G bar
    line(x , y+linescale(gload, maxg, height), x+longline, y+linescale(gload, maxg, height), afscale(5), colorGreenIntense)
    #G bar
    line(x+longline/2 , y, x+longline/2, y+linescale(gload, maxg, height), longline, colorGreenMedium)

    #texts
    fuellabel.text = str(9)
    fuellabel.x = x-longline
    fuellabel.y = y + linescale(9, maxg, height)
    fuellabel.draw()

    fuellabel.text = str(6)
    fuellabel.x = x-longline
    fuellabel.y = y + linescale(6, maxg, height)
    fuellabel.draw()

    fuellabel.text = str(3)
    fuellabel.x = x-longline
    fuellabel.y = y + linescale(3, maxg, height)
    fuellabel.draw()

    fuellabel.text = str("G")
    fuellabel.x = x
    fuellabel.y = y + height+(fuellabel.font_size)
    fuellabel.draw()



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

    set3d()
    draw_sphere()
    set2d()

    draw_speed()
    draw_altitude()

    drawFuelGauge(xfscale(475), yfscale(128))
    drawGLoad(xfscale(-385), yfscale(128))
    drawFlightDirector(window.width/2, yfscale(380))
    
    batchText.draw()

    glColor4f(1.0,0,0,1.0)
    fps_display.draw()

    unSet2d()
def pressKey(str2):
    print(str2)

def clearKeys():
    global key01, key02, key03, key04, key11, key12, key13, key14, key15, key16
    key01 = False
    key02 = False
    key03 = False
    key04 = False

    key11 = False
    key12 = False
    key13 = False
    key14 = False
    key15 = False
    key16 = False

def keyPressCallback(event):
    global key01, key02, key03, key04, key11, key12, key13, key14, key15, key16
    if (event.name == "1"):
        key01 = True
    if (event.name == "2"):
        key02 = True
    if (event.name == "3"):
        key03 = True
    if (event.name == "4"):
        key04 = True

    if (event.name == "5"):
        key11 = True
    if (event.name == "6"):
        key12 = True
    if (event.name == "7"):
        key13 = True
    if (event.name == "8"):
        key14 = True
    if (event.name == "9"):
        key15 = True
    if (event.name == "0"):
        key16 = True


    print(event)
@window.event
def on_key_press(s,m):

    global heading, tilt, radie, rota, geardown, totalFuel, rawFuel

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
    if s == pyglet.window.key.G:
        if (geardown):
            geardown = False
        else:
            geardown = True
    if s == pyglet.window.key.F5:
        totalFuel = rawFuel
        print(rawFuel)
    if s == pyglet.window.key.F12:
        window.set_fullscreen(not window.fullscreen)

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
        createLabelsBatch()
        #glLoadIdentity()
clearKeys()
x = threading.Thread(target=readNetwork)
print("startar nätverks tråd")
x.start()
    
keyboard.on_press(keyPressCallback, suppress=False)
# every 1/10 th get the next frame
pyglet.clock.schedule(update_frame, 1/10.0)
pyglet.app.run()
running = False
