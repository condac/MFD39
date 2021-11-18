import json
import math
import os.path
import urllib3
import socket
import pyglet
import keyboard
from pyglet.gl import *
from sharedDrawFunctions import *
import time
import argparse

import threading

# Create the parser
my_parser = argparse.ArgumentParser(description='MFD39')

# Add the arguments
my_parser.add_argument('-f', action='store_true', help="Fullscreen")
# Execute the parse_args() method
args = my_parser.parse_args()

fullscreen = args.f

zoomlevel = 9
zoomfactor = 1.5
gearratio = 0.0
geardown = True

#58.402261, 15.525880
# eskn
lon = 16.9158608
lat = 58.7806412

# malmen
#lon = 15.525880
#lat = 58.402261

heading = 80.0
tilt = 0.0
rota = 0.0
aoa = 0.0
speedbrake = 1.0


speed = 0.0
altitude = 0.0
groundspeed = 100.0

connection = False
running = True

currentTileX = 0
currentTileY = 0
currentTileZ = 7

EXTILES = 2 # extra tiles around center

currentPage = "MAP"
loadingMap = True

currentWaypoint = 0

tileimages = []
for i in range(1+EXTILES*2):
    tileimages.append([])
    for j in range(1+EXTILES*2):
        tileimages[i].append(0)
# main loop
localPort = 34558
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', localPort))
s.setblocking(0)

maps = {}
currentMap = 0

with open("maps.json") as maps_file:
    maps = json.load(maps_file)
with open("waypoints.json") as way_file:
    waypoints1 = json.load(way_file)
loadedwaypoints = waypoints1
#platform = pyglet.window.get_platform()
#display = platform.get_default_display()

full = False
display = pyglet.canvas.get_display()
screens = display.get_screens()
if (len(screens) >1):
  screen = screens[0]
  full = True
else:
  screen = screens[0]
if fullscreen:
    screen = screens[0]
    full = True

config = pyglet.gl.Config(sample_buffers=1, samples=1, depth_size=24, double_buffer=True)
#window = pyglet.window.Window(config=config, resizable=True, width = 768, height=1024, screen=screen, fullscreen=full)
window = pyglet.window.Window(config=config, resizable=True,  screen=screen, fullscreen=full)
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

mapColor = 3
mapColors = [colorGreen1, colorGreen2, colorGreen3, colorGreen4, colorGreen5, colorGreen6, colorGreen7, colorGreen8, colorGreen9, colorGreen10, colorRBG]
fps_display = pyglet.window.FPSDisplay(window=window)



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

