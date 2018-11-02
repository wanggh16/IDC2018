# encoding:UTF-8
import cv2
import numpy as np
import math
import time
import serial
import random
import hello
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
import pygame

# 二值化找圆形轮廓函数
# 参数为6个HSV阈值
def find(lh, ls, lv, hh, hs, hv):
    X = quad3X
    Y = quad3Y
    lower = np.array([lh, ls, lv])
    upper = np.array([hh, hs, hv])
    mask = cv2.inRange(HSV, lower, upper)   # 二值化
    _, contours, _= cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 找图像轮廓
    temparea = 0
    for i in range(len(contours)):		# 遍历每个轮廓
        M = cv2.moments(contours[i])    # 求轮廓矩
        if M['m00'] > 5:				# 面积不为0
            cx = int(M['m10'] / M['m00'])		# 求中心坐标
            cy = int(M['m01'] / M['m00'])
            center, radius = cv2.minEnclosingCircle(contours[i])    # 最小覆盖圆
            dist = math.sqrt((center[0] - cx)**2 + (center[1] - cy)**2)
            if M['m00'] > temparea and M['m00'] > (radius**2) and cx >= quad3X and cx <= quad1X and cy >= quad3Y and cy <= quad1Y:
                # 面积最大，且圆度满足要求
                temparea = M['m00']		# 取面积最大的轮廓
                X = cx
                Y = cy
    return X, Y


# 找所有目标物
def finddest(lh, ls, lv, hh, hs, hv):
    lower = np.array([lh, ls, lv])
    upper = np.array([hh, hs, hv])
    mask = cv2.inRange(HSV, lower, upper)   # 二值化
    _, contours, _= cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 找图像轮廓
    X = []
    Y = []
    for i in range(len(contours)):		# 遍历每个轮廓
        M = cv2.moments(contours[i])    # 求轮廓矩
        if M['m00'] > 5:
            cx = int(M['m10'] / M['m00'])  # 求中心坐标
            cy = int(M['m01'] / M['m00'])
            if cx >= quad3X and cx <= quad1X and cy >= quad3Y and cy <= quad1Y:
                X.append(cx)
                Y.append(cy)
    return X, Y, len(X)


# 产生随机目标物
def randompoint():
    return random.randrange(quad3X + 30, quad1X - 30), random.randrange(quad3Y + 30, quad1Y - 30)

# 开串口
# serstr = input("input serial port: ")
serstr = "COM12"
ser = serial.Serial(serstr, 9600, timeout=50)
print("Using ", ser.portstr)

# 开相机
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 30)
camera.set(cv2.CAP_PROP_EXPOSURE, -5)
time.sleep(0.1)
i = 0

