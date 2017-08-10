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
        self.display.bind("<MouseWheel>", self.repaint)

    def resize(self, event):
        self.paint(event.width, event.height)

    def repaint(self, event):
        self.__scale__ = self.__scale__*1.1 if event.delta > 0 else self.__scale__/1.1
        w, h = self.display.winfo_width(), self.display.winfo_height()
        self.paint(w, h)

    def paint(self, width, height):
        self.display.delete('LINE')
        self.display.delete('OVAL')

        w = width*self.__scale__
        h = height*self.__scale__
        dx = [self.__x_max__[0] - self.__x_min__[0], self.__x_max__[1] - self.__x_min__[1]]
        s_x = [(self.__x_max__[0] + self.__x_min__[0])/2, (self.__x_max__[1] + self.__x_min__[1])/2]

        # Изображение узлов
        if self.__show_vertex__:
            for i in range(0, len(self.__x__)):
                x = [(self.__x__[i][0] - s_x[0])*w/dx[0]*0.9 + width/2,
                     (self.__x__[i][1] - s_x[1])*h/dx[1]*0.9 + height/2]
                self.display.create_oval([x[0] - 2, x[1] - 2], [x[0] + 2, x[1] + 2], fill='red', tags='OVAL')

        # Изображение КЭ
        if self.__show_fe__:
            for i in range(0, len(self.__fe__)):
                x = []
                for j in range(0, 3):
                    x.append([(self.__x__[self.__fe__[i][j]][0] - s_x[0])*w/dx[0]*0.9 + width/2,
                              (self.__x__[self.__fe__[i][j]][1] - s_x[1])*h/dx[1]*0.9 + height/2])
                self.display.create_line([x[0][0], x[0][1]], [x[1][0], x[1][1]], tags='LINE')
                self.display.create_line([x[1][0], x[1][1]], [x[2][0], x[2][1]], tags='LINE')
                self.display.create_line([x[2][0], x[2][1]], [x[0][0], x[0][1]], tags='LINE')

        # Изображение границы
        if self.__show_be__:
            for i in range(0, len(self.__be__)):
                x = []
                for j in range(0, 2):
                    x.append([(self.__x__[self.__be__[i][j]][0] - s_x[0])*w/dx[0]*0.9 + width/2,
                              (self.__x__[self.__be__[i][j]][1] - s_x[1])*h/dx[1]*0.9 + height/2])
                self.display.create_line([x[0][0], x[0][1]], [x[1][0], x[1][1]], fill='blue', tags='LINE')

        #-----------------------------------
        scale = 1
        for i in range(0, len(self.__be__)):
            x1 = self.__x__[self.__be__[i][0]]
            x2 = self.__x__[self.__be__[i][1]]
            length = ((x1[0] - x2[0])**2 + (x1[1] - x2[1])**2)**0.5
            xc = [(x1[0] + x2[0])/2, (x1[1] + x2[1])/2]
            if x1[1] == x2[1]:
                # Сегмент параллелен оси абсцисс
                y1 = [xc[0], xc[1] + scale*length]
                y2 = [xc[0], xc[1] - scale*length]
                self.display.create_line([(y1[0] - s_x[0])*w/dx[0]*0.9 + width/2, (y1[1] - s_x[1])*h/dx[1]*0.9 + height/2], [(y2[0] - s_x[0])*w/dx[0]*0.9 + width/2, (y2[1] - s_x[1])*h/dx[1]*0.9 + height/2], fill='blue', tags='LINE')
            else:
                # Общий случай
                # Уравнение прямой, ортогональной граничному сегменту (y = kx + b), проходящей через точку xc
                k = (x2[0] - x1[0])/(x1[1] - x2[1])
                b = xc[1] - xc[0]*k
                # Координаты точек, лежащих на ортогогнальной прямой на заданном расстоянии от точки xc
                l = scale*length
                d = (2*b*k - 2*k*xc[1] - 2*xc[0])**2 - 4*(k**2 + 1)*(b**2 - 2*b*xc[1] - l**2 + xc[0]**2 + xc[1]**2)
                px = [(-(2*b*k - 2*k*xc[1] - 2*xc[0]) - d**0.5)/2/(k**2 + 1),
                      (-(2*b*k - 2*k*xc[1] - 2*xc[0]) + d**0.5)/2/(k**2 + 1)]
                py = [px[0]*k + b, px[1]*k + b]
                self.display.create_line([(px[0] - s_x[0])*w/dx[0]*0.9 + width/2, (py[0] - s_x[1])*h/dx[1]*0.9 + height/2], [(px[1] - s_x[0])*w/dx[0]*0.9 + width/2, (py[1] - s_x[1])*h/dx[1]*0.9 + height/2], fill='blue', tags='LINE')
        self.display.create_oval([(-0.5 - s_x[0])*w/dx[0]*0.9 + width/2,(-0.5 - s_x[1])*h/dx[1]*0.9 + height/2],[(0.5 - s_x[0])*w/dx[0]*0.9 + width/2,(0.5 - s_x[1])*h/dx[1]*0.9 + height/2], tags='OVAL')
        self.display.create_oval([(-0.4 - s_x[0])*w/dx[0]*0.9 + width/2,(-1 - s_x[1])*h/dx[1]*0.9 + height/2],[(1.6 - s_x[0])*w/dx[0]*0.9 + width/2,(1 - s_x[1])*h/dx[1]*0.9 + height/2], tags='OVAL')