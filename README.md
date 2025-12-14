# Учебный конфигурационный язык - CLI инструмент
## Проект реализует интерпретатор для специализированного конфигурационного языка, который преобразует конфигурационные файлы в формат JSON.
Он позволяет: создавать конфигурации на специализированном языке,
делать вычисления арифметических выражений в конфигурациях,
работать со строками и символами,
обнаруживать синтаксические ошибки и неопределённые константы,
работать через командную строку с файлами конфигурации,
а также преобразовывать конфигурацию в формат JSON.
## Синтаксис учебного конфигурационного языка
### Константы
```
(def ИМЯ значение);
```
### Поддерживаются числа, строки, массивы и словари.
### Арифмитические вычисления
```
{+ 10 20}
{- 100 50}
{* 5 4}
{/ 100 4}
```
### Словари
```
([
    key1: value1,
    key2: ([
        nested_key: "nested_value"
    ])
])
```
### Массивы
```
array(
    ([ x: 1, y: 2 ]),
    ([ x: 3, y: 4 ])
)
```
### Числа
```
\d+
```
### Строки
```
"Это строка"
```
### Однострочные комментарии
```
% Это однострочный комментарий
```
### Специальные функции
```
{chr 65}
{chr 960}
{len "Hello"}
```
### Установка
```
git clone <репозиторий>
cd Config
```
###  Использование
Через командную строку с файлом: 
```
python main.py <config_file>
```
### Пример ввода
```
(def MAXPLAYERS 4);
(def DEFAULTHEALTH 100);

([
  GAMETITLE: "Space Adventure",
  MAXPLAYERS: MAXPLAYERS,
  DEFAULTSTATS: ([
    HEALTH: DEFAULTHEALTH,
    AMMO: 50
  ]),
  UPGRADES: array(
    {+ DEFAULTHEALTH 20},
    {chr 85}
  )
]);
```
### Пример вывода JSON
```
[
  {
    "GAMETITLE": "Space Adventure",
    "MAXPLAYERS": 4,
    "DEFAULTSTATS": {
      "HEALTH": 100,
      "AMMO": 50
    },
    "UPGRADES": [
      120,
      "U"
    ]
  }
]
```
## Примеры конфигураций и вывод в JSON
Веб-сервер
Конфигурация: 
```
(def PORTBASE 8000);
(def ENV "prod");

([
  SERVER: ([
    HOST: "0.0.0.0",
    PORT: {+ PORTBASE 80},
    ENVNAME: ENV,
    LOGLEVEL: {chr 73}
  ]),
  FEATURES: array("ssl", "gzip", {len ENV})
]);
```
Вывод JSON:
```
[
  {
    "SERVER": {
      "HOST": "0.0.0.0",
      "PORT": 8080,
      "ENVNAME": "prod",
      "LOGLEVEL": "I"
    },
    "FEATURES": [
      "ssl",
      "gzip",
      4
    ]
  }
]
}
```
Геометрические вычисления
Конфигурация: 
```
(def PI 3);
(def RADIUS 5);

([
  CIRCLE: ([
    RADIUS: RADIUS,
    AREA: {* PI {* RADIUS RADIUS}},
    LABEL: {chr 67}
  ]),
  RECT: ([
    WIDTH: 10,
    HEIGHT: {+ RADIUS 2}
  ])
]);
```
Вывод JSON: 
```
[
  {
    "CIRCLE": {
      "RADIUS": 5,
      "AREA": 75,
      "LABEL": "C"
    },
    "RECT": {
      "WIDTH": 10,
      "HEIGHT": 7
    }
  }
]
```
Игра
Конфигурация: 
```
(def MAXPLAYERS 4);
(def DEFAULTHEALTH 100);

([
  GAMETITLE: "Space Adventure",
  MAXPLAYERS: MAXPLAYERS,
  DEFAULTSTATS: ([
    HEALTH: DEFAULTHEALTH,
    AMMO: 50
  ]),
  UPGRADES: array(
    {+ DEFAULTHEALTH 20},
    {chr 85}
  )
]);
```
Вывод JSON:
```
[
  {
    "GAMETITLE": "Space Adventure",
    "MAXPLAYERS": 4,
    "DEFAULTSTATS": {
      "HEALTH": 100,
      "AMMO": 50
    },
    "UPGRADES": [
      120,
      "U"
    ]
  }
]
```
## Тесты
Проект покрыт тестами с использованием простых функций проверки:
|Тест|Описание|Ожидаемый результат|
|----|--------|-------------------|
|test_numbers_and_strings|Базовые типы данных (числа и строки)|Правильное преобразование чисел и строк|
|test_arrays|Создание и обработка массивов|Корректные массивы с разными типами элементов|
|test_nested_structures|Вложенные структуры (массивы со словарями)|Правильная вложенность структур данных|
|test_constants_and_expressions|Константы и арифметические выражения|Вычисление выражений и работа с константами|
|test_dict|Создание и обработка словарей|Корректные словари с ключами и значениями|
|test_complex|Комплексные сценарии с комбинацией функций|Корректная работа всех возможностей языка|
### Запуск тестов
python test_main.py
### Ожидаемый вывод
```
All tests passed!
```
### Обработка ошибок
Синтаксическая ошибка:
```
([
    invalid key "value"  % Пропущено двоеточие
])
```
Вывод: 
```
Syntax error at line 2, column 5:
    invalid key "value"  % Пропущено двоеточие
    ^
```
Неопределённая константа:
```
(def ZERO 0);
({/ 10 UNKNOWN});
```
Вывод:
```
Semantic error: Undefined constant: UNKNOWN
```
Ошибка типа:
```
{+ 10 "text"}  % Попытка сложить число и строку
```
Вывод:
```
Semantic error: + expects integer arguments, got types: int, str
```
## Пример кода
### Файл main.py
```
#!/usr/bin/env python3
import sys
import json
import argparse

from config_parser import parse_and_evaluate

def main():
    parser = argparse.ArgumentParser(description='Config to JSON converter')
    parser.add_argument('--input', required=True, 
                       help='Path to input config file')
    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()

        # Парсинг и вычисление
        result = parse_and_evaluate(content)
        
        # Вывод JSON
        json_output = json.dumps(result, ensure_ascii=False, indent=2)
        sys.stdout.write(json_output)
        
    except ConfigError as e:
        sys.stderr.write(str(e) + '\n')
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Internal error: {str(e)}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
```
### Файл config_parser.py
```
import re

class Token:
    """Представляет лексему с типом, значением и позицией"""
    __slots__ = ('type', 'value', 'line', 'col')
    
    def __init__(self, type, value, line, col):
        self.type = type
        self.value = value
        self.line = line
        self.col = col

class ConfigError(Exception):
    """Класс для ошибок конфигурации"""
    def __init__(self, message, token=None):
        if token:
            message = f"Line {token.line}, Col {token.col}: {message}"
        super().__init__(message)

def tokenize(source_code):
    """Лексический анализатор - разбивает код на токены"""
    token_specs = [
        ('COMMENT', r'%[^\n]*'),
        ('WHITESPACE', r'[ \t\r\n]+'),
        ('DICT_OPEN', r'\(\['),
        ('DICT_CLOSE', r'\]\)'),
        ('ARRAY_KEYWORD', r'array'),
        ('DEF', r'def'),
        ('CHR', r'chr'),
        ('LEN', r'len'),
        ('NUMBER', r'\d+'),
        ('STRING', r'"(?:\\.|[^"\\])*"'),
        ('NAME', r'[A-Za-z_][A-Za-z0-9_]*'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACE', r'\{'),
        ('RBRACE', r'\}'),
        ('COLON', r':'),
        ('COMMA', r','),
        ('PLUS', r'\+'),
        ('MINUS', r'-'),
        ('TIMES', r'\*'),
        ('DIV', r'/'),
        ('SEMICOLON', r';'),
    ]
    
    # Регулярное выражение для всех токенов
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specs)
    
    tokens = []
    line = 1
    col = 1
    
    for mo in re.finditer(tok_regex, source_code):
        kind = mo.lastgroup
        value = mo.group()
        
        # Пропускаем комментарии и пробелы
        if kind == 'COMMENT' or kind == 'WHITESPACE':
            # Обновляем позицию
            for char in value:
                if char == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
            continue
        
        # Создаем токен
        token = Token(kind, value, line, col)
        tokens.append(token)
        
        # Обновляем позицию
        for char in value:
            if char == '\n':
                line += 1
                col = 1
            else:
                col += 1
    
    return tokens

class Parser:
    """Синтаксический анализатор - строит AST"""
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def parse_program(self):
        """Парсит всю программу"""
        definitions = []
        
        # Парсим определения констант
        while self.current_token and self.current_token.type == 'LPAREN':
            next_token = self.peek()
            if next_token and next_token.type == 'DEF':
                definitions.append(self.parse_definition())
            else:
                break
        
        # Парсим основное выражение
        main_expr = self.parse_expr()
        
        if self.current_token:
            raise ConfigError(
                f"Unexpected token after main expression: {self.current_token.type}",
                self.current_token
            )
        
        return Program(definitions, main_expr)
    
    def parse_definition(self):
        """Парсит определение константы"""
        self.consume('LPAREN')
        self.consume('DEF', "Expected 'def' after '('")
        
        name_token = self.consume('NAME', "Expected constant name after 'def'")
        value_expr = self.parse_expr()
        
        self.consume('RPAREN', "Expected ')' after constant value")
        self.consume('SEMICOLON', "Expected ';' after definition")
        
        return Definition(name_token.value, value_expr)
    
    def parse_expr(self):
        """Парсит выражение"""
        if self.current_token is None:
            raise ConfigError("Unexpected end of input")
        
        token_type = self.current_token.type
        
        if token_type == 'NUMBER':
            token = self.consume('NUMBER')
            return NumberNode(token.value)
        elif token_type == 'STRING':
            token = self.consume('STRING')
            return StringNode(token.value[1:-1])
        elif token_type == 'NAME':
            token = self.consume('NAME')
            return NameNode(token.value)
        elif token_type == 'ARRAY_KEYWORD':
            return self.parse_array_expr()
        elif token_type == 'DICT_OPEN':
            return self.parse_dict_expr()
        elif token_type == 'LBRACE':
            return self.parse_brace_expr()
        else:
            raise ConfigError(
                f"Unexpected token in expression: {token_type}",
                self.current_token
            )
    
    def parse_array_expr(self):
        """Парсит массив"""
        self.consume('ARRAY_KEYWORD')
        self.consume('LPAREN', "Expected '(' after 'array'")
        
        elements = []
        if self.current_token and self.current_token.type != 'RPAREN':
            elements.append(self.parse_expr())
            while self.current_token and self.current_token.type == 'COMMA':
                self.consume('COMMA')
                elements.append(self.parse_expr())
        
        self.consume('RPAREN', "Expected ')' to close array")
        return ArrayNode(elements)
    
    def parse_dict_expr(self):
        """Парсит словарь"""
        self.consume('DICT_OPEN')
        
        pairs = []
        if self.current_token and self.current_token.type != 'DICT_CLOSE':
            while True:
                if self.current_token.type != 'NAME':
                    raise ConfigError(
                        f"Expected key name in dictionary, got {self.current_token.type}",
                        self.current_token
                    )
                
                name_token = self.consume('NAME', "Expected key name in dictionary")
                self.consume('COLON', "Expected ':' after key name")
                value_expr = self.parse_expr()
                
                pairs.append((name_token.value, value_expr))
                
                if self.current_token and self.current_token.type == 'COMMA':
                    self.consume('COMMA')
                else:
                    break
        
        self.consume('DICT_CLOSE', "Expected '])' to close dictionary")
        return DictNode(pairs)
    
    def parse_brace_expr(self):
        """Парсит операцию в фигурных скобках"""
        self.consume('LBRACE')
        
        if self.current_token is None:
            raise ConfigError("Unexpected end of input in brace expression")
        
        op_token = self.current_token
        if op_token.type in ['PLUS', 'MINUS', 'TIMES', 'DIV']:
            op_str = op_token.value
            self.advance()
        elif op_token.type in ['CHR', 'LEN']:
            op_str = op_token.value.lower()
            self.advance()
        else:
            raise ConfigError(
                f"Expected operator in brace expression, got {op_token.type}",
                op_token
            )
        
        args = []
        while self.current_token and self.current_token.type != 'RBRACE':
            args.append(self.parse_expr())
        
        self.consume('RBRACE', "Expected '}' to close brace expression")
        return BraceNode(op_str, args)
    
    # Вспомогательные методы
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None
    
    def consume(self, token_type, error_msg=None):
        if self.current_token is None:
            raise ConfigError("Unexpected end of input")
        if self.current_token.type != token_type:
            if error_msg:
                raise ConfigError(error_msg, self.current_token)
            raise ConfigError(
                f"Expected {token_type}, got {self.current_token.type}",
                self.current_token
            )
        token = self.current_token
        self.advance()
        return token

class Evaluator:
    """Интерпретатор - вычисляет значения выражений"""
    def __init__(self, env=None):
        self.env = env if env is not None else {}
    
    def evaluate(self, node):
        """Вычисляет значение узла AST"""
        if isinstance(node, NumberNode):
            return int(node.value)
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, NameNode):
            if node.name in self.env:
                return self.env[node.name]
            raise ConfigError(f"Undefined constant: {node.name}")
        elif isinstance(node, ArrayNode):
            return [self.evaluate(elem) for elem in node.elements]
        elif isinstance(node, DictNode):
            return {name: self.evaluate(expr) for name, expr in node.pairs}
        elif isinstance(node, BraceNode):
            return self.evaluate_brace(node)
        else:
            raise ConfigError(f"Unknown node type: {type(node)}")
    
    def evaluate_brace(self, node):
        """Вычисляет операцию в фигурных скобках"""
        args = [self.evaluate(arg) for arg in node.args]
        op = node.op.lower()
        
        if op == '+':
            self._check_arity(args, 2, '+')
            self._check_all_int(args, '+')
            return args[0] + args[1]
        elif op == '-':
            self._check_arity(args, 2, '-')
            self._check_all_int(args, '-')
            return args[0] - args[1]
        elif op == '*':
            self._check_arity(args, 2, '*')
            self._check_all_int(args, '*')
            return args[0] * args[1]
        elif op == '/':
            self._check_arity(args, 2, '/')
            self._check_all_int(args, '/')
            if args[1] == 0:
                raise ConfigError("Division by zero in constant expression")
            return args[0] // args[1]
        elif op == 'chr':
            self._check_arity(args, 1, 'chr')
            if not isinstance(args[0], int):
                raise ConfigError("chr() expects an integer argument")
            try:
                return chr(args[0])
            except ValueError as e:
                raise ConfigError(f"chr() error: {str(e)}")
        elif op == 'len':
            self._check_arity(args, 1, 'len')
            arg = args[0]
            if isinstance(arg, str) or isinstance(arg, list):
                return len(arg)
            raise ConfigError(f"len() expects string or array, got {type(arg).__name__}")
        else:
            raise ConfigError(f"Unknown operator: {op}")
    
    def _check_arity(self, args, expected, op):
        if len(args) != expected:
            raise ConfigError(f"{op} expects {expected} arguments, got {len(args)}")
    
    def _check_all_int(self, args, op):
        if not all(isinstance(a, int) for a in args):
            types = ', '.join(type(a).__name__ for a in args)
            raise ConfigError(f"{op} expects integer arguments, got types: {types}")

def parse_and_evaluate(source_code):
    """Основная функция парсинга и вычисления"""
    tokens = tokenize(source_code)
    parser = Parser(tokens)
    program = parser.parse_program()
    
    env = {}
    evaluator = Evaluator(env)
    
    # Вычисляем определения констант
    for definition in program.definitions:
        try:
            value = evaluator.evaluate(definition.value_expr)
            env[definition.name] = value
        except Exception as e:
            raise ConfigError(f"Error in definition '{definition.name}': {str(e)}")
    
    # Вычисляем основное выражение
    result = evaluator.evaluate(program.main_expr)
    return result
```
