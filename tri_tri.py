#!/usr/bin/env python
# -*- coding: utf-8 -*-
####################################################################
#   Класс, реализующий триангуляцию плоских геометрических фигур,
#   описанных с помощью R-функций
####################################################################

# https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html#scipy.spatial.Delaunay
# https://stackoverflow.com/questions/26434726/return-surface-triangle-of-3d-scipy-spatial-delaunay
# https://docs.scipy.org/doc/scipy/reference/tutorial/spatial.html


from math import acos
from math import ceil
from numpy import sign
from tri_parser import TParser
from tri_error import TException
from tri_progress import TProgress
from scipy.spatial import Delaunay
import numpy as np


class TTri:
    def __init__(self):
        self.x = []                         # Координаты узлов
        self.be = []                        # Граничные элементы
        self.fe = []                        # Конечные элементы
        self.__file_name__ = ''             # Имя файла, содержащего описание R-функции
        self.__eps__ = 1.0E-10              # Точность поиска корней
        self.__min_x__ = [-10, -10]         # Габариты области поиска границы
        self.__max_x__ = [10, 10]           # ...
        self.__max_step__ = 100             # Максимальное количество итераций для поиска границы
        self.__max_angle__ = 15             # Максимальный угол между соседними граничными сегментами
        self.__max_ratio__ = 2              # Максимальное соотношение длин граничных сегментов
        self.__parser__ = TParser()         # Парсер входного языка описания R-функции
        self.__progress__ = TProgress()     # Индикатор прогресса расчета
        self.__length_optimize__ = True     # Оптимизация по критерию соотношения длин соседних граничных сегментов
        self.__angle_optimize__ = True      # Оптимизация по критерию угла между соседними граничными сегментами

    @staticmethod
    # Определение расстояния между двумя точками
    def __length__(x1, x2):
        return ((x2[0] - x1[0])**2 + (x2[1] - x1[1])**2)**0.5

    # Определение принадлежности точки p i-ому треугольнику
    # http://www.cyberforum.ru/algorithms/thread144722.html
    def __check_point_in_triangle__(self, p, i):
        x = [p[0], self.x[self.fe[i][0]][0], self.x[self.fe[i][1]][0], self.x[self.fe[i][2]][0]]
        y = [p[1], self.x[self.fe[i][0]][1], self.x[self.fe[i][1]][1], self.x[self.fe[i][2]][1]]

        a = (x[1] - x[0])*(y[2] - y[1]) - (x[2] - x[1])*(y[1] - y[0])
        b = (x[2] - x[0])*(y[3] - y[2]) - (x[3] - x[2])*(y[2] - y[0])
        c = (x[3] - x[0])*(y[1] - y[3]) - (x[1] - x[3])*(y[3] - y[0])
        if (a >= 0 and b >= 0 and c >= 0) or (a <= 0 and b <= 0 and c <= 0):
            return True
        return False

    # Поиск координат отрезка, ортогонального заданному граничному сегменту
    def __get_orthogonal__(self, x1, x2, scale):
        xc = [(x1[0] + x2[0])/2, (x1[1] + x2[1])/2]
        if x1[1] == x2[1]:
            # Сегмент параллелен оси абсцисс
            p1 = [xc[0], xc[1] + scale*self.__length__(x1, x2)]
            p2 = [xc[0], xc[1] - scale*self.__length__(x1, x2)]
        else:
            # Уравнение прямой, ортогональной граничному сегменту (y = kx + b), проходящей через точку xc
            k = (x2[0] - x1[0])/(x1[1] - x2[1])
            b = xc[1] - xc[0]*k
            # Координаты точек, лежащих на ортогогнальной прямой на заданном расстоянии от точки xc
            l = scale*self.__length__(x1, x2)
            d = (2*b*k - 2*k*xc[1] - 2*xc[0])**2 - 4*(k**2 + 1)*(b**2 - 2*b*xc[1] - l**2 + xc[0]**2 + xc[1]**2)
            r1 = (-(2*b*k - 2*k*xc[1] - 2*xc[0]) - d**0.5)/2/(k**2 + 1)
            r2 = (-(2*b*k - 2*k*xc[1] - 2*xc[0]) + d**0.5)/2/(k**2 + 1)
            p1 = [r1, r1*k + b]
            p2 = [r2, r2*k + b]
        return p1, p2

    # Определение угла между соседними граничными сегментами
    def __angle__(self, i, j):
        # Координаты направляющих векторов i и j граничных сегментов
        vi = [self.x[self.be[i][0]][0] - self.x[self.be[i][1]][0], self.x[self.be[i][0]][1] - self.x[self.be[i][1]][1]]
        vj = [self.x[self.be[j][0]][0] - self.x[self.be[j][1]][0], self.x[self.be[j][0]][1] - self.x[self.be[j][1]][1]]
        val = abs(vi[0]*vj[0] + vi[1]*vj[1])/((vi[0]**2 + vi[1]**2)**0.5)/((vj[0]**2 + vj[1]**2)**0.5)
        if val > 1.0:
            val = 1.0
        return 180/3.14*acos(val)

    # Проверка принадлежности треугольника исходной области
    def __check_triangle__(self, i, j, k):
        xc = [(self.x[i][0] + self.x[j][0] + self.x[k][0])/3, (self.x[i][1] + self.x[j][1] + self.x[k][1])/3]
        if self.__parser__.run(xc[0], xc[1]) >= 0:
            return True
        return False

    # Реализация метода половинного деления
    def __bisect__(self, x1, x2):
        i = 0
        x = [(x1[0] + x2[0])*0.5, (x1[1] + x2[1])*0.5]
        while i < self.__max_step__:
            if sign(self.__parser__.run(x1[0], x1[1])) != sign(self.__parser__.run(x[0], x[1])):
                x2 = [x[0], x[1]]
            else:
                x1 = [x[0], x[1]]
            x = [(x1[0] + x2[0])*0.5, (x1[1] + x2[1])*0.5]
            if self.__length__(x1, x2) < self.__eps__:
                break
            i += 1
            if i == self.__max_step__:
                print('Warning: ', x1[0], ',', x1[1], ' ', x2[0], ',', x2[1])
        return [(x1[0] + x2[0])*0.5, (x1[1] + x2[1])*0.5]

    # Процедура поиска границы области
    def __find_boundary__(self, min_x, max_x, max_step):
        try:
            h_x = (max_x[0] - min_x[0])/max_step
            h_y = (max_x[1] - min_x[1])/max_step

            self.__progress__.set_process('Search of the region boundary...', 1, max_step)
            for i in range(0, max_step):
                self.__progress__.set_progress(i + 1)
                x = min_x[0] + i*h_x
                for j in range(0, max_step - 1):
                    y1 = min_x[1] + j*h_y
                    y2 = min_x[1] + (j + 1)*h_y
                    if sign(self.__parser__.run(x, y1)) != sign(self.__parser__.run(x, y2)):
                        # На участке между точками (x,y1) и (x,y2) лежит граница области
                        px = self.__bisect__([x, y1], [x, y2])
                        self.x.append(px)
            return True
        except TException as err:
            err.print_error()
            return False

    # Предварительная триангуляция
    def __pre_triangulation__(self):
        self.fe = []
        # Построение триангуляции
        self.__progress__.set_process('Create pretriangulation...', 1, 100)
        try:
            tri = Delaunay(np.array([np.array([self.x[i][0] for i in range(0, len(self.x))]),
                                     np.array([self.x[i][1] for i in range(0, len(self.x))])]).T)
        except ValueError as err:
            print(err)
            return False
        for v in tri.simplices:
            if self.__check_triangle__(v[0], v[1], v[2]) is True:
                self.fe.append([v[0], v[1], v[2]])
        self.__progress__.set_progress(100)
        return True

    # Построение границы области
    def __create_boundary__(self):
        self.be = []
        self.__progress__.set_process('Create boundary...', 1, len(self.fe))
        for i in range(0, len(self.fe)):
            self.__progress__.set_progress(i + 1)
            v = [-1, -1, -1]
            # Находим треугольники, содержащие граничные ребра
            for j in range(0, len(self.fe)):
                if i != j:
                    # Ищем ребра соседних треугольников, которые не являются общими
                    for k in range(0, 3):
                        for m in range(0, 3):
                            if (self.fe[i][k] == self.fe[j][m] and
                                    self.fe[i][k + 1 if k + 1 < 3 else 0] == self.fe[j][m + 1 if m + 1 < 3 else 0]) or \
                                    (self.fe[i][k] == self.fe[j][m + 1 if m + 1 < 3 else 0] and
                                     self.fe[i][k + 1 if k + 1 < 3 else 0] == self.fe[j][m]):
                                v[k] = j
            for j in range(0, 3):
                if v[j] == -1:
                    length = self.__length__(self.x[self.fe[i][j]], self.x[self.fe[i][j + 1 if j + 1 < 3 else 0]])
                    self.be.append([self.fe[i][j], self.fe[i][j + 1 if j + 1 < 3 else 0], -1, -1, i, length])
            self.fe[i] += v
        # Поиск соседей к граничным элементам
        self.__progress__.set_process('Find boundary neighborhood...', 1, len(self.be))
        for i in range(0, len(self.be)):
            self.__progress__.set_progress(i + 1)
            for j in range(0, len(self.be)):
                if i != j:
                    if self.be[i][0] == self.be[j][0] or self.be[i][0] == self.be[j][1] or \
                       self.be[i][1] == self.be[j][0] or self.be[i][1] == self.be[j][1]:
                        if self.be[i][2] < 0:
                            self.be[i][2] = j
                        else:
                            self.be[i][3] = j

    # Удаление вырожденных граничных сегментов
    def __remove_degenerate_boundary__(self):
        del_index = []
        # Удаление вырожденных участков границы
        self.__progress__.set_process('Find degenerate boundary segment...', 1, len(self.fe))
        for i in range(0, len(self.be)):
            self.__progress__.set_progress(i + 1)
            if self.__length__(self.x[self.be[i][0]], self.x[self.be[i][1]]) < self.__eps__:
                del_index.append(self.be[i][1])
        if len(del_index):
            del_index.sort()
            for i in reversed(range(0, len(del_index))):
                self.x.pop(del_index[i])
            # Перетриангуляция
            if self.__pre_triangulation__() is False:
                return False
            # Формирование границы области
            self.__create_boundary__()
        return True

    # Деление граничного сегмента по критерию длины
    def __optimize_boundary_segment_length__(self, index, count=2):
        scale = 0.25   # Параметр, определяющий длину отрезка поиска нуля R-функции
        h = [(self.x[self.be[index][1]][0] - self.x[self.be[index][0]][0])/count,
             (self.x[self.be[index][1]][1] - self.x[self.be[index][0]][1])/count]
        for i in range(0, count):
            x1 = [self.x[self.be[index][0]][0] + i*h[0], self.x[self.be[index][0]][1] + i*h[1]]
            x2 = [self.x[self.be[index][0]][0] + (i + 1)*h[0], self.x[self.be[index][0]][1] + (i + 1)*h[1]]
            p1, p2 = self.__get_orthogonal__(x1, x2, scale)
            if sign(self.__parser__.run(p1[0], p1[1])) != sign(self.__parser__.run(p2[0], p2[1])):
                self.x.append(self.__bisect__(p1, p2))

    # Деление граничного сегмента по критерию угла
    def __optimize_boundary_segment_angle__(self, index, count=2.0):
        scale = 0.05
        h = [(self.x[self.be[index][1]][0] - self.x[self.be[index][0]][0])/count,
             (self.x[self.be[index][1]][1] - self.x[self.be[index][0]][1])/count]
        for i in range(0, int(count)):
            x1 = [self.x[self.be[index][0]][0] + i*h[0], self.x[self.be[index][0]][1] + i*h[1]]
            x2 = [self.x[self.be[index][0]][0] + (i + 1)*h[0], self.x[self.be[index][0]][1] + (i + 1)*h[1]]
