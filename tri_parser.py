# !/usr/bin/env python
# !/usr/bin/env python
# -*- coding: utf-8 -*-
###################################################################
# Реализация интерпретатора арифметических и логических выражений
###################################################################

from tri_error import TException
from tri_tree import TTree
from tri_domain import TDomain

# Типы лексем
tokens = [
    'delimiter',
    'digit',
    'function',
    'variable',
    'end',
    'eol'
]

# Функции
functions = [
    'sin',
    'cos',
    'tan',
    'exp',
    'asin',
    'acos',
    'atan',
    'atan2',
    'sinh',
    'cosh',
    'tanh',
    'abs'
]

# Логические операции
booleans = [
    'not',
    'and',
    'or'
]

# Арифметические операции
operations = [
    '+',
    '-',
    '*',
    '/',
    '^',
    '>',
    '>=',
    '=',
    '<>',
    '<',
    '<='
]

# Операторы
statements = [
    'domain',
    'return',
    'begin',
    'end'
]


# Класс, реализующий разбор и выполнение арифметических и логических выражений
class TParser:
    def __init__(self):
        self.is_begin_block = False
        self.error = self.code = self.token = self.token_type = self.current_block_name = ''
        self.domain_list = []

    # Задание кода для обработки (массив строк преобразуется в одну строку)
    def set_code(self, c):
        for i in range(0, len(c)):
            self.code += c[i]
        self.compile()

    def is_error(self):
        return False if self.error == '' else True

    # Обработка арифметического выражения
    def get_exp(self, result):
        self.get_token()
        if len(self.token) == 0:
            self.say_error('syntax_err')
        result = self.token_or(result)
        return result

    # Обработка операции OR
    def token_or(self, result):
        result = self.token_and(result)
        hold = TTree()
        while not self.token == 'end' and self.token == 'or':
            self.get_token()
            hold = self.token_and(hold)
            result = TTree(result, 'or', hold)
        return result

    # Обработка операции AND
    def token_and(self, result):
        result = self.token_not(result)
        hold = TTree()
        while not self.token == 'end' and self.token == 'and':
            self.get_token()
            hold = self.token_not(hold)
            result = TTree(result, 'and', hold)
        return result

    # Обработка операции NOT
    def token_not(self, result):
        sign = self.token
        if (self.token_type == 'delimiter') and sign == 'not':
            self.get_token()
        result = self.token_add(result)
        if sign == 'not':
            result = TTree(sign, result)
        return result

    # Обработка операции +
    def token_add(self, result):
        result = self.token_mul(result)
        hold = TTree()
        while not self.token == 'end' and (self.token == '+' or self.token == '-' or self.token == '>' or
                                           self.token == '<' or self.token == '>=' or self.token == '<=' or
                                           self.token == '<>' or self.token == '='):
            sign = self.token
            self.get_token()
            hold = self.token_mul(hold)
            result = TTree(result, sign, hold)
        return result

    # Обработка операции *
    def token_mul(self, result):
        result = self.token_pow(result)
        hold = TTree()
        while self.token != 'end' and (self.token == '*' or self.token == '/'):
            sign = self.token
            self.get_token()
            hold = self.token_pow(hold)
            result = TTree(result, sign, hold)
        return result

    # Обработка операции возведения в степень
    def token_pow(self, result):
        result = self.token_un(result)
        hold = TTree()
        while self.token != 'end' and (self.token == '^'):
            self.get_token()
            hold = self.token_brackets(hold)
            result = TTree(result, '^', hold)
        return result

    # Обработка унарной операции +/-
    def token_un(self, result):
        sign = self.token
        if (self.token_type == 'delimiter') and (sign == '+' or sign == '-'):
            self.get_token()
        result = self.token_brackets(result)
        if sign == '+' or sign == '-':
            result = TTree(sign, result)
        return result

    # Обработка скобок
    def token_brackets(self, result):
        if self.token != 'end' and self.token == '(' and self.token_type == 'delimiter':
            self.get_token()
            result = self.token_or(result)
            if self.token != ')':
                self.say_error('brackets_err')
            self.get_token()
        else:
            result = self.token_prim(result)
        return result

    # Проверка наличия идентификатора в таблице областей (подобластей)
    def find_domain_name(self, name):
        ret = -1
        for i in range(0, len(self.domain_list)):
            if name == self.domain_list[i].name:
                ret = i
                break
        return ret

    # Обработка примитива (имени переменной или функции)
    def token_prim(self, result):
        if self.token_type == 'digit':
            val = float(self.token)
            result = TTree(val)
        elif self.token_type == 'function':
            result = self.token_func(result)
        elif self.token_type == 'variable':
            if self.token in self.domain_list[len(self.domain_list) - 1].arguments:
                result = self.domain_list[len(self.domain_list) - 1].arguments[self.token]
            elif self.token in self.domain_list[len(self.domain_list) - 1].variables:
                result = self.domain_list[len(self.domain_list) - 1].variables[self.token]
            else:
                self.say_error('undef_err')
        else:
            self.say_error('syntax_err')
        self.get_token()
        return result

    # Обработка функции
    def token_func(self, result):
        fun_token = self.token
        hold = TTree()
        hold1 = TTree()
        self.get_token()
        if self.token == 'end' or self.token != '(':
            self.say_error('syntax_err')
        self.get_token()
        result = self.token_add(result)
        i = self.find_domain_name(fun_token)
        if i != -1:
            # Обработка вызова функции, описывающей подобласть
            if self.token != ',':
                self.say_error('syntax_err')
            self.get_token()
            hold = self.token_add(hold)  # Аргумент y
            if self.token == ',':
                self.get_token()
                hold1 = self.token_add(hold1)  # Аргумент z
            if self.token != ')':
                self.say_error('syntax_err')
            arg_list = list(self.domain_list[i].arguments.keys())
            x = self.domain_list[i].arguments[arg_list[0]]
            y = self.domain_list[i].arguments[arg_list[1]]
            if len(arg_list) > 2:
                z = self.domain_list[i].arguments[arg_list[2]]
            else:
                z = TTree()
            result = TTree(self.domain_list[i].result, x, y, z, result, hold, hold1)
        else:
            if self.token == ',':
                self.get_token()
                hold = self.token_add(hold)
            result = TTree(fun_token, result, hold)
        if self.token != ')':
            self.say_error('syntax_err')
        return result

    # Обработка очередной лексемы
    def get_token(self):
        self.token_type = self.token = ''
        # Обработка пустой строки
        if len(self.code) == 0:
            self.token = 'end'
            self.token_type = 'delimiter'
            return
        # Пропуск ведущих пробелов и табуляций
        i = 0
        while i < len(self.code) and (self.code[i] == ' ' or self.code[i] == '\t'):
            i += 1
        self.code = self.code[i:]
        if len(self.code) == 0:
            self.token = 'end'
            self.token_type = 'delimiter'
            return
        # Обработка конца строки
        if len(self.code) and self.code[0] == '\n':
            self.code = self.code[1:]
            self.token = 'eol'
            self.token_type = 'delimiter'
            return
        # Пропуск комментариев
        if self.code[0] == '#':
            i = 0
            while i < len(self.code) and self.code[i] != '\n':
                i += 1
            i += 1
            self.code = self.code[i:]
            self.token = 'eol'
            self.token_type = 'delimiter'
            return
        # Обработка разделителей
        if '+-*/()^=><,'.find(self.code[0]) != -1:
            self.token = self.code[0]
            self.code = self.code[1:len(self.code)]
            # Проверка на наличие двойного разделителя
            if len(self.code) and '+-*/()^=><,'.find(self.code[0]) != -1:
                if self.token + self.code[0] in operations:
                    self.token += self.code[0]
                    self.code = self.code[1:len(self.code)]
            self.token_type = 'delimiter'
            return
        # Обработка чисел
        if self.code[0].isdigit():
            i = 0
            while i < len(self.code) and self.code[i].isdigit():
                i += 1
            self.token = self.code[0:i] if (i < len(self.code)) else self.code[0:]
            self.code = self.code[i:]
            if len(self.code) > 0 and self.code[0] == '.':
                self.token += '.'
                self.code = self.code[1:]
                i = 0
                while i < len(self.code) and self.code[i].isdigit():
                    i += 1
                self.token += self.code[0:i] if (i < len(self.code)) else self.code[0:]
                self.code = self.code[i:]
            if len(self.code) > 0 and (self.code[0] == 'E' or self.code[0] == 'e'):
                self.code = self.code[1:]
                self.token += 'E'
                if self.code[0] != '+' and self.code[0] != '-':
                    self.say_error('syntax_err')
                self.token += self.code[0]
                self.code = self.code[1:]
                i = 0
                while i < len(self.code) and self.code[i].isdigit():
                    i += 1
                self.token += self.code[0:i]
                self.code = self.code[i:]
            self.token_type = 'digit'
            return
        # Обработка функкций и переменных
        if self.code[0].isalpha():
            self.token = self.code[0]
            self.code = self.code[1:]
            i = 0
            while i < len(self.code) and (self.code[i].isalpha() or self.code[i] == '_' or self.code[i].isdigit()):
                i += 1
            self.token += self.code[0:i] if (i < len(self.code)) else self.code[0:]
            self.code = self.code[i:]
            if self.token in functions or self.find_domain_name(self.token) != -1:
                self.token_type = 'function'
            elif self.token in booleans:
                self.token_type = 'delimiter'
            elif self.token in statements:
                self.token_type = 'statement'
            else:
                self.token_type = 'variable'
            return

    # Запуск на выполнение
    def run(self, x, y, z=0.0):
        i = len(self.domain_list) - 1
        if i < 0:
            self.say_error('domain_err')
        arg_list = list(self.domain_list[i].arguments.keys())
        self.domain_list[i].arguments[arg_list[0]].__set__(self.domain_list[i].arguments[arg_list[0]], x)
        self.domain_list[i].arguments[arg_list[1]].__set__(self.domain_list[i].arguments[arg_list[1]], y)
        if len(arg_list) > 2:
            self.domain_list[i].arguments[arg_list[2]].__set__(self.domain_list[i].arguments[arg_list[2]], z)
        return self.domain_list[i].result.value()

    # Вывод сообщения об ошибке
    def say_error(self, err):
        self.error = err
        raise TException(self.error)

    # Трансляция входнго описания геометрической области
    def compile(self):
        # Построчная обработка входной спецификации
        while len(self.code):
            self.token_type = ''
            while self.token != 'end':
                self.get_token()
                if self.token_type == 'variable':
                    self.putback()
                    self.assignment()
                elif self.token_type == 'statement':
                    if self.token == 'domain':
                        self.parse_domain()
                    elif self.token == 'begin':
                        self.parse_begin()
                    elif self.token == 'end':
                        self.parse_end()
                    elif self.token == 'return':
                        self.parse_return()

    # Обработка оператора присваивания
    def assignment(self):
        if self.is_begin_block is False or len(self.current_block_name) == 0:
            self.say_error('def_domain_err')
        # Считываем имя переменной
        self.get_token()
        name = self.token
        if name in self.domain_list[len(self.domain_list) - 1].arguments:
            self.say_error('assign_err')
        self.get_token()
        if self.token != '=':
            self.say_error('syntax_err')
        # Считываем выражение
        exp = self.get_exp(TTree())
        if name in self.domain_list[len(self.domain_list) - 1].variables:
            self.domain_list[len(self.domain_list) - 1].set_variable(name, exp)
        else:
            self.domain_list[len(self.domain_list) - 1].add_variable(name, exp)
        if self.token != 'eol':
            self.say_error('syntax_err')

    def putback(self):
        self.code = self.token + self.code

    # Обработка оператора 'domain'
    def parse_domain(self):
        if self.is_begin_block is True:
            self.say_error('def_domain_err')
        self.get_token()
        if self.token in functions or self.token in statements:
            self.say_error('def_domain_err')
        if self.token_type != 'variable':
            self.say_error('syntax_err')
        self.current_block_name = self.token
        # Проверяем на переопределение имени
        for i in range(0, len(self.domain_list)):
            if self.domain_list[i].name == self.token:
                self.say_error('redefinition_domain_err')
        # Добавляем новую область в список
        self.domain_list.append(TDomain())
        self.domain_list[len(self.domain_list) - 1].set_name(self.token)
        self.get_token()
        if self.token != '(':
            self.say_error('syntax_err')
        # Считывание имен аргументов
        for i in range(0, 2):
            self.get_token()
            if self.token in functions or self.token in statements:
                self.say_error('def_domain_err')
            if self.token_type != 'variable':
                self.say_error('syntax_err')
            self.domain_list[len(self.domain_list) - 1].add_argument(self.token)
            self.get_token()
            if self.token != ',' and self.token != ')':
                self.say_error('syntax_err')
            if self.code[0] == ')':
                break
        if self.token != ')':
            self.say_error('syntax_err')

    # Обработка оператора 'begin'
    def parse_begin(self):
        if len(self.current_block_name) == 0:
            self.say_error('def_domain_err')
        if self.is_begin_block is True:
            self.say_error('def_domain_err')
        self.is_begin_block = True
        self.get_token()
        if self.token != 'eol':
            self.say_error('syntax_err')

    # Обработка оператора 'end'
    def parse_end(self):
        if len(self.current_block_name) == 0 or self.is_begin_block is False:
            self.say_error('def_domain_err')
        self.current_block_name = ''
        self.is_begin_block = False
        self.get_token()
        if self.token != 'eol' and self.token != 'end':
            self.say_error('syntax_err')

    # Обработка оператора 'return'
    def parse_return(self):
        if len(self.current_block_name) == 0 or self.is_begin_block is False:
            self.say_error('def_domain_err')
        # Считываем выражение
        exp = self.get_exp(TTree())
        self.domain_list[len(self.domain_list) - 1].set_result(exp)
        if self.token != 'eol':
            self.say_error('syntax_err')
