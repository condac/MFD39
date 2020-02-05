#!/usr/bin/python3


import pygame
from pygame.locals import *

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

with open("settings.json") as settings_file:
    settings = json.load(settings_file)

pygame.init()

screenwidth = 480
screenheight = 320
localPort = 34556

def xscale(x):

    refscale = 1000
    f = screenheight/refscale
    x2 = int(x*f)
    return x2
class MFD():
    def __init__(self):

        self.fontButtonText = pygame.font.SysFont("dejavusans", xscale(33))
        self.fontAltText = pygame.font.SysFont("dejavusans", xscale(33))

        self.font20 = pygame.font.SysFont("dejavusans", 22)
        self.font20_off_x = -2
        self.font8 = pygame.font.SysFont("dejavusans", 11)
        self.fontUnit = pygame.font.SysFont("dejavusans", 22)
        self.fontVar = pygame.font.SysFont("dejavusans", 20)
        self.fontSimVar = pygame.font.SysFont("arial", 40, bold=True)

        self.backgroundColor = (0,0,0)
        self.paperColor = (255,255,255)
        self.paperColorLines = (128,128,128)
        self.paperColorTime = (100,100,100)
        self.rulerColor = (0,0,0)
        self.honeyBlue = (0,0,159)
        self.statusTextColor = (191, 191, 191)
        self.titleTextColor = (191, 191, 191)

        self.colorGreen10 = (0,int(10/10*255),0)
        self.colorGreen8 = (0,int(8/10*255),0)
        self.colorGreen6 = (0,int(6/10*255),0)
        self.colorGreen4 = (0,int(4/10*255),0)
        self.colorGreen2 = (0,int(2/10*255),0)
        self.colorGreen1 = (0,int(1/10*255),0)

        self.w = int(screenwidth)
        self.h = int(screenheight)

        self.src = imageio.imread('arrow.png')

    def createGlobe(self, heading, tilt, rotate):
        size=xscale(650)

        frame = 1
        frames = 40
        # Image pixel co-ordinates
        px=np.arange(-1.0,1.0,2.0/size)+1.0/size
        py=np.arange(-1.0,1.0,2.0/size)+1.0/size
        hx,hy=np.meshgrid(px,py)

        # Compute z of sphere hit position, if pixel's ray hits
        r2=hx*hx+hy*hy
        hit=(r2<=1.0)
        hz=np.where(
            hit,
            -np.sqrt(1.0-np.where(hit,r2,0.0)),
            np.NaN
            )

        # Some spin and tilt to make things interesting
        #spin=2.0*np.pi*(frame+0.5)/frames
        spin= -np.pi/2 - np.radians(heading)
        cs=math.cos(spin)
        ss=math.sin(spin)
        ms=np.array([[cs,0.0,ss],[0.0,1.0,0.0],[-ss,0.0,cs]])

        #tilt=0.125*np.pi*math.sin(2.0*spin)
        tilt = np.radians(tilt)
        ct=math.cos(tilt)
        st=math.sin(tilt)
        mt=np.array([[1.0,0.0,0.0],[0.0,ct,st],[0.0,-st,ct]])

        # Rotate the hit points
        xyz=np.dstack([hx,hy,hz])
        xyz=np.tensordot(xyz,mt,axes=([2],[1]))
        xyz=np.tensordot(xyz,ms,axes=([2],[1]))
        x=xyz[:,:,0]
        y=xyz[:,:,1]
        z=xyz[:,:,2]

        # Compute map position of hit
        latitude =np.where(hit,(0.5+np.arcsin(y)/np.pi)*self.src.shape[0],0.0)
        longitude=np.where(hit,(1.0+np.arctan2(z,x)/np.pi)*0.5*self.src.shape[1],0.0)
        latlong=np.array([latitude,longitude])
        #latlong=np.array([longitude,latitude])

        # Resample, and zap non-hit pixels
        dst=np.zeros((size,size,3))
        for channel in [0,1,2]:
            dst[:,:,channel]=np.where(
                hit,
                scipy.ndimage.interpolation.map_coordinates(
                    self.src[:,:,channel],
                    latlong,
                    order=1
                    ),
                0.0
                )

        #imageio.imsave('f.png',dst)
        return dst
    def drawAline(self,sb,x,y,r1,r2,angle, w=1):
        a = -np.radians(angle)
        x1 = int( x + (sin(a)*r1) )
        y1 = int( y + (cos(a)*r1) )
        x2 = int( x + (sin(a)*r2) )
        y2 = int( y + (cos(a)*r2) )
        pygame.draw.line(sb, self.colorGreen10,(x1 , y1),(x2, y2), w)

    def drawAtext(self,sb,x,y,r1,text,angle, w=1):
        a = -np.radians(angle)
        x1 = int( x + (sin(a)*r1) )
        y1 = int( y + (cos(a)*r1) )


        cpuText = self.fontAltText.render(str(text), 0, self.colorGreen10)
        cpuTextPos = (int(x1-cpuText.get_rect().width/2), int(y1-cpuText.get_rect().height/2) )
        sb.blit(cpuText,cpuTextPos)

    def drawFlightDirector(self,sb, x, y):
        wingspan = xscale(120/2)
        body = xscale(45/2)

        pygame.draw.circle(sb, self.colorGreen10, (x, y), body, xscale(10))
        pygame.draw.line(sb, self.colorGreen10,(x+body , y),(x+wingspan, y), xscale(10))
        pygame.draw.line(sb, self.colorGreen10,(x-body , y),(x-wingspan, y), xscale(10))
        pygame.draw.line(sb, self.colorGreen10,(x , y+body),(x, y+wingspan), xscale(10))

    def createSpeedo(self,sb):
        size = xscale(350/2)
        size2 = xscale(128/2)
        x = xscale(285)
        y = xscale(230)
        speed = self.speed
        maxSpeed = 900

        #Yttre cirkeln
        pygame.draw.circle(sb, self.colorGreen10, (x, y), size, 1)
        #inre cirkeln
        pygame.draw.circle(sb, self.colorGreen10, (x, y), size2, 1)

        #gradering
        for i in range(10):
            l = xscale(15)
            a = i/10*360
            self.drawAline(sb, x, y, size, size-l, a, w=1)

        for i in range(10):
            l = xscale(30)
            a = i/10*360
            self.drawAtext(sb, x, y, size-l, str(i), a, w=1)

        sa = speed/maxSpeed
        sa = sa * 360
        self.drawAline(sb, x, y, size, size2, sa, w=xscale(10))

    def createAltitude(self,sb):
        size = xscale(350/2)
        size2 = xscale(220/2)
        x = xscale(1020)
        y = xscale(230)
        speed = self.altitude
        maxSpeed = 1000

        #Yttre cirkeln
        pygame.draw.circle(sb, self.colorGreen10, (x, y), size, 1)
        #inre cirkeln
        pygame.draw.circle(sb, self.colorGreen10, (x, y), size2, 1)

        #gardering
        for i in range(20):
            l = xscale(15)
            a = i/20*360
            self.drawAline(sb, x, y, size, size-l, a, w=1)

        for i in range(10):
            l = xscale(35)
            a = i/10*360
            self.drawAtext(sb, x, y, size-l, str(i), a, w=1)

        sa = speed/maxSpeed
        sa = sa * 360
        self.drawAline(sb, x, y, size, 0, sa, w=xscale(10))
        speed = self.altitude/10
        sa = speed/maxSpeed
        sa = sa * 360
        self.drawAline(sb, x, y, size2, 0, sa, w=xscale(20))

    def drawPressureString(self,sb):
        textstring = "1027.5 hPa"
        Text = self.fontButtonText.render(str(textstring), 0, self.colorGreen10)
        TextPos = (int(xscale(550)), int(xscale(90)) )
        sb.blit(Text,TextPos)

    def drawButtonText(self,sb):
        textstring = "OVK"
        Text = self.fontButtonText.render(str(textstring), 0, self.colorGreen10)
        TextPos = (int(xscale(200)), int(xscale(915)) )
        sb.blit(Text,TextPos)


        textstring = "LAST"
        Text = self.fontButtonText.render(str(textstring), 0, self.colorGreen10)
        TextPos = (int(xscale(735)), int(xscale(915)) )
        sb.blit(Text,TextPos)


        textstring = "DATA"
        Text = self.fontButtonText.render(str(textstring), 0, self.colorGreen10)
        TextPos = (int(xscale(890)), int(xscale(915)) )
        sb.blit(Text,TextPos)


    def drawPageDefault(self,sb):
        sb.fill(self.backgroundColor)
        #sb.blit(sb,(-1,0))


        #Globe


        dst = self.createGlobe(self.heading, self.tilt, self.rotate)
        dst = np.swapaxes(dst, 0, 1)

        surf = pygame.surfarray.make_surface(dst)
        #pygame.transform.flip(surf, True, True)
        surf = pygame.transform.rotate(surf, self.rotate)
        sw = surf.get_width()
        sh = surf.get_height()
        sb.blit(surf,(int(xscale(660) - sw/2), int(xscale(620) - sh/2) ))

        self.drawFlightDirector(sb, xscale(660), xscale(620))

        # hastighetsmätare

        self.createSpeedo(sb)

        self.createAltitude(sb)

        self.drawPressureString(sb)

        self.drawButtonText(sb)


        textstring = str(self.heading) +" "+str(self.tilt)+" "+str(self.rotate)
        cpuText = self.fontButtonText.render(str(textstring), 0, self.colorGreen10)
        cpuTextPos = (int(xscale(500)), int(xscale(950)) )
        sb.blit(cpuText,cpuTextPos)



    # define a main function
    def main(self):
    # load and set the logo
        logo = pygame.image.load("programicon.jpg")
        pygame.display.set_icon(logo)
        pygame.display.set_caption(settings["title"])

        # create a surface on screen that has the size of X x Y
        dflags = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE
        drawsize = (self.w, self.h)
        screen = pygame.display.set_mode(drawsize,dflags)
        # Create a screen buffer that we draw everything in and allow the screen buffer to be resized
        #sb = screen.copy()
        sb = pygame.Surface(drawsize, 0, 24).convert()
        videoinfo = pygame.display.Info() # we use this to see if we can do smooth scaling
        print(videoinfo)



        # define all objects we draw on the surface
        r = pygame.rect.Rect((0, 200, 20, 20))
        t = pygame.rect.Rect((200, 0, 20, 20))
        upperbar = pygame.rect.Rect((0, 0, self.w, 20))

        # clock for update speed
        clock = pygame.time.Clock()
        # Display some text
        #print(pygame.font.get_fonts())

        textstring = os.getloadavg()
        cpuText = self.font8.render(str(textstring[0]), 0, (255, 255, 255))
        cpuTextPos = (self.w*0.5875+65 -cpuText.get_rect().width,10 )


        #Upper left text
        textTitle = self.font20.render(settings["title"],0,self.titleTextColor)
        textTitlepos = (0,self.font20_off_x)

        #Upper middle text
        textTitleMiddle = self.font20.render(settings["titleDesc"],0,self.titleTextColor)
        twidth = textTitleMiddle.get_rect()
        textTitleMiddlepos = (self.w*0.5875-twidth.width,self.font20_off_x)



        # define a variable to control the main loop
        running = True
        paperTime = 0
        timeline = 0
        fullscreen = False
        oldStatus = 0
        oldIC = ""
        simtime = 0.0
        control = 0
        old_time = pygame.time.get_ticks()
        waited = 0

        self.heading = 0.0
        self.tilt = 0.0
        self.rotate = 0.0
        self.speed = 0.0
        self.altitude = 0.0

        #quickfix for start in fullscreen
        fullscreen = False
        if fullscreen:
            # Display in Fullscreen mode
            pygame.display.quit()
            pygame.display.init()
            screen = pygame.display.set_mode((0, 0), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN)
            infoObject = pygame.display.Info()
            drawsize = (infoObject.current_w, infoObject.current_h)
            pygame.display.set_icon(logo)
            pygame.display.set_caption(settings["title"])
            pygame.mouse.set_visible(False)
        else:
            # Display in window mode
            pygame.display.quit()
            pygame.display.init()
            drawsize = (self.w,self.h)
            screen = pygame.display.set_mode(drawsize,dflags)
            pygame.display.set_icon(logo)
            pygame.display.set_caption(settings["title"])
            pygame.mouse.set_visible(True)
        # end quickfix

        # main loop
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('', localPort))
        self.s.setblocking(0)


        while running:
            pygame.event.pump()
            moredata = True
            while moredata:
                try:
                    message, address = self.s.recvfrom(4098)
                    stringdata = message.decode('utf-8', "ignore").split("}")[0]
                    #print(stringdata)
                    if "A1=" in stringdata:
                        a1 = stringdata.split("A1=")
                        a1 = a1[1].replace(";","")

                        self.tilt = float(a1)
                    if "A2=" in stringdata:
                        a1 = stringdata.split("A2=")
                        a1 = a1[1].replace(";","")
                        #print(a1)
                        self.heading = float(a1)
                    if "A3=" in stringdata:
                        a1 = stringdata.split("A3=")
                        a1 = a1[1].replace(";","")
                        #print(a1)
                        self.rotate = float(a1)
                    if "A4=" in stringdata:
                        a1 = stringdata.split("A4=")
                        a1 = a1[1].replace(";","")
                        #print(a1)
                        self.speed = float(a1)
                    if "A5=" in stringdata:
                        a1 = stringdata.split("A5=")
                        a1 = a1[1].replace(";","")
                        #print(a1)
                        self.altitude = float(a1)
                except socket.error:
                    moredata = False


            # event handling, gets all event from the eventqueue
            for event in pygame.event.get():
                #print(event)
                # only do something if the event if of type QUIT
                if event.type == pygame.QUIT:
                    # change the value to False, to exit the main loop
                    running = False
                if event.type == VIDEORESIZE:
                    drawsize = event.dict['size']
                    screen = pygame.display.set_mode(drawsize, dflags)
                if event.type == pygame.KEYDOWN and event.key == 49:
                    print("saveicbutton")

                if event.type == pygame.KEYDOWN and event.key == 50:
                    print("loadicbutton")

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if fullscreen:
                        fullscreen = False
                        # Display in window mode
                        pygame.display.quit()
                        pygame.display.init()
                        drawsize = (self.w,self.h)
                        screen = pygame.display.set_mode(drawsize,dflags)
                        pygame.display.set_icon(logo)
                        pygame.display.set_caption(settings["title"])
                        pygame.mouse.set_visible(True)
                    else:
                        fullscreen = True
                        # Display in Fullscreen mode
                        pygame.display.quit()
                        pygame.display.init()
                        screen = pygame.display.set_mode((0, 0), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN)
                        infoObject = pygame.display.Info()
                        drawsize = (infoObject.current_w, infoObject.current_h)
                        pygame.display.set_icon(logo)
                        pygame.display.set_caption(settings["title"])
                        pygame.mouse.set_visible(False)

            #########################
            ## MAIN LOOP
            new_time = pygame.time.get_ticks()

            self.drawPageDefault(sb)


            if videoinfo.bitsize >23:
                screen.blit(pygame.transform.smoothscale(sb, drawsize), (0, 0))
            else:
                screen.blit(pygame.transform.scale(sb, drawsize), (0, 0))


            pygame.display.flip()

            waited = new_time - old_time
            old_time = pygame.time.get_ticks()
            looptime = old_time - new_time
            #print(looptime)
            clock.tick(60)
            #time.sleep(0.02)
                #pygame.time.wait(0)
                #pygame.time.wait(1)


        pygame.quit()
        quit()
app = MFD()
# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    app.main()
