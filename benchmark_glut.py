from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time
w,h= 1024,768
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
frames = 0
t0 = time.time()
def showScreen():
    global t0, frames
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    glColor3f(1.0, 0.0, 3.0)
    square()
    glutSwapBuffers()
    frames += 1
    t = time.time()
    if t-t0 >=5.0:
        sec = t -t0
        fps = frames / sec
        print(f"fps {fps}")
        t0 = t
        frames = 0

glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(w, h)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow("OpenGL Coding Practice")
glutDisplayFunc(showScreen)
glutIdleFunc(showScreen)
glutMainLoop()
