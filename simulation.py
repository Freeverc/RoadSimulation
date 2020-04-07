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
import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.axisartist as axisartist
from pygame.locals import *
from sys import exit
from os import environ
from time import time
import CarConfig
from CarConfig import Car
import math

# 比例尺：1:2
# 窗口大小属性
window_width = 10 * CarConfig.road_length
window_height = 10 * CarConfig.road_width + 150
road_image_name = "images\\road.jpg"
epsilon_t = 0.01
epsilon_t_x = 1 * epsilon_t
epsilon_t_v = 10 * epsilon_t
epsilon_t_a = 10 * epsilon_t
epsilon_t_da = 1 * epsilon_t

def make_cars():
    xa, ya, va, aa = 20, 5, CarConfig.v_abcd, CarConfig.a_init
    xb, yb, vb, ab = 41, 1, CarConfig.v_abcd, CarConfig.a_init
    xc, yc, vc, ac = 60, 5, CarConfig.v_abcd, CarConfig.a_init
    xd, yd, vd, ad = 66, 1, CarConfig.v_abcd, CarConfig.a_init
    xe, ye, ve, ae = 0, 1, CarConfig.v_e, CarConfig.a_init
    cars = [Car('A', xa, ya, va, aa), Car('B', xb, yb, vb, ab),
            Car('C', xc, yc, vc, ac), Car('D', xd, yd, vd, ad)]
    cars.sort(key=Car.sort_key)
    cars.append(Car('E', xe, ye, ve, ae))
    return cars


def simulation(cars):
    pygame.init()
    environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (10, 100)

    # 生成窗口以及窗口标题
    screen = pygame.display.set_mode((window_width, window_height), 0, 32)
    pygame.display.set_caption("Cars")
    # 加载并转换图片
    highway = pygame.transform.scale(pygame.image.load(road_image_name).convert(), (window_width, window_height - 150))
    for car in cars:
        car.image = pygame.transform.scale(pygame.image.load('images\\car' + car.name + '.png').convert_alpha(), (40, 20))
    # generate labels
    font = pygame.font.SysFont('microsoft Yahei', 40)
    x_label = font.render("x (m): ", False, (50, 50, 100))
    v_label = font.render("v (m/s): ", False, (50, 50, 100))
    a_label = font.render("a (m/s2): ", False, (50, 50, 100))

    # 主循环
    Car.gen_neighbors(cars)
    Car.gen_e_neighbors(cars)
    Car.gen_car_middle(cars)
    Car.x_middle_init = Car.x_middle
    Car.gen_expected_t(cars)
    Car.gen_aim_x(cars)
    Car.gen_neighbors(cars)
    Car.time_start()
    print("Car: ", Car.t_expected, Car.x_middle_init, Car.x_middle, Car.t_used)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.display.quit()
                exit()

        screen.fill([255, 255, 255])
        screen.blit(highway, (0, 0))
        Car.gen_car_middle(cars)
        pygame.draw.line(screen, (255, 0, 0), (10 * Car.x_middle, 0), (10 * Car.x_middle, window_height), 1)
        Car.gen_neighbors(cars)
        Car.gen_e_neighbors(cars)
        for car in cars:
            # car.soft_safe_adjust()
            # car.simple_safe_adjust()
            car.simple_aim_adjust()
            screen.blit(car.image, (10 * car.x, 10 * car.y))
            car.refresh_sequence()

        # show x, v, a
        screen.blit(x_label, (10, 90))
        screen.blit(v_label, (10, 140))
        screen.blit(a_label, (10, 190))
        for car in cars:
            x_text = font.render(car.name + " : %.2f" % car.x, False, (50, 50, 100))
            v_text = font.render(car.name + " : %.2f" % car.v, False, (50, 50, 100))
            a_text = font.render(car.name + " : %.2f" % car.a, False, (50, 50, 100))
            screen.blit(x_text, (150 * (1 + cars.index(car)), 90))
            screen.blit(v_text, (150 * (1 + cars.index(car)), 140))
            screen.blit(a_text, (150 * (1 + cars.index(car)), 190))
        pygame.display.update()
        if Car.e_pass_done(cars):
            Car.time_end()
            draw_figure(cars)
            for car in cars:
                car.reset_position()
            Car.time_start()


