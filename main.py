# -*- coding: utf-8 -*-
'''
本程序模拟县、乡级道路的车辆让步情况：假定前方有4辆车，需为后面的一辆车让步
程序仿真比例为2:1, 在尺度上尽可能接近真实情况
程序涉及的距离单位均为米
一些尺度约定：
家用小汽车参考长度为3.5 * 1.8，单位：米， 此处取整数值4 * 2
安全距离参考：
高速行车，即车速在30m/s以上时，安全车距在90米以上。
快速行车，即车速在20m/s以上时，安全车距在60米。
中速行车，即车速在10m/s以上时，安全车距不低于30米。
低速行车，即车速在10m/s以下时，安全车距不低于10米。

一般1.6排量自然吸气的家用汽车,从0km/H到100km/H的加速时间约为12秒。
按 v=at, a约为:100x1000/60/60/12=2.315m/s2, 程序取2
'''

# 导入程序相关的模块
import pygame
from pygame.locals import *
from sys import exit
from os import environ
from time import time

# xa = input()
# xb = input()
# xc = input()
# xd = input()
# xe = input()

# 家用小汽车参考长度3.5*1.8，单位：米， 此处取整数值
vehicle_lenth = 4
vehicle_width = 2
safe_distance = 30
# 宽度为7.5米，单车道约为4米
lane_width = 4
road_length = 150
road_width = 8
# 窗口大小属性
window_width = 10 * road_length
window_height = 10 * road_width + 50
road_image_name = "images\\road.jpg"
epsilon_v = 0.0005
epsilon_a = 0.001
# 比例尺：1:2
# 单位：米， 米每秒,  米每秒的平方
# xa, ya, va, aa = 40, 1, 10, 2
# xb, yb, vb, ab = 70, 1, 10, 2
# xc, yc, vc, ac = 100, 1, 10, 2
# xd, yd, vd, ad = 110, 5, 10, 2
# xe, ye, ve, ae = 0, 1, 20, 4
xa, ya, va, aa = 70, 5, 10, 2
xb, yb, vb, ab = 80, 1, 10, 2
xc, yc, vc, ac = 90, 1, 10, 2
xd, yd, vd, ad = 95, 5, 10, 2
xe, ye, ve, ae = 0, 1, 20, 6


class Car:
    highWay_state = 0
    def __init__(self, name, x, y, v, a):
        self.name = name
        self.image = None
        self.color = None
        self.length = vehicle_lenth
        self.width = vehicle_width

        self.xInit = x
        self.yInit = y
        self.vInit = v
        self.aInit = a
        self.vy = 5

        self.x = self.xInit
        self.y = self.yInit
        self.v = self.vInit
        self.a = self.aInit

        self.front_car = None
        # self.safe_dist = self.v * 3
        self.safe_dist = safe_distance
        self.safe = False
        # self.back_car = None

        if self.y < lane_width:
            self.lane = 0
        else:
            self.lane = 1

    def change_lane(self):
        self.y = 1 - self.y

    def change_accelorate(self, a):
        self.a = a

    def reset_position(self):
        self.x = self.xInit
        self.y = self.yInit
        self.v = self.vInit
        self.a = self.aInit


def sort_key(car):
    return car.x


def simulation(cars):
    pygame.init()
    environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (10, 100)
    # 生成窗口以及窗口标题
    screen = pygame.display.set_mode((window_width, window_height), 0, 32)
    pygame.display.set_caption("Cars")

    # 加载并转换图片
    highway = pygame.transform.scale(pygame.image.load(road_image_name).convert(), (road_length * 10, road_width * 10))
    for car in cars:
        car.image = pygame.transform.scale(pygame.image.load('images\\car' + car.name + '.png').convert_alpha(), (40, 20))

    font = pygame.font.SysFont('microsoft Yahei', 40)

    # 主循环
    t0 = time()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.display.quit()
                exit()

        screen.fill([255, 255, 255])
        screen.blit(highway, (0, 0))
        for car in cars:
            if car.front_car != None and car.front_car.x - car.x < car.safe_dist:
                if car.v > 3:
                    car.v -= car.a * epsilon_a
                car.safe = False
            if car.front_car == None or car.front_car.x - car.x > car.safe_dist:
                if car.v < car.vInit:
                    car.v += car.a * epsilon_a
                car.safe = True
            car.x += car.v * epsilon_v
            if car.safe and car.name != 'E' and car.y < 5:
                car.y += car.vy * epsilon_v
            screen.blit(car.image, (10 * car.x, 10 * car.y))
        if cars[-1].x > road_length + cars[-1].length:
            print("time : ", time() - t0)
            t0 = time()
            for car in cars:
                car.reset_position()
        i = 0
        for car in cars[:-1]:
            if car.y < lane_width:
                cars[-1].front_car = car
                i =  1
                break
        if i == 0:
            cars[-1].front_car = None
        # print(cars[-1].front_car.name)
        surface = font.render("v (m/s): ", False, (255, 200, 10))
        screen.blit(surface, (10, 90))
        i = 1
        for car in cars:
            surface = font.render(car.name + " : %.2f" % car.v, False, (255, 200, 10))
            screen.blit(surface, (150 * i, 90))
            i += 1
        pygame.display.update()


if __name__ == "__main__":
    cars = []
    n = 5
    cars.append(Car('A', xa, ya, va, aa))
    cars.append(Car('B', xb, yb, vb, ab))
    cars.append(Car('C', xc, yc, vc, ac))
    cars.append(Car('D', xd, yd, vd, ad))
    cars.sort(key=sort_key)
    for i in range(3):
        cars[i].front_car = cars[i+1]
    cars.append(Car('E', xe, ye, ve, ae))
    simulation(cars)
