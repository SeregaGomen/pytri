#!/usr/bin/env python
# -*- coding: utf-8 -*-
####################################################################
#               Класс, визуализирующий триангуляцию
####################################################################

from tkinter import *


class TTriView(Frame):
    def __init__(self, root, name, x, fe, be, show_vertex=False, show_fe=False, show_be=True):
        Frame.__init__(self, root)
        root.title('R-function - ' + name)

        self.__scale__ = 1
        self.__w__ = 600
        self.__h__ = 600
        self.__x__ = x
        self.__fe__ = fe
        self.__be__ = be
        self.__show_vertex__ = show_vertex
        self.__show_fe__ = show_fe
        self.__show_be__ = show_be

        self.__x_min__ = [min(x[i][0] for i in range(0, len(x))), min(x[i][1] for i in range(0, len(x)))]
        self.__x_max__ = [max(x[i][0] for i in range(0, len(x))), max(x[i][1] for i in range(0, len(x)))]
        size = 600

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.display = Canvas(self, width=size, height=size, bd=0, highlightthickness=0)
        self.display.grid(row=0, sticky=W+E+N+S)
        self.pack(fill=BOTH, expand=1)
        self.bind("<Configure>", self.resize)
#        self.display.bind("<Double-1>", self.repaint)
        self.display.bind("<MouseWheel >", self.repaint, "delta")
        self.paint()

    def resize(self, event):
        self.__w__ = event.width
        self.__h__ = event.height
        self.paint()

    def repaint(self, event):
        if event.delta > 0:
            self.__scale__ *= 1.1
        else:
            self.__scale__ /= 1.1
        self.paint()

    def paint(self):
        self.display.delete('LINE')
        self.display.delete('OVAL')

        dx = [self.__x_max__[0] - self.__x_min__[0], self.__x_max__[1] - self.__x_min__[1]]
        s_x = [(self.__x_max__[0] + self.__x_min__[0])/2, (self.__x_max__[1] + self.__x_min__[1])/2]

        # Изображение узлов
        if self.__show_vertex__:
            for i in range(0, len(self.__x__)):
                x = [(self.__x__[i][0] - s_x[0])*self.__w__*self.__scale__/dx[0]*0.9 + self.__w__*self.__scale__/2,
                     (self.__x__[i][1] - s_x[1])*self.__h__*self.__scale__/dx[1]*0.9 + self.__h__*self.__scale__/2]
                self.display.create_oval([x[0] - 2, x[1] - 2], [x[0] + 2, x[1] + 2], fill='red', tags='OVAL')

        # Изображение КЭ
        if self.__show_fe__:
            for i in range(0, len(self.__fe__)):
                x = []
                for j in range(0, 3):
                    x.append([(self.__x__[self.__fe__[i][j]][0] - s_x[0])*self.__w__*self.__scale__/dx[0]*0.9 + self.__w__*self.__scale__/2,
                              (self.__x__[self.__fe__[i][j]][1] - s_x[1])*self.__h__*self.__scale__/dx[1]*0.9 + self.__h__*self.__scale__/2])
                self.display.create_line([x[0][0], x[0][1]], [x[1][0], x[1][1]], tags='LINE')
                self.display.create_line([x[1][0], x[1][1]], [x[2][0], x[2][1]], tags='LINE')
                self.display.create_line([x[2][0], x[2][1]], [x[0][0], x[0][1]], tags='LINE')

        # Изображение границы
        if self.__show_be__:
            for i in range(0, len(self.__be__)):
                x = []
                for j in range(0, 2):
                    x.append([(self.__x__[self.__be__[i][j]][0] - s_x[0])*self.__w__*self.__scale__/dx[0]*0.9 + self.__w__*self.__scale__/2,
                              (self.__x__[self.__be__[i][j]][1] - s_x[1])*self.__h__*self.__scale__/dx[1]*0.9 + self.__h__*self.__scale__/2])
                self.display.create_line([x[0][0], x[0][1]], [x[1][0], x[1][1]], fill='blue', tags='LINE')