def simulation_aim(cars):
    pygame.init()
    environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (10, 100)

    # 生成窗口以及窗口标题
    screen = pygame.display.set_mode((window_width, window_height), 0, 32)
    pygame.display.set_caption("Cars")
    # 加载并转换图片
    highway = pygame.transform.scale(pygame.image.load(road_image_name).convert(), (window_width, window_height - 150))
    for car in cars:
        car.image = pygame.transform.scale(pygame.image.load('images\\car' + car.name + '.png').convert_alpha(), (40, 20))
    # generate labels
    font = pygame.font.SysFont('microsoft Yahei', 40)
    x_label = font.render("x (m): ", False, (50, 50, 100))
    v_label = font.render("v (m/s): ", False, (50, 50, 100))
    a_label = font.render("a (m/s2): ", False, (50, 50, 100))

    # 主循环
    Car.gen_neighbors(cars)
    Car.gen_e_neighbors(cars)
    Car.gen_car_middle(cars)
    Car.x_middle_init = Car.x_middle
    Car.gen_expected_t(cars)
    Car.gen_aim_x(cars)
    Car.gen_relative_x(cars)
    Car.gen_neighbors(cars)
    Car.gen_e_neighbors(cars)
    Car.time_start()
    print("Car: ", Car.t_expected, Car.x_middle_init, Car.x_middle, Car.t_used)
    delta_t = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.display.quit()
                exit()

        screen.fill([255, 255, 255])
        screen.blit(highway, (0, 0))
        Car.gen_car_middle(cars)
        pygame.draw.line(screen, (255, 0, 0), (10 * Car.x_middle, 0), (10 * Car.x_middle, window_height), 1)
        Car.gen_neighbors(cars)
        Car.gen_e_neighbors(cars)
        ep_t = delta_t * epsilon_t
        for car in cars:
            if not Car.adjust_done:
                A = car.relative_x
                car.a = A * 2 * math.pi / Car.t_expected / Car.t_expected * math.sin(ep_t * 2 * math.pi/Car.t_expected)
                car.v = car.vInit + A / Car.t_expected * (1 - math.cos(2*math.pi / Car.t_expected * ep_t))
                car.x = car.xInit + car.vInit * ep_t + ep_t * A / Car.t_expected - A  / 2 / math.pi * math.sin(2 * math.pi / Car.t_expected * ep_t)
            else:
                car.x += car.v * epsilon_t_x
                car.change_lane()
            screen.blit(car.image, (10 * car.x, 10 * car.y))
            car.refresh_sequence()

        if ep_t >= Car.t_expected and not Car.adjust_done:
            t_adjust_done = delta_t
            Car.adjust_done = True
            print(car.name, car.x, car.aim_x, car.v, car.vInit, car.a)
            print(car.name, "adjust done", t_adjust_done)
        if cars[-1].x >= cars[-2].x and not Car.pass_done:
            t_pass_done = delta_t
            Car.pass_done = True
            print(car.name, car.x, car.aim_x, car.v, car.vInit, car.a)
            print(car.name, "pass done", t_pass_done)
        delta_t += 1

        # show x, v, a
        screen.blit(x_label, (10, 90))
        screen.blit(v_label, (10, 140))
        screen.blit(a_label, (10, 190))
        for car in cars:
            x_text = font.render(car.name + " : %.2f" % car.x, False, (50, 50, 100))
            v_text = font.render(car.name + " : %.2f" % car.v, False, (50, 50, 100))
            a_text = font.render(car.name + " : %.2f" % car.a, False, (50, 50, 100))
            screen.blit(x_text, (150 * (1 + cars.index(car)), 90))
            screen.blit(v_text, (150 * (1 + cars.index(car)), 140))
            screen.blit(a_text, (150 * (1 + cars.index(car)), 190))
        pygame.display.update()
        if Car.e_pass_done(cars):
            print(delta_t)
            # if delta_t > 8000:
            Car.time_end()
            draw_figure(cars, t_adjust_done, t_pass_done)
            for car in cars:
                car.reset_position()
            Car.time_start()
            break