# 开GUI
if __name__ == '__main__':
    ui = hello.Ui_mainwindow()
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    # 这些参数在不同轮比赛是一样的
    # 四个角点坐标
    quad1X = 545
    quad1Y = 380
    quad2X = 80
    quad2Y = 380
    quad3X = 80
    quad3Y = 40
    quad4X = 545
    quad4Y = 40
	'''
    # 放点音乐玩
    pygame.init()
    track = pygame.mixer.music.load("BGM0.mp3")
    pygame.mixer.music.play()
    time.sleep(0.1)
	'''
    while 1:
        i += 1
        print("this is round ", i)
        # 这些参数在每轮比赛之前是要清空的
        go = 0  # 比赛状态，1开始，0停止
        cnt = 0  # 当前目标物编号
        dcnt = 0  # 上一帧是否找到了目标物，找到即为1，用来决定是否更换目标物位置
        keep = 0  # 小车需要保持在目标物上方的帧数
        num = 20  # 目标物最大数量
        tim = np.zeros(num + 1)  # 找到每个目标物所用时间
        DestX = 0  # 目标物XY
        DestY = 0
        init_DestX = 0  # 移动目标物的初始位置
        init_DestY = 0
        deltaDestX = 0  # 移动目标物的偏移量
        deltaDestY = 0
        DestXarray = []
        DestYarray = []
        a = np.pi / 4  # 目标物路径方位角
        xdir = np.cos(a)
        ydir = np.sin(a)

        # 主循环
        while 1:
            start = time.clock()    # 计算一帧时间用
            _, image = camera.read()

            # image=cv2.GaussianBlur(image, (9,9), 0)
            # 校正畸变
            size = (640, 480)
            # cameraMatrix = np.array([[444.0921, 0,322.7946],[0.0, 418.6386, 243.2555],[0.0, 0.0, 1]]) # 1.35m
            # distCoeffs = np.array([[-0.331557540080152], [0.104637411219310], [0], [0], [0]])   # 1.35m  [k1,k2,p1,p2,k3]
            cameraMatrix = np.array([[354.1292, 0, 340.7632], [0.0, 350.3886, 229.5138], [0.0, 0.0, 1]])  # 0.3m
            distCoeffs = np.array([[-0.346137013351145], [0.098960232607204], [0], [0], [0]])  # 0.3m
            retval, validPixROI = cv2.getOptimalNewCameraMatrix(cameraMatrix, distCoeffs, size, 1, size)
            # print(validPixROI)
            dst = cv2.undistort(image, cameraMatrix, distCoeffs, None, retval)
            x, y, w, h = validPixROI
            dst = dst[y:y+h, x:x+w]

            # 读ui滑条参数
            # 转HSV，找车头车尾坐标
            HSV = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)
            HeadX, HeadY = find(ui.head_hue_L.value(), ui.head_sat_L.value(), ui.head_val_L.value(), ui.head_hue_H.value(), 255, 255)    # 车头XY
            TailX, TailY = find(ui.tail_hue_L.value(), ui.tail_sat_L.value(), ui.tail_val_L.value(), ui.tail_hue_H.value(), 255, 255)    # 车尾XY
            # 这几个参数都需要做成输入滑条
            CenterX = 0		# 车中心XY
            CenterY = 0

            # 找到坐标时显示在图上
            if HeadX != 0 and HeadY != 0:
                cv2.circle(dst, (HeadX, HeadY), 3, (0, 255, 255), 6)
                cv2.putText(dst, "head", (HeadX, HeadY), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)
            if TailX != 0 and TailY != 0:
                cv2.circle(dst, (TailX, TailY), 3, (0, 0, 255), 6)
                cv2.putText(dst, "tail", (TailX, TailY), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            if HeadX != 0 and HeadY != 0 and TailX != 0 and TailY != 0:
                CenterX = int((HeadX + TailX) / 2)
                CenterY = int((HeadY + TailY) / 2)
                cv2.circle(dst, (CenterX, CenterY), 3, (0, 255, 0), 6)
                cv2.putText(dst, "center", (TailX, TailY), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

            if go == 0:
                if ui.match_status.value() == 1:    # 滑条控制比赛开始，懒得写按钮……
                    go = 1
                    print("match start")
                    tim[0] = time.clock()
                    dcnt = 1
                else:       #设置场地角点，或输出指定点HSV帮助调参
                    setx = ui.xpos.value()
                    sety = 419 - ui.ypos.value()
                    setsel = ui.pos_sel.value()
                    cv2.circle(dst, (setx, sety), 2, (0, 0, 255), 4)
                    if setsel == 0:
                        ui.hue.setText(str(HSV[sety][setx][0]))
                        ui.sat.setText(str(HSV[sety][setx][1]))
                        ui.val.setText(str(HSV[sety][setx][2]))
                    elif setsel == 1:
                        quad1X = setx
                        quad1Y = sety
                    elif setsel == 2:
                        quad2X = setx
                        quad2Y = sety
                    elif setsel == 3:
                        quad3X = setx
                        quad3Y = sety
                    elif setsel == 4:
                        quad4X = setx
                        quad4Y = sety

            # 比赛进行中
            else:
                if dcnt == 1:       # 生成下一个目标物并输出一些信息
                    # 视觉目标物模式
                    # 这里可以看出目标物不是实时更新的，只读取一次蓝色色块坐标
                    if ui.mode.value() == 1 and cnt==0:
                        DestXarray, DestYarray, num = finddest(ui.dest_hue_L.value(), ui.dest_sat_L.value(), ui.dest_val_L.value(), ui.dest_hue_H.value(), 255, 255)
                        print("target count: ", num)
                        DestX = DestXarray[0]
                        DestY = DestYarray[0]
                    elif ui.mode.value() == 1 and cnt > 0 and cnt < num:
                        DestX = DestXarray[cnt]
                        DestY = DestYarray[cnt]

                    # 随机目标物模式
                    elif ui.mode.value() == 0 and cnt==0:
                        DestX, DestY = randompoint()
                        init_DestX = DestX
                        init_DestY = DestY
                        deltaDestX = 0
                        deltaDestY = 0
                        num = ui.rand_cnt.value()
                        print("target count: ", num)
                    elif ui.mode.value() == 0 and cnt > 0 and cnt < num:
                        DestX, DestY = randompoint()
                        init_DestX = DestX
                        init_DestY = DestY
                        deltaDestX = 0
                        deltaDestY = 0

                    # 比赛结束
                    else:
                        print("final time: ", tim[cnt]-tim[0], "seconds")
                        ui.match_status.setValue(0)
                        ui.pos_sel.setValue(0)
                        break
                    print("current target: No.", cnt+1)

                # 显示当前目标物坐标，并随机漂移
                if DestX != 0 and DestY != 0:
                    if ui.mode.value() == 0:
                        if DestX > quad1X - 30:
                            xdir = -np.cos(a)
                        elif DestX < quad3X + 30:
                            xdir = np.cos(a)
                        if DestY > quad1Y - 30:
                            ydir = -np.sin(a)
                        elif DestY < quad3Y + 30:
                            ydir = np.sin(a)
                        deltaDestX += xdir*ui.dest_spd.value()/10.0
                        deltaDestY += ydir*ui.dest_spd.value()/10.0
                        DestX = init_DestX + int(deltaDestX)
                        DestY = init_DestY + int(deltaDestY)
                    cv2.circle(dst, (DestX, DestY), 3, (255, 0, 0), 6)
                    cv2.putText(dst, "dest", (DestX, DestY), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
                    dcnt = 0

                # 小车与目标物接近了
                if (CenterX-DestX)**2 + (CenterY-DestY)**2 < ui.pixel_error.value()**2:
                    keep += 1
                    if keep > 5:        # 保持在目标物旁边5帧以上
                        cnt += 1
                        dcnt = 1        # 换下一个目标
                        keep = 0
                        tim[cnt] = time.clock()
                        print("target ", cnt, " get in ", tim[cnt]-tim[cnt-1], "seconds")
                        # print("total time: ", tim[cnt]-tim[0], "seconds")
                # 小车远离目标物
                else:
                    if keep > 0:
                        keep -= 1

            #画出场地
            cv2.line(dst, (quad1X, quad1Y), (quad2X, quad2Y), (255, 0, 255), 1)
            cv2.line(dst, (quad2X, quad2Y), (quad3X, quad3Y), (255, 0, 255), 1)
            cv2.line(dst, (quad3X, quad3Y), (quad4X, quad4Y), (255, 0, 255), 1)
            cv2.line(dst, (quad4X, quad4Y), (quad1X, quad1Y), (255, 0, 255), 1)

            # 坐标变换并显示，并编码串口所需字符串
            if go == 1:
                Xhsend = int(max(240*(HeadX-quad3X)/(quad1X-quad3X),0))
                Xtsend = int(max(240*(TailX-quad3X)/(quad1X-quad3X),0))
                Xdsend = int(max(240*(DestX-quad3X)/(quad1X-quad3X),0))
                Yhsend = int(max(180-180*(HeadY-quad3Y)/(quad1Y-quad3Y),0))
                Ytsend = int(max(180-180*(TailY-quad3Y)/(quad1Y-quad3Y),0))
                Ydsend = int(max(180-180*(DestY-quad3Y)/(quad1Y-quad3Y),0))
                ui.hx.setText(str(Xhsend))
                ui.hy.setText(str(Yhsend))
                ui.tx.setText(str(Xtsend))
                ui.ty.setText(str(Ytsend))
                ui.dx.setText(str(Xdsend))
                ui.dy.setText(str(Ydsend))
                strsend = '0' + chr(Xhsend) + chr(Yhsend) + chr(Xtsend) + chr(Ytsend) + chr(Xdsend) + chr(Ydsend) + '\r' + '\n'

                if HeadX != quad3X and TailX != quad3X and DestX != quad3X:		# 数据有效才发送，防止选手动作不稳定
                    ser.write(strsend.encode(encoding = 'latin1'))

            # 显示图像，其实有ui就不需要它了，但去掉的话ui也显示不出来，不知道为啥，只能这样最小化了
            cv2.imshow("map", dst)
            cv2.moveWindow("map", 0, 0)
            cv2.resizeWindow("map", 1, 1)
            # 在UI上画图
            dst = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)
            img = QImage(dst.data, dst.shape[1], dst.shape[0], dst.shape[1] * 3, QImage.Format_RGB888)        # 这句话只能这么写，查了一个小时……
            ui.arena.setPixmap(QPixmap.fromImage(img))
            cv2.waitKey(1)
            ui.tim.setText(str(ui.match_status.value()*(time.clock()-tim[0])))
            # print(time.clock() - start)