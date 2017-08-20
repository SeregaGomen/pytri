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

        self.__x__ = x
        self.__fe__ = fe
        self.__be__ = be
        self.__show_vertex__ = show_vertex
        self.__show_fe__ = show_fe
        self.__show_be__ = show_be
        self.__scale__ = 1
        self.__shift_x__ = 0
        self.__shift_y__ = 0

        self.__x_min__ = [min(x[i][0] for i in range(0, len(x))), min(x[i][1] for i in range(0, len(x)))]
        self.__x_max__ = [max(x[i][0] for i in range(0, len(x))), max(x[i][1] for i in range(0, len(x)))]
        size = 600

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.display = Canvas(self, width=size, height=size, bd=0, highlightthickness=0)
        self.display.grid(row=0, sticky=W+E+N+S)
        self.pack(fill=BOTH, expand=1)
        self.bind('<Configure>', self.resize)
        self.display.bind('<MouseWheel>', self.zoom)
        self.display.bind('<Button-3>', self.shift)
        self.display.bind_all('<KeyPress>', self.shift)

    def resize(self, event):
        self.paint(event.width, event.height)

    def zoom(self, event):
        self.__scale__ = self.__scale__*1.1 if event.delta > 0 else self.__scale__/1.1
        w, h = self.display.winfo_width(), self.display.winfo_height()
        self.paint(w, h)

    def shift(self, event):
        w, h = self.display.winfo_width(), self.display.winfo_height()
        if event.keysym == 'Right':
            self.__shift_x__ -= (self.__x_max__[0] - self.__x_min__[0])/100
        elif event.keysym == 'Left':
            self.__shift_x__ += (self.__x_max__[0] - self.__x_min__[0])/100
        elif event.keysym == 'Up':
            self.__shift_y__ += (self.__x_max__[1] - self.__x_min__[1])/100
        elif event.keysym == 'Down':
            self.__shift_y__ -= (self.__x_max__[1] - self.__x_min__[1])/100
        else:
            return
        self.paint(w, h)

    def paint(self, width, height):
        self.display.delete('LINE')
        self.display.delete('OVAL')

        w = width*self.__scale__
        h = height*self.__scale__
        dx = [self.__x_max__[0] - self.__x_min__[0], self.__x_max__[1] - self.__x_min__[1]]
        s_x = [self.__shift_x__ + (self.__x_max__[0] + self.__x_min__[0])/2,
               self.__shift_y__ + (self.__x_max__[1] + self.__x_min__[1])/2]

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

        #-----------------
        self.display.create_oval([(-1.0 - s_x[0])*w/dx[0]*0.9 + width/2,(-1.0 - s_x[1])*h/dx[1]*0.9 + height/2],[(1.0 - s_x[0])*w/dx[0]*0.9 + width/2,(1.0 - s_x[1])*h/dx[1]*0.9 + height/2], tags='OVAL')
        self.display.create_oval([(-0.8 - s_x[0])*w/dx[0]*0.9 + width/2,(-0.8 - s_x[1])*h/dx[1]*0.9 + height/2],[(0.8 - s_x[0])*w/dx[0]*0.9 + width/2,(0.8 - s_x[1])*h/dx[1]*0.9 + height/2], tags='OVAL')