def simulation_aim1(cars):
    pygame.init()
    environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (10, 100)

    # 生成窗口以及窗口标题
    screen = pygame.display.set_mode((window_width, window_height), 0, 32)
    pygame.display.set_caption("Cars")
    # 加载并转换图片
    highway = pygame.transform.scale(pygame.image.load(road_image_name).convert(), (window_width, window_height - 150))
    for car in cars:
        car.image = pygame.transform.scale(pygame.image.load('images\\car' + car.name + '.png').convert_alpha(), (40, 20))
    # generate labels
    font = pygame.font.SysFont('microsoft Yahei', 40)
    x_label = font.render("x (m): ", False, (50, 50, 100))
    v_label = font.render("v (m/s): ", False, (50, 50, 100))
    a_label = font.render("a (m/s2): ", False, (50, 50, 100))

    # 主循环
    Car.gen_neighbors(cars)
    Car.gen_e_neighbors(cars)
    Car.gen_car_middle(cars)
    Car.x_middle_init = Car.x_middle
    Car.gen_expected_t(cars)
    Car.gen_aim_x(cars)
    Car.gen_relative_x(cars)
    Car.gen_neighbors(cars)
    Car.time_start()
    print("Car: ", Car.t_expected, Car.x_middle_init, Car.x_middle, Car.t_used)
    delta_t = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.display.quit()
                exit()

        screen.fill([255, 255, 255])
        screen.blit(highway, (0, 0))
        Car.gen_car_middle(cars)
        pygame.draw.line(screen, (255, 0, 0), (10 * Car.x_middle, 0), (10 * Car.x_middle, window_height), 1)
        Car.gen_neighbors(cars)
        Car.gen_e_neighbors(cars)
        ep_t = delta_t * epsilon_t
        # A =max(car[0].relative_x, car[1].relative_x, car[2].relative_x, car[3].relative_x)
        for car in cars:
            A = car.relative_x
            if not car.get_aim_x:
                car.a = A * 2 * math.pi / Car.t_expected / Car.t_expected * math.sin(ep_t * 2 * math.pi/Car.t_expected)
                car.v = car.vInit + A * Car.t_expected / 2 / math.pi * (1 - math.cos(2*math.pi / Car.t_expected * ep_t))
                car.x = car.xInit + car.vInit * ep_t + ep_t * A / Car.t_expected - A  / 2 / math.pi * math.sin(2 * math.pi / Car.t_expected * ep_t)
            else:
                car.x += car.v * epsilon_t_x
                car.change_lane()
            screen.blit(car.image, (10 * car.x, 10 * car.y))
            car.refresh_sequence()

        if ep_t >= Car.t_expected and not Car.adjust_done:
            t_adjust_done = delta_t
            Car.adjust_done = True
            print(car.name, car.x, car.aim_x, car.v, car.vInit, car.a)
            print(car.name, "adjust done", t_adjust_done)
        if cars[-1].x >= cars[-2].x and not Car.pass_done:
            t_pass_done = delta_t
            Car.pass_done = True
            print(car.name, car.x, car.aim_x, car.v, car.vInit, car.a)
            print(car.name, "pass done", t_pass_done)
        delta_t += 1

        # show x, v, a
        screen.blit(x_label, (10, 90))
        screen.blit(v_label, (10, 140))
        screen.blit(a_label, (10, 190))
        for car in cars:
            x_text = font.render(car.name + " : %.2f" % car.x, False, (50, 50, 100))
            v_text = font.render(car.name + " : %.2f" % car.v, False, (50, 50, 100))
            a_text = font.render(car.name + " : %.2f" % car.a, False, (50, 50, 100))
            screen.blit(x_text, (150 * (1 + cars.index(car)), 90))
            screen.blit(v_text, (150 * (1 + cars.index(car)), 140))
            screen.blit(a_text, (150 * (1 + cars.index(car)), 190))
        pygame.display.update()
        if Car.e_pass_done(cars):
            # if delta_t > 8000:
            Car.time_end()
            draw_figure(cars, t_adjust_done, t_pass_done)
            for car in cars:
                car.reset_position()
            Car.time_start()
            break

