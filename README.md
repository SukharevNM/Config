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
import sys
import json
from pathlib import Path
from lark import Lark, Transformer, v_args, UnexpectedInput, Tree, Token

grammar = r"""
    start: (statement)*

    ?statement: const_def | expr_value

    const_def: "(" "def" IDENTIFIER value ")" ";"

    expr_value: value ";"

    ?value: NUMBER
          | STRING
          | array
          | dict
          | IDENTIFIER          -> const_ref
          | expr

    array: "array" "(" [value ("," value)*] ")"

    dict: "([" [pair ("," pair)*] ","? "])"
    pair: IDENTIFIER ":" value   -> dict_pair

    ?expr: "{" OPER value value "}"   -> binary_op
         | "{" "chr" value "}"        -> chr_op
         | "{" "len" value "}"        -> len_op

    OPER: "+" | "-" | "*" | "/"

    IDENTIFIER: /[A-Z]+/
    NUMBER: /\d+/
    STRING: /"[^"]*"/

    %import common.WS
    %import common.NEWLINE
    %ignore WS
    %ignore COMMENT
    COMMENT: "%" /[^\n]*/
"""


class ConstCollector(Transformer):
    """Первый проход: собираем все определения констант"""

    def __init__(self):
        self.consts = {}

    def const_def(self, args):
        name = str(args[0])
        value_tree = args[1]
        self.consts[name] = value_tree
        return None  # Удаляем из результата

    def expr_value(self, args):
        return None  # Игнорируем значения в первом проходе

    def start(self, _):
        return self.consts


class Evaluator(Transformer):
    """Второй проход: вычисляем значения с уже известными константами"""

    def __init__(self, consts):
        super().__init__()
        self.consts = {}
        # Вычисляем константы в порядке определения
        for name, value_tree in consts.items():
            self.consts[name] = self.transform(value_tree)

    # Обработка литералов
    def NUMBER(self, token):
        return int(token)

    def STRING(self, token):
        return token[1:-1]  # Убираем кавычки

    # Обработка констант
    def const_ref(self, args):
        name = str(args[0])
        if name in self.consts:
            return self.consts[name]
        raise ValueError(f"Undefined constant: {name}")

    # Обработка массивов
    def array(self, items):
        return [self.transform(item) if isinstance(item, Tree) else item for item in items]

    # Обработка словарей
    def dict_pair(self, args):
        key = str(args[0])
        value = args[1]
        if isinstance(value, Tree):
            value = self.transform(value)
        return (key, value)

    def dict(self, pairs):
        result = {}
        for key, value in pairs:
            if isinstance(value, Tree):
                value = self.transform(value)
            result[key] = value
        return result

    # Обработка выражений
    def binary_op(self, args):
        op = str(args[0])
        left = self.transform(args[1]) if isinstance(args[1], Tree) else args[1]
        right = self.transform(args[2]) if isinstance(args[2], Tree) else args[2]

        if op == "+":
            return left + right
        elif op == "-":
            return left - right
        elif op == "*":
            return left * right
        elif op == "/":
            if right == 0:
                raise ValueError("Division by zero")
            return left // right
        else:
            raise ValueError(f"Unknown operator: {op}")

    def chr_op(self, args):
        val = self.transform(args[0]) if isinstance(args[0], Tree) else args[0]
        if not isinstance(val, int):
            raise ValueError("chr() expects an integer")
        return chr(val)

    def len_op(self, args):
        val = self.transform(args[0]) if isinstance(args[0], Tree) else args[0]
        if not isinstance(val, str):
            raise ValueError("len() expects a string")
        return len(val)

    # Обработка верхнеуровневых конструкций
    def expr_value(self, args):
        value = args[0]
        if isinstance(value, Tree):
            return self.transform(value)
        return value

    def const_def(self, _):
        return None  # Уже обработано в первом проходе

    def start(self, args):
        result = []
        for item in args:
            if item is not None:
                if isinstance(item, Tree):
                    result.append(self.transform(item))
                else:
                    result.append(item)
        return result


def parse_config(text):
    parser = Lark(grammar, parser='lalr')
    tree = parser.parse(text)

    # Первый проход: собираем константы
    collector = ConstCollector()
    consts = collector.transform(tree)

    # Второй проход: вычисляем всё
    evaluator = Evaluator(consts)
    result = evaluator.transform(tree)
    return result


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <config_file>", file=sys.stderr)
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: file '{filepath}' not found", file=sys.stderr)
        sys.exit(1)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        result = parse_config(text)
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()
    except UnexpectedInput as e:
        print(f"Syntax error at line {e.line}, column {e.column}:\n{e.get_context(text)}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Semantic error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```
### Файл test_main.py
```
import json
import tempfile
from pathlib import Path
from main import parse_config

def test_numbers_and_strings():
    config = '''
    42;
    "hello";
    '''
    result = parse_config(config)
    assert result == [42, "hello"]

def test_arrays():
    config = '''
    array(1, "a", 3);
    '''
    result = parse_config(config)
    assert result == [[1, "a", 3]]

def test_nested_structures():
    config = '''
    array(
        ([ A: "x", B: 10 ]),
        "top"
    );
    '''
    result = parse_config(config)
    expected = [[{"A": "x", "B": 10}, "top"]]
    assert result == expected

def test_constants_and_expressions():
    config = '''
    (def SIZE 10);
    (def LABEL "Player");
    {+ SIZE 5};
    {len LABEL};
    {chr 65};
    '''
    result = parse_config(config)
    assert result == [15, 6, "A"]

def test_dict():
    config = '''
    ([
        NAME: "Server",
        PORT: 8080,
        TAGS: array("http", "api")
    ]);
    '''
    result = parse_config(config)
    expected = [{"NAME": "Server", "PORT": 8080, "TAGS": ["http", "api"]}]
    assert result == expected

def test_complex():
    config = '''
    (def X 3);
    (def Y 4);
    ([
        AREA: {* X Y},
        MSG: {chr {+ 65 X}}
    ]);
    '''
    result = parse_config(config)
    expected = [{"AREA": 12, "MSG": "D"}]
    assert result == expected

if __name__ == "__main__":
    test_numbers_and_strings()
    test_arrays()
    test_nested_structures()
    test_constants_and_expressions()
    test_dict()
    test_complex()
    print("All tests passed!")
```