def createLabels():
    global speedlabel, smalllabel, speedlabels, altlabels, buttonlabel,waylabel,checklabel, rightlabel, airportlabel, altlabel
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
    buttonlabel = pyglet.text.Label(str("speed"),
                        font_name='Monospace',
                        font_size=aiscale(25),
                        color=(0,255,0,255),
                        x=window.width//2, y=window.height//2,
                        anchor_x='center', anchor_y='center',
                        group=None)
    rightlabel = pyglet.text.Label(str("speed"),
                        font_name='Monospace',
                        font_size=aiscale(25),
                        color=(0,255,0,255),
                        x=window.width//2, y=window.height//2,
                        anchor_x='right', anchor_y='center',
                        group=None)
    waylabel = pyglet.text.Label(str("speed"),
                        font_name='Monospace',
                        font_size=aiscale(15),
                        color=(0,255,0,255),
                        x=window.width//2, y=window.height//2,
                        anchor_x='left', anchor_y='center',
                        group=None)
    checklabel = pyglet.text.Label(str("speed"),
                        font_name='Consolas',
                        font_size=aiscale(30),
                        color=(0,255,0,255),
                        x=window.width//2, y=window.height//2,
                        anchor_x='left', anchor_y='center',
                        group=None)
    airportlabel = pyglet.text.Label(str("speed"),
                        font_name='Consolas',
                        font_size=aiscale(16),
                        color=(0,0,0,255),
                        x=window.width//2, y=window.height//2,
                        anchor_x='left', anchor_y='center',
                        group=None)
    altlabel = pyglet.text.Label(str("speed"),
                        font_name='Consolas',
                        font_size=aiscale(15),
                        color=(0,200,0,255),
                        x=window.width//2, y=window.height//2,
                        anchor_x='left', anchor_y='center',
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

def parseNetData(stin, stringdata, old):

    if stin in stringdata:
        a1 = stringdata.split(stin)
        a1 = a1[1].replace(";","")
        connection = True
        return float(a1)
    return old

def readNetwork():
    global tilt, heading, rota, speed, altitude, fuel, gload, gearratio
    global rawFuel, totalFuel, connection, lon, lat, groundspeed, aoa, speedbrake
    
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
                if "A13=" in stringdata:
                    a1 = stringdata.split("A13=")
                    a1 = a1[1].replace(";","")
                    #print(a1)
                    aoa = float(a1)
            except socket.error:
                moredata = False
                time.sleep(0.01)
                
def update_frame(x, y):
    global gearratio, geardown, connection

    if (connection == False):
        fakevalues()
    #readNetwork()

    nextWaypoint()
    if (gearratio >=0.9):
        geardown = True
    else:
        geardown = False

def fakevalues():
    global lon, lat
    #lat = lat + 0.001
    #if lat > 60.0:
    #    lat = 58.0
    #lon = lon + 0.001
    #if lon > 19.0:
    #    lon = 17.0

    return

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

def getCurrentMapDir():
    return maps["maps"][currentMap]["dir"]

def getCurrentMapURL():
    return maps["maps"][currentMap]["url"]
def downloadTile(xtile, ytile, zoom):
    filename = "tiles" + os.path.sep + getCurrentMapDir() + os.path.sep + str(zoom) + os.path.sep + str(xtile) + os.path.sep + str(ytile) + ".png"
    getname = str(zoom) + "/" + str(xtile) + "/" + str(ytile) + ".png"
    url = getCurrentMapURL() + getname
    http = urllib3.PoolManager()
    print ("download: ", url)
    r = http.request('GET', url)
    print ("download status ", r.status)
    if (r.status == 200):
        f = open(filename,'wb')
        f.write(r.data)
        f.close()
        return True
    else:
        return False

def getTileImage(xtile, ytile, zoom):
    filename = "tiles" + "/" + getCurrentMapDir() + "/" + str(zoom) + "/" + str(xtile) + "/" + str(ytile) + ".png"
    directory = "tiles" + os.path.sep + getCurrentMapDir() + os.path.sep + str(zoom) + os.path.sep + str(xtile)


    if xtile < 0 or ytile < 0:
        return pyglet.resource.image("0.png")

    if os.path.isfile(filename):
        #print ("File exist")
        return pyglet.resource.image(filename)
    else:
        print ("Cache miss: " + filename)
        from pathlib import Path
        Path(directory).mkdir(parents=True, exist_ok=True)
        ok = downloadTile(xtile, ytile, zoom)
        if ok:
            pyglet.resource.reindex()
            return pyglet.resource.image(filename)
        else:
            return pyglet.resource.image("0.png")
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

airports = []
apindex = {}

def updateAirports():
    global currentTileX, currentTileY, zoomlevel
    global airports, apindex
    (latMax, lonMax) = num2deg(currentTileX+EXTILES+1, currentTileY-EXTILES, zoomlevel)
    (latMin, lonMin) = num2deg(currentTileX-EXTILES, currentTileY+EXTILES+1, zoomlevel)
    starttid = time.time()
    airports = []
    try:
        with open("airport_xpl11.csv") as file_in:
            firstline = True
            for line in file_in:
                sline = line.split(",")
                if (firstline):
                    firstline = False
                    apindex = {}
                    ii = 0
                    for index in sline:
                        index = index.replace("\n", "")
                        index = index.replace("\r", "")
                        apindex[index] = ii
                        #print("adding index:", index, ii)
                        ii = ii + 1
                else:

                    if (len(sline)>65):
                        #print(sline[0])
                        #64 lon
                        #65 lat
                        try:
                            if(float(sline[apindex["laty"]]) < latMax and float(sline[apindex["laty"]]) > latMin and
                                float(sline[apindex["lonx"]]) < lonMax and float(sline[apindex["lonx"]]) > lonMin):
                                if (float(sline[apindex["longest_runway_length"]]) > 400) :
                                    if (sline[apindex["longest_runway_surface"]] == "A" or sline[apindex["longest_runway_surface"]] == "C" ) :
                                        #print(sline[2], sline[64], sline[65], sline[apindex["longest_runway_surface"]])
                                        sline[65] = float(sline[65])
                                        sline[apindex["lonx"]] = float(sline[apindex["lonx"]])
                                        airports.append(sline)
                        except ValueError:
                            print("Not a float")



    except:
        print("error airport_")

    sluttid = time.time()
    print ("update airport time:" , sluttid - starttid)

def updateTile(lat_deg,lon_deg,zoom):
    global currentTileX, currentTileY, currentTileZ, tileimage, tileimages
    global loadingMap
    (xtile, ytile) = deg2num(lat_deg, lon_deg, zoom)
    if (xtile != currentTileX or ytile != currentTileY or zoom != currentTileZ) :
        if loadingMap == False:
            loadingMap = True

        else:
            print("change tile")
            loadingMap = False
            currentTileX = xtile
            currentTileY = ytile
            currentTileZ = zoom
            #tileimage = getTileImage(xtile, ytile, zoom)
            updateAirports()
            for x in range(1+EXTILES*2):
                for y in range(1+EXTILES*2):
                    tileimages[x][y] = getTileImage(xtile-EXTILES+x, ytile-EXTILES+y, zoom)


def drawFlightDirector(x, y):
    global geardown, aoa, speedbrake
    wingspan = afscale(100/2)
    body = afscale(35/2)
    linewidth = afscale(3)

    aoaoffset = afscale(-aoa*10.0)
    y = y + aoaoffset

    setColor(colorGreenMedium)

    #pygame.draw.circle(sb, self.colorGreen10, (x, y), body, xscale(10))
    circle_line(x,y,body, linewidth)
    #pygame.draw.line(sb, self.colorGreen10,(x+body , y),(x+wingspan, y), xscale(10))
    line(x+body , y, x+wingspan, y, linewidth)
    #pygame.draw.line(sb, self.colorGreen10,(x-body , y),(x-wingspan, y), xscale(10))
    line(x-body , y, x-wingspan, y, linewidth)
    if (geardown):
        line(x, y-body, x, y-wingspan, linewidth)
    else:
        line(x, y+body, x, y+wingspan, linewidth)
    #pygame.draw.line(sb, self.colorGreen10,(x , y+body),(x, y+wingspan), xscale(10))
    if (speedbrake >0):
        line(x, y, x+body, y+body, linewidth)
        line(x, y, x-body, y+body, linewidth)

def drawFlightDirectorLines(x, y):
    global tilt, rota, altitude
    length = afscale(400)
    offset = afscale(75)
    linewidth = afscale(2)

    tiltoffset = afscale(-tilt*10.0)

    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #moving object left and right
    glTranslatef(x, y , -0.0 ) #x,y,z,

    #line(-math.sin(visare)*size2, -math.cos(visare)*size2, -math.sin(visare)*size, -math.cos(visare)*size, xfscale(10), (0.0,1.0,0.0,1.0) )
    #rotating object

    glRotatef(rota, 0.0, 0.0, 1.0) #by 10 degrees around the x, y or z axis

    line(offset , tiltoffset, length, tiltoffset, linewidth)
    line(-offset , tiltoffset, -length, tiltoffset, linewidth)
    altstr = ""
    if (altitude<1000):
        altstr = "{:03d}".format(int(altitude) )
    else:
        altstr = "{:.1f}".format(altitude/1000)
    altlabel.text = str(altstr)
    altlabel.x = offset*2
    altlabel.y = tiltoffset+altlabel.font_size*0.8
    altlabel.draw()

    #draw elsevere also to avoid strange bugs
    altlabel.text = str("ba")
    altlabel.x = -10000
    altlabel.y = -10000
    altlabel.draw()

    glPopMatrix()

    return



def drawCompass(x, y, width):
    global heading
    ahead = heading /360.0 * math.pi*2

    linewidth = afscale(5)
    marklength = afscale(15)
    radius = width
    glDisable(GL_DEPTH_TEST)
    setColor(colorGreenLight)
    arc(x, y-radius, radius,linewidth, (math.pi/2)- math.pi/6, math.pi/3)

    for i in range(36):
        ihead = i*10 /360.0 * math.pi*2
        #move one rotation for more simble angle compare when it loops from 0 to 360 deg
        if ((ihead > ahead-math.pi/6 and ihead < ahead+math.pi/6) or
            (ihead-math.pi*2 > ahead-math.pi/6 and ihead-math.pi*2 < ahead+math.pi/6) or
            (ihead+math.pi*2 > ahead-math.pi/6 and ihead+math.pi*2 < ahead+math.pi/6)):
            #it is visible draw it
            ihead = ihead +math.pi/2 - ahead
            line(x-math.cos(ihead)*radius, y-radius+math.sin(ihead)*radius, x-math.cos(ihead)*(radius+marklength), y-radius+math.sin(ihead)*(radius+marklength), afscale(5) )

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

    #speedlabel.text = str(int(heading))
    #speedlabel.x = x
    #speedlabel.y = y-afscale(30)
    #speedlabel.draw()
    #glEnable(GL_DEPTH_TEST)

def drawMap(x, y):
    global tileimage, zoomlevel, lon, lat, zoomfactor
    #print("lon", lon , "lat", lat)
    updateTile(lat,lon,zoomlevel)
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #moving object left and right
    glTranslatef(x, y , -0.0 ) #x,y,z,

    glRotatef(heading, 0.0, 0.0, 1.0) #by 10 degrees around the x, y or z axis

    (ox, oy) = whereInTile(lat,lon,zoomlevel)
    #tileimage.blit(-ox, -oy)

    setColor(mapColors[mapColor])
    glPushMatrix()
    glScalef(zoomfactor, zoomfactor, 1)
    for xx in range(1+EXTILES*2):
        for yy in range(1+EXTILES*2):
            tileimages[xx][yy].blit(-ox + (255*(-EXTILES+xx)), -oy - (255*(-EXTILES+yy)))
    glPopMatrix()
    #setColor(colorGreenLight)
    #circle_line(0,0,afscale(10), afscale(3))
    setColor(colorGreenLight)
    #circle_line(0,0,afscale(3), afscale(3))
    glPopMatrix()

def drawWaypoints(x, y):
    global tileimage, zoomlevel, lon, lat, zoomfactor
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #moving object left and right
    glTranslatef(x, y , -0.0 ) #x,y,z,

    glRotatef(heading, 0.0, 0.0, 1.0) #by 10 degrees around the x, y or z axis

    setColor((1.0,1.0,0.0,1.0))
    glPushMatrix()
    glScalef(zoomfactor, zoomfactor, 1)
    for xx in loadedwaypoints["waypoints"]:
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
        waylabel.text = xx["text"]
        waylabel.x = ox + waylabel.font_size/2
        waylabel.y = oy
        waylabel.draw()
    setColor(colorGreenLight)
    glLineWidth(1)
    glBegin(GL_LINE_STRIP);
    for xx in loadedwaypoints["waypoints"]:
        (ox, oy) = whereInMap(xx["lat"],xx["lon"],zoomlevel)
        #circle_line(ox,oy,afscale(3), afscale(3))
        glVertex2f(ox, oy)

    glEnd();
    glPopMatrix()

    glPopMatrix()

def drawAirports(x, y):
    global airports, apindex, zoomlevel, zoomfactor
    if (zoomlevel > 6):
        glPushMatrix()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        #moving object left and right
        glTranslatef(x, y , -0.0 ) #x,y,z,

        glRotatef(heading, 0.0, 0.0, 1.0) #by 10 degrees around the x, y or z axis

        setColor((0.0,0.0,0.0,1.0))
        glPushMatrix()
        glScalef(zoomfactor, zoomfactor, 1)
        for xx in airports:
            (ox, oy) = whereInMap(xx[apindex["laty"]],xx[apindex["lonx"]],zoomlevel)
            circle_line(ox,oy,afscale(16), 2, 8)
            if (zoomlevel > 7):
                airportlabel.text = xx[apindex["ident"]]
                airportlabel.x = ox + afscale(16)
                airportlabel.y = oy
                airportlabel.draw()
            if (zoomlevel > 8):

                angle = np.deg2rad(float(xx[apindex["longest_runway_heading"]])+90)
                cx = afscale(16) * math.cos(angle)
                cy = afscale(16) * math.sin(angle)
                line(ox-cx, oy-cy, ox+cx, oy+cy, 2)


        glPopMatrix()

        glPopMatrix()




def nextWaypoint(manual = False):
    global lat, lon, currentWaypoint
    cur = loadedwaypoints["waypoints"][currentWaypoint]
    distance = getDistanceGPS(cur["lat"], cur["lon"], lat,lon)
    if (distance < 2.0 or manual == True):
        currentWaypoint = currentWaypoint +1
        if currentWaypoint >= len(loadedwaypoints["waypoints"]) :
            currentWaypoint = 0

def drawWaypointsInfo():
    global lat, lon, currentWaypoint, checklabel, groundspeed
    lineoff = 0
    for xx in loadedwaypoints["waypoints"]:
        if (currentWaypoint == lineoff):
            checklabel.color = (255,255,0,255)
            checklabel.text = ">"
            checklabel.x = afscale(40)
            checklabel.y = yfscale(900) - checklabel.font_size*1.5*lineoff
            checklabel.draw()
        else:
            checklabel.color = (0,200,0,255)
        checklabel.text = " " + xx["text"]
        checklabel.x = afscale(40)
        checklabel.y = yfscale(900) - checklabel.font_size*1.5*lineoff
        checklabel.draw()
        lineoff = lineoff + 1

    # Riktning och avstånd till nästa
    cur = loadedwaypoints["waypoints"][currentWaypoint]
    distance = getDistanceGPS(cur["lat"], cur["lon"], lat,lon)
    #head = getHeadingGPS( lat,lon, cur["lat"], cur["lon"])
    head2 = getHeadingGPS2( lat,lon, cur["lat"], cur["lon"])
    eta = 0
    if (groundspeed != 0.0):
        etatime = (distance*1000/groundspeed)/60
        if (etatime < 1000):
            eta = str(int(etatime)) + "m"
        else:
            eta = "N/A"
    else:
        eta = "N/A"

    rightlabel.color = (0,255,0,255)
    rightlabel.text = cur["text"]
    rightlabel.x = window.width-rightlabel.font_size
    rightlabel.y = yfscale(10) + rightlabel.font_size*1.5*4
    rightlabel.draw()

    rightlabel.color = (0,255,0,255)
    rightlabel.text = "H"+str(int(head2))
    rightlabel.x = window.width-rightlabel.font_size
    rightlabel.y = yfscale(10) + rightlabel.font_size*1.5*3
    rightlabel.draw()

    rightlabel.color = (0,255,0,255)
    rightlabel.text = str(int(distance)) + "km"
    rightlabel.x = window.width-rightlabel.font_size
    rightlabel.y = yfscale(10) + rightlabel.font_size*1.5*2
    rightlabel.draw()

    rightlabel.color = (0,255,0,255)
    rightlabel.text = "ETA " + eta
    rightlabel.x = window.width-rightlabel.font_size
    rightlabel.y = yfscale(10) + rightlabel.font_size*1.5*1
    rightlabel.draw()


def vertText(x, y, textstr):
    center = (buttonlabel.font_size+4)*(len(textstr)-1)
    center = center / 2
    for i in range(len(textstr)):
        buttonlabel.text = str(textstr[i])
        buttonlabel.x = x
        buttonlabel.y = y + center - (buttonlabel.font_size+4)*i
        buttonlabel.draw()
def horiText(x, y, textstr):
    center = (buttonlabel.font_size+2)
    center = center / 2
    buttonlabel.text = str(textstr)
    buttonlabel.x = x
    buttonlabel.y = y + center
    buttonlabel.draw()

def linebreakText(x, y, textstr, label):

    ii = 0
    text = textstr.split("\n")
    for line in text:


        label.text = str(line)
        label.x = x
        label.y = y - (label.font_size*1.4)*ii
        label.draw()
        ii = ii + 1



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
    gluPerspective(45, 1.0 * window.width / window.height, 1, 100)


    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #glTranslatef(0,0,-40)


def set2d():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # store the projection matrix to restore later
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()

    # load orthographic projection matrix
    glLoadIdentity()
    glOrtho(0, float(window.width),0, float(window.height), 0, 10)

    # reset modelview
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    #glClear(GL_COLOR_BUFFER_BIT)
def unSet2d():
    glEnable(GL_DEPTH_TEST)
    # load back the projection matrix saved before
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()


def loadPage():
    global key01, key02, key03, key04, key11, key12, key13, key14, key15, key16, currentPage
    if currentPage == "MAP":
        pageMap()
    elif currentPage == "MENU":
        pageMenu()
    elif currentPage == "CHECKLIST":
        pageChecklist()
    elif currentPage == "WAYPOINT":
        pageWaypoint()
    else:
        pageMenu()

waypointfiles = PathToDict("waypoints"+os.sep)

waypoints = []
selectedList = 0

for key, item in waypointfiles["items"].items():
    if item["type"] == 'f':
        if key.endswith(".json"):
            list = {}
            f = open(item['full_path'])
            list["name"] = key.replace(".json", "")
            list["text"] = f.read()
            waypoints.append(list)
selectedWList = 0
def pageWaypoint():
    global key01, key02, key03, key04, key11, key12, key13, key14, key15, key16
    global currentPage, selectedWList, scrollCheck, loadedwaypoints
    if key11:
        currentPage = "MAP"
        clearKeys()
    if key16:
        currentPage = "MENU"
        clearKeys()
    if key01:
        selectedWList = selectedWList - 1
        scrollCheck = 0
        if selectedWList < 0:
            selectedWList = 0
        clearKeys()
    if key02:
        selectedWList = selectedWList + 1
        scrollCheck = 0
        if selectedWList >= len(waypoints):
            selectedWList = len(waypoints)-1
        clearKeys()
    if key03:
        scrollCheck = scrollCheck - 1
        if scrollCheck < 0:
            scrollCheck = 0
        clearKeys()
    if key04:
        scrollCheck = scrollCheck + 1
        clearKeys()
    #set3d()
    set2d()

    setColor(colorGreenLight)
    loadedwaypoints = json.loads(waypoints[selectedWList]["text"])

    linebreakText(xfscale(-200), yfscale(900), waypoints[selectedWList]["name"], checklabel)
    linebreakText(xfscale(-340), yfscale(800)+scrollCheck*afscale(100), waypoints[selectedWList]["text"], checklabel)

    #drawFlightDirector(xfscale(0), yfscale(500))
    #drawFlightDirectorLines(xfscale(0), yfscale(500))

    #BUTTONS
    setColor(colorBlack)
    rect(0, 0, afscale(25),yfscale(1000))
    rect(0, yfscale(1000-25), xfscale(1000),yfscale(25))
    setColor(colorGreenLight)
    vertText(afscale(25/2), yfscale(1000)/7*6, "KART")
    vertText(afscale(25/2), yfscale(1000)/7*5, "")
    vertText(afscale(25/2), yfscale(1000)/7*4, "")

    vertText(afscale(25/2), yfscale(1000)/7*3, "CHKL")
    vertText(afscale(25/2), yfscale(1000)/7*2, "")
    vertText(afscale(25/2), yfscale(1000)/7*1, "MENY") #key16

    horiText(xfscale(-250), yfscale(1000-25), "FÖRG") #key01
    horiText(xfscale(-100), yfscale(1000-25), "NÄSTA") #key02
    horiText(xfscale(100), yfscale(1000-25), "UPP") #key03
    horiText(xfscale(200), yfscale(1000-25), "NER") #key04

    unSet2d()


showWaypoint = True
subPageMap = "KSTR"
def pageMap():
    global key01, key02, key03, key04, key11, key12, key13, key14, key15, key16, currentPage
    global mapColor, currentMap, currentTileX, zoomlevel
    global loadingMap, showWaypoint, subPageMap
    if key11:
        subPageMap = "KSTR"
        clearKeys()
    if key12:
        subPageMap = "VAT"
        clearKeys()

    if key14:
        currentPage = "CHECKLIST"
        clearKeys()
    if key16:
        currentPage = "MENU"
        clearKeys()



    if (subPageMap == "KSTR") :
        if key01:
            clearKeys()
            zoomlevel += 1
            if (zoomlevel >12):
                zoomlevel = 12
            print("zoomlevel ", zoomlevel)
        if key02:
            clearKeys()
            zoomlevel -= 1
            if (zoomlevel <1):
                zoomlevel = 1
            print("zoomlevel ", zoomlevel)
        if key03:
            clearKeys()
            mapColor = mapColor + 1
            if (mapColor >= len(mapColors) ):
                mapColor = 0
        if key04:
            clearKeys()
            mapColor = mapColor - 1
            if (mapColor < 0 ):
                mapColor = 0

    if (subPageMap == "VAT") :
        if key01:
            clearKeys()
            nextWaypoint(manual=True)
        if key02:
            clearKeys()
            showWaypoint = not showWaypoint

        if key03:
            clearKeys()

        if key04:
            clearKeys()
            currentPage = "WAYPOINT"



    #set3d()
    set2d()
    drawMap(xfscale(0), yfscale(250))
    drawAirports(xfscale(0), yfscale(250))
    if (showWaypoint):
        drawWaypoints(xfscale(0), yfscale(250))
        drawWaypointsInfo()
    glColor4f(1.0,0,0,1.0)

    #drawCompass(xfscale(0), yfscale(910), afscale(800))
    drawFlightDirector(xfscale(0), yfscale(500))
    drawFlightDirectorLines(xfscale(0), yfscale(500))
    setColor(colorBlack)
    rect(0, 0, afscale(25),yfscale(1000))
    rect(0, yfscale(1000-25), xfscale(1000),yfscale(25))
    setColor(colorGreenLight)
    vertText(afscale(25/2), yfscale(1000)/7*6, "KSTR") # key11
    vertText(afscale(25/2), yfscale(1000)/7*5, "VAT")  # key12
    vertText(afscale(25/2), yfscale(1000)/7*4, "")

    vertText(afscale(25/2), yfscale(1000)/7*3, "")  # key14
    vertText(afscale(25/2), yfscale(1000)/7*2, "")
    vertText(afscale(25/2), yfscale(1000)/7*1, "MENY")  # key16


    if (subPageMap == "KSTR") :
        rect_line(afscale(1), yfscale(1000)/7*6 -afscale(120/2), afscale(25), afscale(120), afscale(2))

        horiText(xfscale(-200), yfscale(1000-25), "+") # key01
        horiText(xfscale(-100), yfscale(1000-25), "-") # key02
        horiText(xfscale(100), yfscale(1000-25), "FÄRG")  # key03
        horiText(xfscale(200), yfscale(1000-25), "")  # key04
    if (subPageMap == "VAT") :
        rect_line(afscale(1), yfscale(1000)/7*5 -afscale(120/2), afscale(25), afscale(120), afscale(2))

        horiText(xfscale(-200), yfscale(1000-25), "STEG") # key01
        horiText(xfscale(-100), yfscale(1000-25), "VISA") # key02
        horiText(xfscale(100), yfscale(1000-25), "")  # key03
        horiText(xfscale(200), yfscale(1000-25), "LIST")  # key04

    setColor(colorGreenLight)
    jas(xfscale(0), yfscale(250-25), afscale(25))
    if loadingMap == True:
        setColor(colorGreenLight)
        linebreakText(xfscale(-50), yfscale(100), "Laddar karta", checklabel)
    #fps_display.draw()
    fps_display.draw()
    unSet2d()

def pageMenu():
    global key01, key02, key03, key04, key11, key12, key13, key14, key15, key16, currentPage
    if key11:
        currentPage = "MAP"
        clearKeys()
    if key14:
        currentPage = "CHECKLIST"
        clearKeys()
    if key15:
        currentPage = "WAYPOINT"
        clearKeys()
    #set3d()
    set2d()

    glColor4f(1.0,0,0,1.0)
    fps_display.draw()

    drawFlightDirector(xfscale(0), yfscale(500))
    drawFlightDirectorLines(xfscale(0), yfscale(500))

    #BUTTONS
    setColor(colorBlack)
    rect(0, 0, afscale(25),yfscale(1000))
    rect(0, yfscale(1000-25), xfscale(1000),yfscale(25))
    setColor(colorGreenLight)
    vertText(afscale(25/2), yfscale(1000)/7*6, "KART")
    vertText(afscale(25/2), yfscale(1000)/7*5, "")
    vertText(afscale(25/2), yfscale(1000)/7*4, "")

    vertText(afscale(25/2), yfscale(1000)/7*3, "CHKL")
    vertText(afscale(25/2), yfscale(1000)/7*2, "WAYP")
    vertText(afscale(25/2), yfscale(1000)/7*1, "")

    horiText(xfscale(-200), yfscale(1000-25), "")
    horiText(xfscale(-100), yfscale(1000-25), "")
    horiText(xfscale(100), yfscale(1000-25), "")
    horiText(xfscale(200), yfscale(1000-25), "")



    unSet2d()




checklistfiles = PathToDict("checklists"+os.sep)

checklists = []
selectedList = 0

for key, item in checklistfiles["items"].items():
    if item["type"] == 'f':
        if key.endswith(".txt"):
            list = {}
            f = open(item['full_path'])
            list["name"] = key.replace(".txt", "")
            list["text"] = f.read()
            checklists.append(list)

scrollCheck = 0
def pageChecklist():
    global key01, key02, key03, key04, key11, key12, key13, key14, key15, key16
    global currentPage, selectedList, scrollCheck
    if key11:
        currentPage = "MAP"
        clearKeys()
    if key16:
        currentPage = "MENU"
        clearKeys()
    if key01:
        selectedList = selectedList - 1
        scrollCheck = 0
        if selectedList < 0:
            selectedList = 0
        clearKeys()
    if key02:
        selectedList = selectedList + 1
        scrollCheck = 0
        if selectedList >= len(checklists):
            selectedList = len(checklists)-1
        clearKeys()
    if key03:
        scrollCheck = scrollCheck - 1
        if scrollCheck < 0:
            scrollCheck = 0
        clearKeys()
    if key04:
        scrollCheck = scrollCheck + 1
        clearKeys()
    #set3d()
    set2d()

    setColor(colorGreenLight)

    linebreakText(xfscale(-200), yfscale(900), checklists[selectedList]["name"], checklabel)
    linebreakText(xfscale(-340), yfscale(800)+scrollCheck*afscale(100), checklists[selectedList]["text"], checklabel)

    #drawFlightDirector(xfscale(0), yfscale(500))
    #drawFlightDirectorLines(xfscale(0), yfscale(500))

    #BUTTONS
    setColor(colorBlack)
    rect(0, 0, afscale(25),yfscale(1000))
    rect(0, yfscale(1000-25), xfscale(1000),yfscale(25))
    setColor(colorGreenLight)
    vertText(afscale(25/2), yfscale(1000)/7*6, "KART")
    vertText(afscale(25/2), yfscale(1000)/7*5, "")
    vertText(afscale(25/2), yfscale(1000)/7*4, "")

    vertText(afscale(25/2), yfscale(1000)/7*3, "CHKL")
    vertText(afscale(25/2), yfscale(1000)/7*2, "")
    vertText(afscale(25/2), yfscale(1000)/7*1, "MENY") #key16

    horiText(xfscale(-250), yfscale(1000-25), "FÖRG") #key01
    horiText(xfscale(-100), yfscale(1000-25), "NÄSTA") #key02
    horiText(xfscale(100), yfscale(1000-25), "UPP") #key03
    horiText(xfscale(200), yfscale(1000-25), "NER") #key04

    unSet2d()



@window.event
def on_draw():

    loadPage()




@window.event
def on_key_press(s,m):

    global heading, tilt, altitude, rota, geardown, totalFuel, rawFuel, zoomlevel, lat, lon, zoomfactor, currentMap, mapColor

    if s == pyglet.window.key.NUM_SUBTRACT:
        zoomlevel -= 1
        if (zoomlevel <1):
            zoomlevel = 1
        print("zoomlevel ", zoomlevel)
    if s == pyglet.window.key.NUM_ADD:
        zoomlevel += 1
        if (zoomlevel >12):
            zoomlevel = 12
        print("zoomlevel ", zoomlevel)

    if s == pyglet.window.key.NUM_MULTIPLY:
        zoomfactor -= 0.5
        print("zoomfactor ", zoomfactor)

    if s == pyglet.window.key.NUM_DIVIDE:
        zoomfactor += 0.5
        print("zoomfactor ", zoomfactor)

    if s == pyglet.window.key.PAGEUP:
        currentMap = currentMap + 1
        if (currentMap >= len(maps["maps"]) ):
            currentMap = 0
    if s == pyglet.window.key.PAGEDOWN:
        mapColor = mapColor + 1
        if (mapColor >= len(mapColors) ):
            mapColor = 0
    if s == pyglet.window.key.UP:
        lat += 0.1
    if s == pyglet.window.key.DOWN:
        lat -= 0.1
    if s == pyglet.window.key.LEFT:
        lon -= 0.1
    if s == pyglet.window.key.RIGHT:
        lon += 0.1
    #lat = lat + 0.001
    #if lat > 60.0:
    #    lat = 58.0
    #lon = lon + 0.001
    #if lon > 19.0:
    #    lon = 17.0
    if s == pyglet.window.key.W:
        tilt -= 1.1
    if s == pyglet.window.key.S:
        tilt += 1.1
    if s == pyglet.window.key.A:
        heading += 1.1
    if s == pyglet.window.key.D:
        heading -= 1.1
    if s == pyglet.window.key.R:
        altitude -= 100
    if s == pyglet.window.key.F:
        altitude += 100
    if s == pyglet.window.key.Q:
        rota += -1
    if s == pyglet.window.key.E:
        rota += 1
    if s == pyglet.window.key.G:
        if (geardown):
            geardown = False
        else:
            geardown = True

    if s == pyglet.window.key.F12:
        window.set_fullscreen(not window.fullscreen)

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
    if (event.name == "f1"):
        key01 = True
    if (event.name == "f2"):
        key02 = True
    if (event.name == "f3"):
        key03 = True
    if (event.name == "f4"):
        key04 = True

    if (event.name == "f5"):
        key11 = True
    if (event.name == "f6"):
        key12 = True
    if (event.name == "f7"):
        key13 = True
    if (event.name == "f8"):
        key14 = True
    if (event.name == "f9"):
        key15 = True
    if (event.name == "f10"):
        key16 = True


    print(event)
def keyPressCallback5(event, b1, b2, b3, b4):

    keyPressCallback(event)
@window.event
def on_resize(width, height):
        print ('on resize')
        if height == 0:
            height = 1
        glViewport(0, 0, width, height) # specify viewport

        # load perspective projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.0 * width / height, 1, 100)
        createLabels()
        #glLoadIdentity()


#keyboard.add_hotkey("F1", keyPressCallback5, args=("key01"))
#keyboard.add_hotkey("F2", keyPressCallback5, args=("key02"))
#keyboard.add_hotkey("F3", keyPressCallback5, args=("key03"))
#keyboard.add_hotkey("F4", keyPressCallback5, args=("key04"))

#keyboard.add_hotkey("F5", keyPressCallback5, args=("key11"))
#keyboard.add_hotkey("F6", keyPressCallback5, args=("key12"))
#keyboard.add_hotkey("F7", keyPressCallback5, args=("key13"))
#keyboard.add_hotkey("F8", keyPressCallback5, args=("key14"))
#keyboard.add_hotkey("F9", keyPressCallback5, args=("key15"))
#keyboard.add_hotkey("F10", keyPressCallback5, args=("key16"))

x = threading.Thread(target=readNetwork)
print("startar nätverks tråd")
x.start()

clearKeys()
keyboard.on_press(keyPressCallback, suppress=False)

# every 1/10 th get the next frame
pyglet.clock.schedule(update_frame, 1/10.0)
pyglet.app.run()

running = False
