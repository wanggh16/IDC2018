import numpy as np
import serial
import cv2
pi = 3.14159265359


def distance(ax, ay, bx, by):
    return np.sqrt((ax - bx) ** 2 + (ay - by) ** 2)


def getangle(xx, yy, dxx, dyy):
    if dxx == xx:
        if dyy < yy:
            de = -pi/2
        else:
            de = pi/2
    elif dxx < xx:
        if dyy < yy:
            de = np.arctan((dyy - yy) / (dxx - xx)) - pi
        else:
            de = np.arctan((dyy - yy) / (dxx - xx)) + pi
    else:
        de = np.arctan((dyy - yy) / (dxx - xx))
    return de


def getangledist(xx, yy, dxx, dyy, aa):
    de = getangle(xx, yy, dxx, dyy) - aa
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
    if de > pi/6:
        ls = -100
        rs = 100
    elif de < -pi/6:
        ls = 100
        rs = -100
    else:
        ls = int(spd + 100 * de)
        rs = int(spd - 100 * de)
    if re == 1:
        temp = ls
        ls = -rs
        rs = -temp
    return ls, rs


def gotopro(de, re, dis):
    if dis > 15:
        return goto(de, re, 200)
    elif dis > 3:
        return goto(de, re, 100)
    else:
        return goto(de, re, 0)


def getpre(xx, yy, aa, arr):
    dea, disa = np.zeros(20), np.zeros(20)
    for i in range(0, len(arr)):
        dea[i], disa[i] = getangledist(xx, yy, arr[i][0], arr[i][1], aa)
    m = 0
    while (2 * disa[m] > 16 * (m + 1)):
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
    for i in range(0, 160):
        if dxx > 223:
            xxdir = -np.cos(b)
        elif dxx < 17:
            xxdir = np.cos(b)
        if dyy > 163:
            yydir = -np.sin(b)
        elif dyy < 17:
            yydir = np.sin(b)
        dxx += tsp * xxdir
        dyy += tsp * yydir
        if i % 8 == 0:
            result[i//8] = (dxx, dyy)
    return result


def read():
    string = readport.readline()
    while len(string) != 9:
        string = readport.readline()
    hx = string[1]
    hy = string[2]
    tx = string[3]
    ty = string[4]
    dx = string[5]
    dy = string[6]
    return (hx+tx)/2, (hy+ty)/2, dx, dy, getangle(tx, ty, hx, hy)


def write(ls, rs):
    if ls > 0 and rs > 0:
        strsend = chr(1) + chr(abs(ls)) + chr(abs(rs))
    elif ls < 0 and rs > 0:
        strsend = chr(2) + chr(abs(ls)) + chr(abs(rs))
    elif ls > 0 and rs < 0:
        strsend = chr(3) + chr(abs(ls)) + chr(abs(rs))
    elif ls < 0 and rs < 0:
        strsend = chr(4) + chr(abs(ls)) + chr(abs(rs))
    else:
        strsend = chr(1) + chr(1) + chr(1)
    writeport.write(strsend.encode(encoding='latin1'))


def draw():
    global x, y, a, dx, dy, going, mm
    img = np.zeros((180, 240, 3))
    if get == 0:
        for i in range(0, len(going)):
            if i == mm:
                cv2.circle(img, (int(going[i][0]), 180 - int(going[i][1])), 2, (0, 0, 255), 2)
            else:
                cv2.circle(img, (int(going[i][0]), 180 - int(going[i][1])), 2, (255, 255, 255), 2)
    hx = x + 10 * np.cos(a)
    hy = y + 10 * np.sin(a)
    tx = x - 10 * np.cos(a)
    ty = y - 10 * np.sin(a)
    cv2.circle(img, (int(hx), int(180 - hy)), 3, (0, 255, 255), 2)
    cv2.circle(img, (int(tx), int(180 - ty)), 3, (0, 255, 0), 2)
    cv2.line(img, (int(hx), 180 - int(hy)), (int(tx), 180 - int(ty)), (255, 255, 255))
    cv2.circle(img, (dx, 180 - dy), 3, (255, 0, 0), 2)
    cv2.line(img, (int(x), 180 - int(y)), (dx, 180 - dy), (255, 255, 255))
    cv2.imshow('car', img)
    cv2.waitKey(1)

x = 120
y = 90
dx = 120
dy = 90
idx = 120
idy = 90

a = 0
delta = 0
dist = 0

b = pi/4

lspeed = 0
rspeed = 0

get = 1
num = 0
rev = 0
mode = 0
frame = 0
mm = 0

readport = serial.Serial('COM21', 9600, timeout=50)
writeport = serial.Serial('COM29', 9600, timeout=50)

while 1:
    # get positions
    dxo = dx
    dyo = dy
    x, y, dx, dy, a = read()
    if frame > 8 * (mm + 1):
        get = 2
    if distance(dxo, dyo, dx, dy) > 10:
        get = 1
    # get track
    if mode == 1:
        idx = dx
        idy = dy
    else:
        if get == 1:
            get = 2
        elif get == 2:
            dt = getdir(dx, dy, dxo, dyo)
            going = gettrack(dt, dx, dy, 2)
            mm = getpre(x, y, a, going)
            idx, idy = going[mm]
            get = 0
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
    write(lspeed, rspeed)
    draw()