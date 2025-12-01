#!/usr/bin/env python3
import sys
import re
import json
import argparse
from pathlib import Path


class ConfigError(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(f"Line {line}: {message}" if line else message)


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.tokens = []

    def tokenize(self):
        while self.pos < len(self.text):
            # Пропускаем пробелы
            if self.text[self.pos].isspace():
                if self.text[self.pos] == '\n':
                    self.line += 1
                self.pos += 1
                continue

            # Комментарии
            if self.text[self.pos] == '%':
                while self.pos < len(self.text) and self.text[self.pos] != '\n':
                    self.pos += 1
                continue

            # Строки
            if self.text[self.pos] == '"':
                start = self.pos
                self.pos += 1
                while self.pos < len(self.text) and self.text[self.pos] != '"':
                    if self.text[self.pos] == '\\' and self.pos + 1 < len(self.text):
                        self.pos += 2
                    else:
                        self.pos += 1

                if self.pos >= len(self.text):
                    raise ConfigError("Unclosed string", self.line)

                self.pos += 1
                self.tokens.append(('STRING', self.text[start:self.pos], self.line))
                continue

            # Числа
            if self.text[self.pos].isdigit():
                start = self.pos
                while self.pos < len(self.text) and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
                    self.pos += 1
                self.tokens.append(('NUMBER', self.text[start:self.pos], self.line))
                continue

            # Имена (константы - заглавные буквы)
            if self.text[self.pos].isupper():
                start = self.pos
                while self.pos < len(self.text) and (
                        self.text[self.pos].isupper() or self.text[self.pos].isdigit() or self.text[self.pos] == '_'):
                    self.pos += 1
                self.tokens.append(('NAME', self.text[start:self.pos], self.line))
                continue

            # Имена ключей (строчные буквы)
            if self.text[self.pos].islower():
                start = self.pos
                while self.pos < len(self.text) and (
                        self.text[self.pos].isalpha() or self.text[self.pos].isdigit() or self.text[self.pos] == '_'):
                    self.pos += 1
                value = self.text[start:self.pos]
                # Проверяем ключевые слова
                if value == 'array':
                    self.tokens.append(('ARRAY', value, self.line))
                elif value == 'def':
                    self.tokens.append(('DEF', value, self.line))
                elif value in ['chr', 'len']:
                    self.tokens.append(('FUNC', value, self.line))
                else:
                    self.tokens.append(('KEY', value, self.line))
                continue

            # Одиночные символы
            ch = self.text[self.pos]
            if ch in '()[]{}:,;+-*/':
                self.tokens.append((ch, ch, self.line))
                self.pos += 1
                continue

            raise ConfigError(f"Unexpected character: '{ch}'", self.line)

        return self.tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.constants = {}

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type=None):
        token = self.current()
        if token is None:
            raise ConfigError("Unexpected end of input")

        if expected_type and token[0] != expected_type:
            raise ConfigError(f"Expected {expected_type}, got {token[0]}", token[2])

        self.pos += 1
        return token

    def peek(self, expected_type):
        token = self.current()
        return token and token[0] == expected_type

    def parse(self):
        result = None

        while self.pos < len(self.tokens):
            token_type, token_value, line = self.current()

            if token_type == 'DEF':
                self.parse_constant_def()
            elif token_type == '(' and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1][0] == '[':
                result = self.parse_dict()
            elif token_type == '[':
                result = self.parse_dict()
            else:
                raise ConfigError(f"Unexpected token: {token_type}", line)

        return result or {}

    def parse_constant_def(self):
        self.consume('DEF')  # def
        name_token = self.consume('NAME')
        value = self.parse_value()

        # Пропускаем закрывающие скобки и точку с запятой
        if self.peek(')'):
            self.consume(')')
        if self.peek(';'):
            self.consume(';')

        self.constants[name_token[1]] = value
        return ('CONST', name_token[1], value)

    def parse_value(self):
        token_type, token_value, line = self.current()

        if token_type == 'NUMBER':
            self.consume()
            # Проверяем, целое или дробное
            if '.' in token_value:
                return float(token_value)
            return int(token_value)

        elif token_type == 'STRING':
            self.consume()
            # Убираем кавычки
            return token_value[1:-1]

        elif token_type == 'NAME':
            self.consume()
            # Это ссылка на константу
            if token_value in self.constants:
                return self.constants[token_value]
            raise ConfigError(f"Undefined constant: {token_value}", line)

        elif token_type == 'KEY':
            # Это ключ в словаре, но в значении это не ожидается
            raise ConfigError(f"Unexpected key in value position: {token_value}", line)

        elif token_type == 'ARRAY':
            return self.parse_array()

        elif token_type == '{':
            return self.parse_expression()

        elif token_type == '(':
            self.consume('(')
            if self.peek('['):
                result = self.parse_dict()
            else:
                result = self.parse_value()
                if self.peek(')'):
                    self.consume(')')
            return result

        elif token_type == '[':
            return self.parse_dict()

        else:
            raise ConfigError(f"Unexpected token in value: {token_type}", line)

    def parse_array(self):
        self.consume('ARRAY')  # array
        self.consume('(')  # (

        elements = []
        while not self.peek(')'):
            elements.append(self.parse_value())
            if self.peek(','):
                self.consume(',')

        self.consume(')')  # )
        return elements

    def parse_dict(self):
        # Пропускаем возможные открывающие скобки
        if self.peek('('):
            self.consume('(')

        self.consume('[')  # [

        pairs = {}
        while not self.peek(']'):
            # Пропускаем возможные открывающие скобки внутри
            if self.peek('('):
                self.consume('(')

            # Читаем ключ
            if self.peek('KEY'):
                _, key, _ = self.consume('KEY')
            elif self.peek('NAME'):
                _, key, _ = self.consume('NAME')
            else:
                raise ConfigError("Expected key name", self.current()[2] if self.current() else None)

            self.consume(':')  # :

            # Читаем значение
            value = self.parse_value()
            pairs[key] = value

            if self.peek(','):
                self.consume(',')

        self.consume(']')  # ]

        # Пропускаем возможные закрывающие скобки
        if self.peek(')'):
            self.consume(')')

        return pairs

    def parse_expression(self):
        self.consume('{')  # {

        # Читаем оператор или функцию
        if self.peek('FUNC'):
            _, func, line = self.consume('FUNC')
            args = []
            while not self.peek('}'):
                args.append(self.parse_value())
            self.consume('}')  # }

            # Вычисляем функцию
            if func == 'chr':
                if len(args) != 1:
                    raise ConfigError("chr() expects exactly 1 argument", line)
                return chr(int(args[0]))
            elif func == 'len':
                if len(args) != 1:
                    raise ConfigError("len() expects exactly 1 argument", line)
                if isinstance(args[0], str):
                    return len(args[0])
                elif isinstance(args[0], list):
                    return len(args[0])
                else:
                    raise ConfigError("len() expects string or array", line)

        else:
            # Арифметические операторы
            if self.peek('+'):
                op = '+'
                self.consume('+')
            elif self.peek('-'):
                op = '-'
                self.consume('-')
            elif self.peek('*'):
                op = '*'
                self.consume('*')
            elif self.peek('/'):
                op = '/'
                self.consume('/')
            else:
                raise ConfigError("Expected operator", self.current()[2] if self.current() else None)

            # Читаем аргументы
            args = []
            while not self.peek('}'):
                args.append(self.parse_value())
            self.consume('}')  # }

            # Вычисляем выражение
            if len(args) < 2:
                raise ConfigError(f"Operator {op} expects at least 2 arguments", line)

            result = args[0]
            for arg in args[1:]:
                if op == '+':
                    if isinstance(result, str) or isinstance(arg, str):
                        result = str(result) + str(arg)
                    else:
                        result += arg
                elif op == '-':
                    result -= arg
                elif op == '*':
                    result *= arg
                elif op == '/':
                    result /= arg

            return result


def parse_config(text):
    """Основная функция парсинга конфигурации"""
    lexer = Lexer(text)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    result = parser.parse()

    return result


def main():
    parser = argparse.ArgumentParser(description='Конфигурационный парсер в JSON')
    parser.add_argument('-i', '--input', required=True, help='Входной файл')
    parser.add_argument('-o', '--output', help='Выходной файл (опционально)')

    args = parser.parse_args()

    try:
        # Чтение входного файла
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()

        # Парсинг
        result = parse_config(content)

        # Преобразование в JSON
        json_output = json.dumps(result, indent=2, ensure_ascii=False)

        # Вывод результата
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            print(f"Результат сохранен в {args.output}")
        else:
            print(json_output)

    except FileNotFoundError:
        print(f"Ошибка: файл '{args.input}' не найден")
        sys.exit(1)
    except ConfigError as e:
        print(f"Ошибка конфигурации: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()