def draw_figure(cars, t_adjust_done, t_pass_done):
    # 通过set_visible方法设置绘图区的顶部及右侧坐标轴隐藏
    t_sequence = [ i / t_adjust_done * Car.t_expected for i in list(range(len(cars[0].x_sequence))) ]
    for car in cars:
        plt.figure()
        plt.plot(t_sequence, car.x_sequence)
        plt.savefig('figures\\' + car.name + 'x.png', format='png')
        plt.close()
        plt.figure()
        plt.plot(t_sequence, car.v_sequence)
        plt.savefig('figures\\' + car.name + 'v.png', format='png')
        plt.close()
        plt.figure()
        plt.plot(t_sequence, car.a_sequence)
        plt.savefig('figures\\' + car.name + 'a.png', format='png')
        plt.close()
    fig = plt.figure()
    ax = axisartist.Subplot(fig, 111)
    fig.add_axes(ax)
    ax.axis["top"].set_visible(False)
    ax.axis["right"].set_visible(False)
    ax.axis["left"].set_axisline_style("->", size=1.0)
    ax.axis["bottom"].set_axisline_style("->", size=1.0)
    plt.plot(t_sequence, cars[0].x_sequence)
    plt.plot(t_sequence, cars[1].x_sequence)
    plt.plot(t_sequence, cars[2].x_sequence)
    plt.plot(t_sequence, cars[3].x_sequence)
    plt.plot(t_sequence, cars[4].x_sequence)
    plt.vlines(Car.t_expected, min(car.x_sequence), max(car.x_sequence), color="k",linestyles='--')  # 竖线
    plt.vlines(t_pass_done / t_adjust_done * Car.t_expected, min(car.x_sequence), max(car.x_sequence), color="k", linestyles="--")  # 竖线
    plt.legend(["A", "B", "C", "D", "E"])
    plt.xlabel('time')
    plt.ylabel('distance')
    plt.ylim(0, max(car.x_sequence))
    plt.text(Car.t_expected - 1.5, 5, "t_a")
    plt.text(t_pass_done / t_adjust_done * Car.t_expected - 1.5, 5, "t_p")
    ax = plt.gca()
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    plt.savefig('figures\\x_all.png', format='png')
    plt.close()
    fig = plt.figure()
    ax = axisartist.Subplot(fig, 111)
    fig.add_axes(ax)
    ax.axis["top"].set_visible(False)
    ax.axis["right"].set_visible(False)
    ax.axis["left"].set_axisline_style("->", size=1.0)
    ax.axis["bottom"].set_axisline_style("->", size=1.0)
    plt.plot(t_sequence, cars[0].v_sequence)
    plt.plot(t_sequence, cars[1].v_sequence)
    plt.plot(t_sequence, cars[2].v_sequence)
    plt.plot(t_sequence, cars[3].v_sequence)
    plt.plot(t_sequence, cars[4].v_sequence)
    plt.legend(["A", "B", "C", "D", "E"])
    plt.xlabel('time')
    plt.ylabel('velocity')
    plt.savefig('figures\\v_all.png', format='png')
    plt.close()
    fig = plt.figure()
    ax = axisartist.Subplot(fig, 111)
    fig.add_axes(ax)
    ax.axis["top"].set_visible(False)
    ax.axis["right"].set_visible(False)
    ax.axis["left"].set_axisline_style("->", size=1.0)
    ax.axis["bottom"].set_axisline_style("->", size=1.0)
    plt.plot(t_sequence, cars[0].a_sequence)
    plt.plot(t_sequence, cars[1].a_sequence)
    plt.plot(t_sequence, cars[2].a_sequence)
    plt.plot(t_sequence, cars[3].a_sequence)
    plt.plot(t_sequence, cars[4].a_sequence)
    plt.legend(["A", "B", "C", "D", "E"])
    plt.xlabel('time')
    plt.ylabel('accelorate')
    plt.savefig('figures\\a_all.png', format='png')
    plt.close()
    # plt.figure()
    # data = np.array(cars[0].a_sequence) - np.array(cars[1].a_sequence)
    # plt.plot(range(len(cars[0].a_sequence)), data)
    # data = np.array(cars[1].a_sequence) - np.array(cars[1].a_sequence)
    # plt.plot(range(len(cars[0].a_sequence)), data)
    # data = np.array(cars[2].a_sequence) - np.array(cars[1].a_sequence)
    # plt.plot(range(len(cars[0].a_sequence)), data)
    # data = np.array(cars[3].a_sequence) - np.array(cars[1].a_sequence)
    # plt.plot(range(len(cars[0].a_sequence)), data)
    # data = np.array(cars[4].a_sequence) - np.array(cars[1].a_sequence)
    # plt.plot(range(len(cars[0].a_sequence)), data)
    # plt.plot(range(len(cars[1].a_sequence)), cars[1].a_sequence - car[1].a_sequence)
    # plt.plot(range(len(cars[2].a_sequence)), cars[2].a_sequence - car[1].a_sequence)
    # plt.plot(range(len(cars[3].a_sequence)), cars[3].a_sequence - car[1].a_sequence)
    # plt.plot(range(len(cars[4].a_sequence)), cars[4].a_sequence - car[1].a_sequence)
    # plt.legend(["A", "B", "C", "D", "E"])
    # plt.savefig('figures\\a_to_B_all.png', format='png')
    # plt.close()


if __name__ == "__main__":
    cars = make_cars()
    simulation_aim(cars)
