import cv2
import numpy as np
import time
import random
pi = 3.14159265359


def distance(ax, ay, bx, by):
    return np.sqrt((ax - bx) ** 2 + (ay - by) ** 2)


def generate(tsp):
    global get, dx, dy, x, y, dxf, dyf, xdir, ydir, b
    if get == 1:
        while distance(dx, dy, x, y) < 150:
            dx = random.randint(0, 640)
            dy = random.randint(0, 480)
            dxf = dx
            dyf = dy
        get = 0
        xdir = np.cos(b)
        ydir = np.sin(b)
    if get == 0:
        if dx > 600:
            xdir = -np.cos(b)
        elif dx < 40:
            xdir = np.cos(b)
        if dy > 440:
            ydir = -np.sin(b)
        elif dy < 40:
            ydir = np.sin(b)
        dxf += tsp * xdir
        dyf += tsp * ydir
        dx = int(dxf)
        dy = int(dyf)


def getangledist(xx, yy, dxx, dyy, aa):
    if dxx == xx:
        if dyy > yy:
            de = -pi/2
        else:
            de = pi/2
    elif dxx < xx:
        if dyy > yy:
            de = - np.arctan((dyy - yy) / (dxx - xx)) - pi
        else:
            de = pi - np.arctan((dyy - yy) / (dxx - xx))
    else:
        de = - np.arctan((dyy - yy) / (dxx - xx))
    de = de - aa
    if de > pi:
        de -= 2 * pi
    elif de < -pi:
        de += 2 * pi
    dis = distance(dxx, dyy, xx, yy)
    return de, dis


def switch(de):
    if -pi/2 < de < pi/2:
        re = 0
    else:
        if de > 0:
            de -= pi
        else:
            de += pi
        re = 1
    return de, re

def goto(de, re, spd):
    if de > pi/12:
        ls = 3
        rs = -3
    elif de < -pi/12:
        ls = -3
        rs = 3
    else:
        ls = spd + 3 * de
        rs = spd - 3 * de
    if re == 1:
        temp = ls
        ls = -rs
        rs = -temp
    return ls, rs


def gotopro(de, re, dis):
    if dis > 15:
        return goto(de, re, 6)
    elif dis > 3:
        return goto(de, re, 3)
    else:
        return goto(de, re, 0)


def getpre(xx, yy, aa, arr):
    dea, disa = np.zeros(20), np.zeros(20)
    for i in range(0, len(arr)):
        dea[i], disa[i] = getangledist(xx, yy, arr[i][0], arr[i][1], aa)
    m = 0
    while (1.8 * disa[m] > 40 * (m + 1)):
        m += 1
        if m == 19:
            break
    return m


def getdir(dxx, dyy, dxxo, dyyo):
    if dxx > dxxo and dyy < dyyo:
        return 1
    elif dxx < dxxo and dyy < dyyo:
        return 2
    elif dxx < dxxo and dyy > dyyo:
        return 3
    elif dxx > dxxo and dyy > dyyo:
        return 4
    else:
        return 0


def gettrack(dtt, dxx, dyy, tsp):
    dxxf = dxx
    dyyf = dyy
    if dtt == 1:
        xxdir = np.cos(b)
        yydir = -np.sin(b)
    elif dtt == 2:
        xxdir = -np.cos(b)
        yydir = -np.sin(b)
    elif dtt == 3:
        xxdir = -np.cos(b)
        yydir = np.sin(b)
    elif dtt == 4:
        xxdir = np.cos(b)
        yydir = np.sin(b)
    else:
        xxdir = 0
        yydir = 0
    result = [[0 for col in range(2)] for row in range(20)]
    for i in range(0, 100):
        if dxx > 600:
            xxdir = -np.cos(b)
        elif dxx < 40:
            xxdir = np.cos(b)
        if dyy > 440:
            yydir = -np.sin(b)
        elif dyy < 40:
            yydir = np.sin(b)
        dxxf += tsp * xxdir
        dyyf += tsp * yydir
        dxx = int(dxxf)
        dyy = int(dyyf)
        if i % 5 == 0:
            result[i//5] = (dxx, dyy)
    return result


def move(ls, rs):
    global a, xf, yf, x, y
    a += (ls - rs) / (l / 2)
    xf += np.cos(a) * (ls + rs) / 2
    yf -= np.sin(a) * (ls + rs) / 2
    x = int(xf)
    y = int(yf)


def draw():
    global xf, yf, x, y, l, a, dx, dy, going, mm
    img = np.zeros((480, 640, 3))
    if get1 == 0:
        for i in range(0, len(going)):
            if i == mm:
                cv2.circle(img, (going[i][0], going[i][1]), 2, (0, 0, 255), 2)
            else:
                cv2.circle(img, (going[i][0], going[i][1]), 2, (255, 255, 255), 2)
    hx = int(xf + l * np.cos(a) / 2)
    hy = int(yf - l * np.sin(a) / 2)
    tx = int(xf - l * np.cos(a) / 2)
    ty = int(yf + l * np.sin(a) / 2)
    cv2.circle(img, (hx, hy), 4, (0, 255, 255), 3)
    cv2.circle(img, (tx, ty), 4, (0, 255, 0), 3)
    cv2.line(img, (hx, hy), (tx, ty), (255, 255, 255))
    cv2.circle(img, (dx, dy), 4, (255, 0, 0), 3)
    cv2.line(img, (x, y), (dx, dy), (255, 255, 255))
    cv2.imshow('car', img)
    cv2.waitKey(1)


x = 320
y = 240
xf = 320
yf = 240
dx = 320
dy = 240
idx = 320
idy = 240
dxf = 320
dyf = 240

l = 60
a = 0
delta = 0
dist = 0

b = pi/4
xdir = 0
ydir = 0
dt = 0

lspeed = 0
rspeed = 0

get = 1
get1 = 1
getcnt = 0
frame = 0
mm = 0
num = 0
rev = 0
random.seed(time.clock())

# car max speed = 6
# target speed = 8
generate(8)
while 1:
    # generate target
    dxo = dx
    dyo = dy
    generate(8)
    if frame > 5 * (mm + 1):
        get1 = 2
    # get track
    if get1 == 1:
        get1 = 2
    elif get1 == 2:
        dt = getdir(dx, dy, dxo, dyo)
        going = gettrack(dt, dx, dy, 8)
        mm = getpre(x, y, a, going)
        idx, idy = going[mm]
        get1 = 0
        frame = 0
    else:
        frame += 1
    # calculate angle
    delta, dist = getangledist(x, y, idx, idy, a)
    # head/tail switch
    delta, rev = switch(delta)
    # get speed
    # lspeed, rspeed = goto(delta, rev, 6)
    lspeed, rspeed = gotopro(delta, rev, dist)
    # move
    move(lspeed, rspeed)
    # check
    if distance(x, y, dx, dy) < 30:
        getcnt += 1
    elif getcnt > 0:
        getcnt -= 1
    if getcnt > 4:
        get = 1
        get1 = 1
        getcnt = 0
        num += 1
        print("get", num)
    # draw
    draw()
    time.sleep(0.05)