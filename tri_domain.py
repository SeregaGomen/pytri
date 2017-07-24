#!/usr/bin/env python
# -*- coding: utf-8 -*-
############################################################
#  Класс, описывающий геометрическую область или ее часть
############################################################

from tri_tree import TTree
from tri_error import TException


class TDomain:
    def __init__(self):
        self.name = ''              # Название геометрического объекта
        self.arguments = {}         # Таблица аргументов (координат)
        self.variables = {}         # Таблица переменных
        self.result = TTree()       # Дерево разбора функционального выражения, описывающего object

    def set_name(self, name):
        self.name = name

    def add_argument(self, name):
        if name in self.arguments:
            raise TException('redefinition_err')
        self.arguments.setdefault(name, TTree())

    def add_variable(self, name, value=TTree()):
        if name in self.variables:
            raise TException('redefinition_err')
        self.variables.setdefault(name, value)

    def set_variable(self, name, value):
        if name not in self.variables:
            raise TException('undef_err')
        self.variables[name] = value

    def set_result(self, value):
        self.result = value