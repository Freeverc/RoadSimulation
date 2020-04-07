'''
class Car
定义汽车类及相关变量
'''

import time

# 家用小汽车参考长度3.5*1.8，单位：米， 此处取整数值
vehicle_lenth = 4
vehicle_width = 2

# 宽度为7.5米，单车道约为4米
road_length = 500
road_width = 8
lane_width = road_width / 2
road_safe_distance = 15

epsilon_t = 0.001
epsilon_t_x = 5 * epsilon_t
epsilon_t_v = 10 * epsilon_t
epsilon_t_a = 50 * epsilon_t
epsilon_t_da = 100 * epsilon_t

v_abcd = 50/3.6
v_e = 60/3.6
a_init = 0
max_v = 60/3.6
min_v = v_abcd - 10
max_a = 2
min_a = -2


class Car:
    x_middle_init = 0
    x_middle = 0
    highWay_state = 0
    t_expected = 0
    t_start = 0
    t_end = 0
    t_used = 0
    safe_distance = road_safe_distance
    adjust_dist = road_safe_distance + 10
    adjust_done = False
    pass_done = False

    @staticmethod
    def gen_neighbors(cars):
        for i in range(4):
            if i < 3:
                cars[i].front_car = cars[i+1]
            if i > 0:
                cars[i].back_car = cars[i-1]

    @staticmethod
    def gen_e_neighbors(cars):
        cars[-1].front_car = None
        for car in cars[:-1]:
            if car.y < lane_width:
                cars[-1].front_car = car
                if car.back_car == None or car.back_car.x < cars[-1].x:
                    car.back_car = cars[-1]
                break

    @staticmethod
    def gen_car_middle(cars):
        x_middle = 0
        for car in cars[:-1]:
            x_middle += car.x
        x_middle /= (len(cars) - 1)
        Car.x_middle = x_middle
        # print(x_middle)

    @staticmethod
    def gen_expected_t(cars):
        Car.t_expected = (Car.x_middle_init - 1.5 * Car.safe_distance) / (v_e - v_abcd)
        # Car.t_expected = (Car.x_middle_init - 1.5 * Car.safe_distance - lane_width / 5 * v_e) / (v_e - v_abcd)
        # Car.t_expected = (Car.x_middle_init + v_abcd * Car.t_expected - 1.5 * Car.safe_distance) / (v_e - v_abcd)

    @staticmethod
    def gen_aim_x(cars):
        cars[0].aim_x = Car.x_middle_init + v_abcd * Car.t_expected - 1.5 * Car.safe_distance
        cars[1].aim_x = Car.x_middle_init + v_abcd * Car.t_expected - 0.5 * Car.safe_distance
        cars[2].aim_x = Car.x_middle_init + v_abcd * Car.t_expected + 0.5 * Car.safe_distance
        cars[3].aim_x = Car.x_middle_init + v_abcd * Car.t_expected + 1.5 * Car.safe_distance
        cars[4].aim_x = Car.x_middle_init + v_abcd * Car.t_expected - 1.5 * Car.safe_distance
        # cars[4].aim_x = Car.x_middle_init + v_abcd * Car.t_expected - 1.5 * Car.safe_distance - lane_width / 5 * v_e
        print(cars[0].aim_x, cars[1].aim_x, cars[2].aim_x, cars[3].aim_x, cars[4].aim_x)

    @staticmethod
    def gen_aim_t(cars):
        # Car.t_expected = (Car.x_middle_init - 1.5 * Car.safe_distance) / (v_e - v_abcd)
        # for car in cars:
        #     car.get_aim_t =
        pass

    @staticmethod
    def gen_relative_x(cars):
        for car in cars:
            car.relative_x = car.aim_x - car.xInit - car.vInit * Car.t_expected
            print(car.name, " : ", car.xInit, car.aim_x, car.relative_x)

            if car.xInit + v_abcd * Car.t_expected > car.aim_x:
                car.speed_flag = -1
            elif car.xInit + v_abcd * Car.t_expected < car.aim_x:
                car.speed_flag = 1
            else:
                car.speed_flag = 0

    @staticmethod
    def adjust_to_aim_done(cars):
        for car in cars:
            if not car.x == car.aim_x or not car.v == car.vInit:
                return False
        return True

    @staticmethod
    def change_lane_done(cars):
        for car in cars:
            if not car.y >= road_width + 1:
                return False
        return True

    @staticmethod
    def e_pass_done(cars):
        if cars[-1].x > cars[-2].x + 5:
            return True
        else:
            return False

    @staticmethod
    def time_start():
        Car.t_start = time.time()

    @staticmethod
    def time_end():
        Car.t_end = time.time()
        print("time : ", Car.t_end - Car.t_start)

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
        self.t_finish = 0

        self.x = self.xInit
        self.y = self.yInit
        self.v = self.vInit
        self.vy = 5
        # self.vy = self.v / 2
        self.a = self.aInit
        self.delta_a = 0
        self.aim_x = self.xInit
        self.speed_flag = 1
        self.get_aim_x = False
        self.get_aim_v = False
        self.relative_x = 0
        self.get_aim_t = 0

        self.x_sequence = []
        self.v_sequence = []
        self.a_sequence = []

        self.front_car = None
        self.back_car = None
        self.front_car = None
        self.back_car = None
        self.front_dist = float('inf')
        self.back_dist = float('inf')
        self.front_dist_safe = False
        self.back_dist_safe = False
        self.front_speed_safe = False
        self.back_speed_safe = False
        # self.safe_dist = self.v * 3

        if self.y < lane_width:
            self.lane = 0
        else:
            self.lane = 1

    def gen_safe_flag(self):
        # generate distance
        if self.front_car is not None:
            self.front_dist = self.front_car.x - self.x
        else:
            self.front_dist = float('inf')
        if self.back_car is not None:
            self.back_dist = self.x - self.back_car.x
        else:
            self.back_dist = float('inf')

        # generate safe flag
        if self.front_car is not None:
            if self.front_dist < self.adjust_dist:
                self.front_dist_safe = False
            else:
                self.front_dist_safe = True
            if self.v > self.front_car.v:
                self.front_speed_safe = False
            else:
                self.front_speed_safe = True
        else:
            self.front_dist_safe = True
            self.front_speed_safe = True
        if self.back_car is not None:
            if self.back_dist < self.adjust_dist:
                self.back_dist_safe = False
            else:
                self.back_dist_safe = True
            if self.v < self.back_car.v:
                self.back_speed_safe = False
            else:
                self.back_speed_safe = True
        else:
            self.back_dist_safe = True
            self.back_speed_safe = True

    def change_lane(self):
        # if self.front_dist_safe and self.back_dist_safe and self.name != 'E' and self.y < 5:
        #     self.y += max(abs(self.vy), 5) * epsilon_t_x
        if self.name != 'E' and self.y < 5:
            self.y += max(abs(self.vy), 5) * epsilon_t_x

    def simple_safe_adjust(self):
        self.gen_safe_flag()
        # generate v
        # self.v += self.a * epsilon_t_v
        if not self.front_dist_safe or not self.back_dist_safe:
            if self.front_dist < self.back_dist and self.a > min_a:
                self.v -= epsilon_t_v
            elif self.front_dist > self.back_dist and self.a < max_a:
                self.v += epsilon_t_v
        else:
            if self.v > self.vInit:
                self.v -= epsilon_t_v
            if self.v < self.vInit:
                self.v += epsilon_t_v
        # generate x
        self.x += self.v * epsilon_t_x
        self.change_lane()

    def soft_safe_adjust(self):
        self.gen_safe_flag()
        if not self.front_dist_safe or not self.back_dist_safe:
            if self.front_dist < self.back_dist and self.a > min_a:
                self.a -= epsilon_t_a
            elif self.front_dist > self.back_dist and self.a < max_a:
                self.a += epsilon_t_a
        else:
            if self.v > self.vInit:
                self.a -= epsilon_t_a
            if self.v < self.vInit:
                self.v += epsilon_t_a
        # generate v
        self.v += self.a * epsilon_t_v
        # generate x
        self.x += self.v * epsilon_t_x
        self.change_lane()
        # generate v
        # generate a
        # if self.a < max_a and self.a > min_a:
        #     self.a += self.delta_a * epsilon_t_a
        # change lane
        # if self.front_dist_safe  and self.back_dist_safe and self.front_speed_safe and self.back_speed_safe and self.name != 'E' and self.y < 5:
        # self.change_lane()

    def simple_aim_adjust(self):
        self.gen_safe_flag()
        # generate v
        # self.v += self.a * epsilon_t_v
        if abs(self.x - self.aim_x) > 1:
            if self.x < (self.aim_x + self.xInit) / 2 - 5:
                if self.speed_flag == 1:
                    self.v += epsilon_t_v
                elif self.speed_flag == -1:
                    self.v -= epsilon_t_v
                # print("jiasu")
                # self.v = 20
            if self.x > ((self.xInit + self.aim_x) / 2 + 5):
                if self.speed_flag == 1:
                    self.v -= epsilon_t_v
                elif self.speed_flag == -1:
                    self.v += epsilon_t_v
                self.v -= epsilon_t_v
                # print("jiansu")
                # self.v = 10
        else:
            if self.v < self.vInit:
                self.v += epsilon_t_v
            if self.v > self.vInit:
                self.v -= epsilon_t_v
        # generate x
        self.x += self.v * epsilon_t_x
        if abs(self.x - self.aim_x) < 1:
            self.get_aim_x = True
        if self.get_aim:
            self.change_lane()

    # def adjust_simple(self):
    #     for car in cars:
    #         if car.x < car.aim_x:
    #             car.x += epsilon_t_x
    #
    def reset_position(self):
        self.x = self.xInit
        self.y = self.yInit
        self.v = self.vInit
        self.a = self.aInit
        self.x_sequence = []
        self.v_sequence = []
        self.a_sequence = []
        self.get_aim_x = False
        self.get_aim_v = False

    def refresh_sequence(self):
        self.x_sequence.append(self.x)
        self.v_sequence.append(self.v)
        self.a_sequence.append(self.a)

    def sort_key(car):
        return car.x
