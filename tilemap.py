import json
import math
import os.path
import urllib3
import socket
import pyglet
from pyglet.gl import *
from sharedDrawFunctions import *

zoomlevel = 8
zoomfactor = 1.5
gearratio = 0.0
geardown = True

lon = 16.92
lat = 58.7761015

heading = 0.0
tilt = 0.0
rota = 0.0

speed = 0
altitude = 0

connection = False

currentTileX = 0
currentTileY = 0
currentTileZ = 7

EXTILES = 2 # extra tiles around center



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
    waypoints = json.load(way_file)
waypoints = waypoints["waypoints"]
#platform = pyglet.window.get_platform()
#display = platform.get_default_display()
display = pyglet.canvas.get_display()
screens = display.get_screens()
if (len(screens) >1):
  screen = screens[0]
else:
  screen = screens[0]

config = pyglet.gl.Config(sample_buffers=1, samples=1, depth_size=24)
window = pyglet.window.Window(config=config, resizable=True, width = 768, height=1024, screen=screen, fullscreen=False)
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



mapColor = 0
mapColors = [colorGreenDark,colorGreenMedium, colorRBG, colorGreenIntense, colorGreenLight, colorGreenDark, colorGreenSky]
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
    global speedlabel, smalllabel, speedlabels, altlabels, buttonlabel,waylabel
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
                        anchor_x='right', anchor_y='center',
                        group=None)
    waylabel = pyglet.text.Label(str("speed"),
                        font_name='Monospace',
                        font_size=aiscale(15),
                        color=(0,255,0,255),
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

def readNetwork():
    global tilt, heading, rota, speed, altitude, fuel, gload, gearratio, rawFuel, totalFuel, connection, lon, lat
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
        except socket.error:
            moredata = False
def update_frame(x, y):
    global gearratio, geardown, connection

    if (connection == False):
        fakevalues()
    readNetwork()

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
    r = http.request('GET', url)

    f = open(filename,'wb')
    f.write(r.data)
    f.close()
    return

def getTileImage(xtile, ytile, zoom):
    filename = "tiles" + os.path.sep + getCurrentMapDir() + os.path.sep + str(zoom) + os.path.sep + str(xtile) + os.path.sep + str(ytile) + ".png"
    directory = "tiles" + os.path.sep + getCurrentMapDir() + os.path.sep + str(zoom) + os.path.sep + str(xtile)
    if os.path.isfile(filename):
        #print ("File exist")
        return pyglet.resource.image(filename)
    else:
        print ("Cache miss: " + filename)
        from pathlib import Path
        Path(directory).mkdir(parents=True, exist_ok=True)
        downloadTile(xtile, ytile, zoom)

        pyglet.resource.reindex()

        return pyglet.resource.image(filename)
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

def updateTile(lat_deg,lon_deg,zoom):
    global currentTileX, currentTileY, currentTileZ, tileimage, tileimages
    (xtile, ytile) = deg2num(lat_deg, lon_deg, zoom)
    if (xtile != currentTileX or ytile != currentTileY or zoom != currentTileZ) :
        print("change tile")
        currentTileX = xtile
        currentTileY = ytile
        currentTileZ = zoom
        #tileimage = getTileImage(xtile, ytile, zoom)
        for x in range(1+EXTILES*2):
            for y in range(1+EXTILES*2):
                tileimages[x][y] = getTileImage(xtile-EXTILES+x, ytile-EXTILES+y, zoom)


def drawFlightDirector(x, y):
    global geardown
    wingspan = afscale(100/2)
    body = afscale(35/2)
    linewidth = afscale(4)


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


def drawFlightDirectorLines(x, y):
    global tilt, rota
    length = afscale(400)
    offset = afscale(75)
    linewidth = afscale(4)

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
    circle_line(0,0,afscale(3), afscale(3))
    glPopMatrix()

def drawWaypoints(x, y):
    glPushMatrix()
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #moving object left and right
    glTranslatef(x, y , -0.0 ) #x,y,z,

    glRotatef(heading, 0.0, 0.0, 1.0) #by 10 degrees around the x, y or z axis

    setColor((1.0,1.0,0.0,1.0))
    glPushMatrix()
    glScalef(zoomfactor, zoomfactor, 1)
    for xx in waypoints:
        (ox, oy) = whereInMap(xx["lat"],xx["lon"],zoomlevel)
        circle_line(ox,oy,afscale(3), afscale(3))
        waylabel.text = xx["text"]
        waylabel.x = ox + waylabel.font_size/2
        waylabel.y = oy
        waylabel.draw()
    setColor(colorGreenLight)
    glLineWidth(2)
    glBegin(GL_LINE_STRIP);
    for xx in waypoints:
        (ox, oy) = whereInMap(xx["lat"],xx["lon"],zoomlevel)
        #circle_line(ox,oy,afscale(3), afscale(3))
        glVertex2f(ox, oy)

    glEnd();
    glPopMatrix()
    #setColor(colorGreenLight)
    #circle_line(0,0,afscale(10), afscale(3))
    setColor(colorGreenLight)
    circle_line(0,0,afscale(3), afscale(3))
    glPopMatrix()


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

    #glClear(GL_COLOR_BUFFER_BIT)
def unSet2d():

    # load back the projection matrix saved before
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()


@window.event
def on_draw():

    #set3d()
    set2d()
    drawMap(xfscale(0), yfscale(250))
    drawWaypoints(xfscale(0), yfscale(250))
    glColor4f(1.0,0,0,1.0)
    fps_display.draw()
    drawCompass(xfscale(0), yfscale(910), afscale(800))
    drawFlightDirector(xfscale(0), yfscale(500))
    drawFlightDirectorLines(xfscale(0), yfscale(500))
    setColor(colorBlack)
    rect(0, 0, afscale(25),yfscale(1000))
    rect(0, yfscale(1000-25), xfscale(1000),yfscale(25))
    setColor(colorGreenLight)
    vertText(afscale(25), yfscale(1000)/7*6, "KSTR")
    vertText(afscale(25), yfscale(1000)/7*5, "VAT")
    vertText(afscale(25), yfscale(1000)/7*4, "UDAT")

    vertText(afscale(25), yfscale(1000)/7*3, "CHKL")
    vertText(afscale(25), yfscale(1000)/7*2, "LÄNK")
    vertText(afscale(25), yfscale(1000)/7*1, "FIX")



    horiText(xfscale(-200), yfscale(1000-25), "VAP")
    horiText(xfscale(-100), yfscale(1000-25), "LAND")
    horiText(xfscale(100), yfscale(1000-25), "ÄPOL")
    horiText(xfscale(200), yfscale(1000-25), "PMGD")

    setColor(colorGreenLight)
    jas(xfscale(0), yfscale(250-25), afscale(25))
    #fps_display.draw()

    unSet2d()

@window.event
def on_key_press(s,m):

    global heading, tilt, radie, rota, geardown, totalFuel, rawFuel, zoomlevel, lat, lon, zoomfactor, currentMap, mapColor

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
    if s == pyglet.window.key.F4:
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
        gluPerspective(45, 1.0 * width / height, 1, 100)
        createLabels()
        #glLoadIdentity()


test = deg2num(58.0, 16.0, zoomlevel)
print (test)
tileimage = getTileImage(test[0],test[1], zoomlevel)
hej = num2deg(test[0],test[1], zoomlevel)
print (hej)
# every 1/10 th get the next frame
pyglet.clock.schedule(update_frame, 1/10.0)
pyglet.app.run()
