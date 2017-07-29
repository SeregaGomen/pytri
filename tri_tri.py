#!/usr/bin/env python
# -*- coding: utf-8 -*-
####################################################################
#   Класс, реализующий триангуляцию плоских геометрических фигур,
#   описанных с помощью R-функций
####################################################################

# https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html#scipy.spatial.Delaunay
# https://stackoverflow.com/questions/26434726/return-surface-triangle-of-3d-scipy-spatial-delaunay
# https://docs.scipy.org/doc/scipy/reference/tutorial/spatial.html


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
        self.__parser__ = TParser()         # Парсер входного языка описания R-функции
        self.__progress__ = TProgress()     # Индикатор прогресса расчета

    @staticmethod
    # Определение расстояния между двумя точками
    def __length__(x1, x2):
        return ((x2[0] - x1[0])**2 + (x2[1] - x1[1])**2)**0.5

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
        while i < 100:
            if sign(self.__parser__.run(x1[0], x1[1])) != sign(self.__parser__.run(x[0], x[1])):
                x2 = [x[0], x[1]]
            else:
                x1 = [x[0], x[1]]
            x = [(x1[0] + x2[0])*0.5, (x1[1] + x2[1])*0.5]
            if self.__length__(x1, x2) < self.__eps__:
                break
            i += 1
            if i == 100:
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
#            for j in range(i + 1, len(self.fe)):
            for j in range(0, len(self.fe)):
                if i == j:
                    continue
                # Ищем ребра соседних треугольников, которые не являются общими
                for k in range(0, 3):
                    for m in range(0, 3):
                        if (self.fe[i][k] == self.fe[j][m] and
                                self.fe[i][k + 1 if k + 1 < 3 else 0] == self.fe[j][m + 1 if m + 1 < 3 else 0]) or \
                                (self.fe[i][k] == self.fe[j][m + 1 if m + 1 < 3 else 0] and
                                 self.fe[i][k + 1 if k + 1 < 3 else 0] == self.fe[j][m]):
                            v[k] = 1
            for j in range(0, 3):
                if v[j] == -1:
                    self.be.append([self.fe[i][j], self.fe[i][j + 1 if j + 1 < 3 else 0], -1, -1])
        # Поиск соседей к граничным элементам
        self.__progress__.set_process('Find boundary neighborhood...', 1, len(self.fe))
        for i in range(0, len(self.be)):
            self.__progress__.set_progress(i + 1)
            for j in range(0, len(self.be)):
                if i == j:
                    continue
                if self.be[i][0] == self.be[j][0] or self.be[i][0] == self.be[j][1] or \
                   self.be[i][1] == self.be[j][0] or self.be[i][1] == self.be[j][1]:
                    if self.be[i][2] < 0:
                        self.be[i][2] = j
                    else:
                        self.be[i][3] = j
        return True

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
            if self.__create_boundary__() is False:
                return False
        return True

    # Деление граничного сегмента пополам
    def __optimize_boundary_segment__(self, x1, x2):
        scale = 0.25   # Параметр, определяющий длину участка поиска нуля R-функции
        xc = [(x1[0] + x2[0])/2, (x1[1] + x2[1])/2]
        if x1[1] == x2[1]:
            # Сегмент параллелен оси абсцисс
            y1 = [xc[0], xc[1] + scale*self.__length__(x1, x2)]
            y2 = [xc[0], xc[1] - scale*self.__length__(x1, x2)]
            if sign(self.__parser__.run(y1[0], y1[1])) != sign(self.__parser__.run(y2[0], y2[1])):
                return True, self.__bisect__(y1, y2)
            return False, [0, 0]
        # Общий случай
        # Уравнение прямой, ортогональной граничному сегменту (y = kx + b), проходящей через точку xc
        k = (x2[0] - x1[0])/(x1[1] - x2[1])
        b = xc[1] - xc[0]*k
        # Координаты точек, лежащих на ортогогнальной прямой на заданном расстоянии от точки xc
        l = scale*self.__length__(x1, x2)
        d = (2*b*k - 2*k*xc[1] - 2*xc[0])**2 - 4*(k**2 + 1)*(b**2 - 2*b*xc[1] - l**2 + xc[0]**2 + xc[1]**2)
        if abs(d) < self.__eps__:
            d = 0
        px = [(-(2*b*k - 2*k*xc[1] - 2*xc[0]) - d**0.5)/2/(k**2 + 1),
              (-(2*b*k - 2*k*xc[1] - 2*xc[0]) + d**0.5)/2/(k**2 + 1)]
        py = [px[0]*k + b, px[1]*k + b]
        if sign(self.__parser__.run(px[0], py[0])) != sign(self.__parser__.run(px[1], py[1])):
            return True, self.__bisect__([px[0], py[0]], [px[1], py[1]])
        return False, [0, 0]

    # Оптимизация границы области
    def __optimize_boundary__(self):
        is_optimize = False
        # Оптимизация по критерию соотношения длин соседних граничных сегментов
        for i in range(0, len(self.be)):
            # Определяем длины соседних граничных сегментов
            len1 = self.__length__(self.x[self.be[i][0]], self.x[self.be[i][1]])
            len2 = self.__length__(self.x[self.be[self.be[i][2]][0]], self.x[self.be[self.be[i][2]][1]])
            len3 = self.__length__(self.x[self.be[self.be[i][3]][0]], self.x[self.be[self.be[i][3]][1]])
#            print(len1, len2, len3, len1/len2, len1/len3)
            if i == len(self.be) - 1:
                is_optimize = True
            if len1/len2 < 1.2 and len1/len3 < 1.2:
                continue
            is_optimize = True
            is_success, x = self.__optimize_boundary_segment__(self.x[self.be[i][0]], self.x[self.be[i][1]])
            if is_success is True:
                self.x.append(x)
        if is_optimize is True:
            # Перетриангуляция
            if self.__pre_triangulation__() is False:
                return False
            # Формирование границы области
            if self.__create_boundary__() is False:
                return False
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
            if self.__create_boundary__() is False:
                return False
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

        is_optimize = True
        # Поиск границы области
        if self.__find_boundary__(self.__min_x__, self.__max_x__, self.__max_step__) is False:
            return False
        # Предварительная триангуляция  
        if self.__pre_triangulation__() is False:
            return False
        # Формирование границы области
        if self.__create_boundary__() is False:
            return False
        # Оптимизация границы
        if is_optimize is True:
            if self.__remove_orphan_vertex__() is False:
                return False
            if self.__remove_degenerate_boundary__() is False:
                return False
            if self.__optimize_boundary__() is False:
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
