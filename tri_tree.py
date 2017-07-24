#!/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Реализация дерева разбора арифметических и логических выражений
###################################################################

import math
from abc import abstractmethod


# Абстрактный базовый класс значения выражения
class TNode:
    @abstractmethod
    def value(self):
        raise NotImplementedError('Method TNode.value is pure virtual')


# Класс, реализующий дерево разбора арифметических выражений
class TTree:
    def __init__(self, *args):
        if len(args) == 0:
            self.node = TRealNode(0)
        elif len(args) == 1:
            self.node = TRealNode(args[0])
        elif len(args) == 2:
            self.node = TUnaryNode(args[0], args[1])
        elif len(args) == 3:
            if type(args[0]) == str:
                self.node = TFunctionNode(args[0], args[1], args[2])
            else:
                self.node = TBinaryNode(args[0], args[1], args[2])
        elif len(args) == 7:
            self.node = TDomainNode(args[0], args[1], args[2], args[3], args[4], args[5], args[6])

    def __set__(self, instance, value):
        self.node.__val__ = value

    def value(self):
        return self.node.value()


# Вещественная переменная
class TRealNode(TNode):
    def __init__(self, val):
        self.__val__ = val

    def value(self):
        return self.__val__


# Унарная операция
class TUnaryNode(TNode):
    def __init__(self, op, val):
        self.__op__ = op
        self.__val__ = val

    def value(self):
        if self.__op__ == '-':
            return -self.__val__.value()
        elif self.__op__ == '+':
            return +self.__val__.value()
        elif self.__op__ == 'not':
            return -self.__val__.value()


# Бинарная операция
class TBinaryNode(TNode):
    def __init__(self, left, op, right):
        self.__left__ = left
        self.__op__ = op
        self.__right__ = right

    def value(self):
        if self.__op__ == '+':
            return self.__left__.value() + self.__right__.value()
        elif self.__op__ == '-':
            return self.__left__.value() - self.__right__.value()
        elif self.__op__ == '*':
            return self.__left__.value()*self.__right__.value()
        elif self.__op__ == '/':
            return self.__left__.value()/self.__right__.value()
        elif self.__op__ == '^':
            return math.pow(self.__left__.value(), self.__right__.value())
        elif self.__op__ == '=':
            return 1 if self.__left__.value() == self.__right__.value() else 0
        elif self.__op__ == '<>':
            return 0 if self.__left__.value() == self.__right__.value() else 1
        elif self.__op__ == '<':
            return 1 if self.__left__.value() < self.__right__.value() else 0
        elif self.__op__ == '<=':
            return 1 if self.__left__.value() <= self.__right__.value() else 0
        elif self.__op__ == '>':
            return 1 if self.__left__.value() > self.__right__.value() else 0
        elif self.__op__ == '>=':
            return 1 if self.__left__.value() >= self.__right__.value() else 0
        elif self.__op__ == 'or':
            return self.__left__.value() + self.__right__.value() + \
                   math.sqrt(self.__left__.value()**2 + self.__right__.value()**2)
        elif self.__op__ == 'and':
            return self.__left__.value() + self.__right__.value() - \
                   math.sqrt(self.__left__.value()**2 + self.__right__.value()**2)


# Вызов внешней функции
class TDomainNode(TNode):
    def __init__(self, code, x, y, z, vx, vy, vz):
        self.__code__ = code
        self.__x__ = x
        self.__y__ = y
        self.__z__ = z
        self.__vx__ = vx
        self.__vy__ = vy
        self.__vz__ = vz

    def value(self):
        self.__x__.__set__(self.__x__, self.__vx__.value())
        self.__y__.__set__(self.__y__, self.__vy__.value())
        self.__z__.__set__(self.__z__, self.__vz__.value())
        return self.__code__.value()


# Вызов встроенной функции
class TFunctionNode(TNode):
    def __init__(self, func, val1, val2):
        self.__func__ = func
        self.__val1__ = val1
        self.__val2__ = val2

    def value(self):
        if self.__func__ == 'abs':
            return math.fabs(self.__val1__.value())
        elif self.__func__ == 'sin':
            return math.sin(self.__val1__.value())
        elif self.__func__ == 'cos':
            return math.cos(self.__val1__.value())
        elif self.__func__ == 'tan':
            return math.tan(self.__val1__.value())
        elif self.__func__ == 'exp':
            return math.exp(self.__val1__.value())
        elif self.__func__ == 'asin':
            return math.asin(self.__val1__.value())
        elif self.__func__ == 'acos':
            return math.acos(self.__val1__.value())
        elif self.__func__ == 'atan':
            return math.atan(self.__val1__.value())
        elif self.__func__ == 'sinh':
            return math.sinh(self.__val1__.value())
        elif self.__func__ == 'cosh':
            return math.cosh(self.__val1__.value())
        elif self.__func__ == 'atan2':
            return math.atan2(self.__val1__.value(), self.__val2__.value())