#            if x1[0] == x2[0]:
#                print(x1, x2)
            p1, p2 = self.__get_orthogonal__(x1, x2, scale)
            xc = [(p1[0] + p2[0])/2, (p1[1] + p2[1])/2]
            if self.__check_point_in_triangle__(p1, self.be[index][4]):
                p1 = xc
                p2 = [p1[0] + 1000*(p2[0] - p1[0]), p1[1] + 1000*(p2[1] - p1[1])]
            else:
                p2 = xc
                p1 = [p2[0] + 1000*(p1[0] - p2[0]), p2[1] + 1000*(p1[1] - p2[1])]
            if sign(self.__parser__.run(p1[0], p1[1])) != sign(self.__parser__.run(p2[0], p2[1])):
                self.x.append(self.__bisect__(p1, p2))

    # Оптимизация границы области по критерию соотношения длин соседних сегментов
    def __optimize_boundary_for_length__(self):
        size_x = len(self.x)
        # Определяем среднюю длину граничного сегмента
        avg_len = 0
        for i in range(0, len(self.be)):
            avg_len += self.be[i][5]
        avg_len /= len(self.be)
        # Дробим на части граничные сегменты, длина которых выше средней
        for i in range(0, len(self.be)):
            if self.be[i][5]/avg_len > self.__max_ratio__:
                self.__optimize_boundary_segment_length__(i, int(ceil(self.be[i][5]/avg_len)))
        if size_x != len(self.x):
            # Перетриангуляция
            if self.__pre_triangulation__() is False:
                return False
            # Формирование границы области
            self.__create_boundary__()
        return True

    # Оптимизация границы области по критерию угла между соседними сегментами
    @property
    def __optimize_boundary_for_angle__(self):
        size_x = len(self.x)
        for i in range(0, len(self.be)):
            # Определяем углы между соседними граничными сегментами
            angle = max(self.__angle__(i, self.be[i][2]), self.__angle__(i, self.be[i][3]))
            if angle > self.__max_angle__:
                count = ceil(angle/self.__max_angle__)
                self.__optimize_boundary_segment_angle__(i, count)
        if size_x != len(self.x):
            # Перетриангуляция
            if self.__pre_triangulation__() is False:
                return False
            # Формирование границы области
            self.__create_boundary__()
        return True

    # Удаление "висячих" узлов
    def __remove_orphan_vertex__(self):
        attr = np.zeros(len(self.x))
        self.__progress__.set_process('Find orphan vertex...', 1, len(self.fe))
        for i in range(0, len(self.be)):
            self.__progress__.set_progress(i + 1)
            attr[self.be[i][0]] = attr[self.be[i][1]] = 1
        is_orphan = False
        for i in reversed(range(0, len(attr))):
            if (attr[i]) == 0:
                self.x.pop(i)
                is_orphan = True
        if is_orphan is True:
            # Перетриангуляция
            if self.__pre_triangulation__() is False:
                return False
            # Формирование границы области
            self.__create_boundary__()
        return True

    # Запуск процедуры построения триангуляции
    def start(self):
        try:
            file = open(self.__file_name__)
            code = file.readlines()
            file.close()
        except IOError as err:
            print('\033[1;31m%s\033[1;m' % err)
            return False

        try:
            self.__parser__.set_code(code)
        except TException as err:
            err.print_error()
            return False

        # Поиск границы области
        if self.__find_boundary__(self.__min_x__, self.__max_x__, self.__max_step__) is False:
            return False
        # Предварительная триангуляция
        if self.__pre_triangulation__() is False:
            return False
        # Формирование границы области
        self.__create_boundary__()
        # Удаление "висячих" узлов
        if self.__remove_orphan_vertex__() is False:
            return False
        # Удаление вырожденых граничных сегментов
        if self.__remove_degenerate_boundary__() is False:
            return False
        # Оптимизация по критерию длины сегмента
        if self.__length_optimize__ is True:
            if self.__optimize_boundary_for_length__() is False:
                return False
        for i in range(0, 5):
            # Оптимизация по критерию угла между соседними грничными сегментами
            if self.__angle_optimize__ is True:
                if self.__optimize_boundary_for_angle__ is False:
                    return False
        return True

    # Задание имени файла, содержащего описание R-функции на входном языке
    def set_file_name(self, file_name):
        self.__file_name__ = file_name

    # Здание точности вычислений
    def set_eps(self, eps):
        self.__eps__ = eps

    # Здание количества шагов
    def set_step(self, step):
        self.__max_step__ = step

    # Здание области поиска
    def set_region(self, min_x, max_x):
        self.__min_x__ = min_x
        self.__max_x__ = max_x

    # Здание максимального соотношения длин соседних сегментов
    def set_ratio(self, ratio):
        self.__max_ratio__ = ratio

    # Здание максимального соотношения уголов между соседними сегментами
    def set_angle(self, angle):
        self.__max_angle__ = angle

    # Здание оптимизвции по углу между соседними сегментами
    def set_angle_optimize(self, is_angle):
        self.__angle_optimize__ = is_angle

    # Здание оптимизвции по соотношению длин соседних сегментов
    def set_length_optimize(self, is_length):
        self.__length_optimize__ = is_length
