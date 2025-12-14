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
