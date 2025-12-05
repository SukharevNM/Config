import sys
import json
import argparse
import re


class Token:
    __slots__ = ('type', 'value', 'line', 'col')

    def __init__(self, type, value, line, col):
        self.type = type
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.col})"


class ASTNode:
    pass


class NumberNode(ASTNode):
    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value


class StringNode(ASTNode):
    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value


class NameNode(ASTNode):
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name


class ArrayNode(ASTNode):
    __slots__ = ('elements',)

    def __init__(self, elements):
        self.elements = elements


class DictNode(ASTNode):
    __slots__ = ('pairs',)

    def __init__(self, pairs):
        self.pairs = pairs  # list of (name, expr)


class BraceNode(ASTNode):
    __slots__ = ('op', 'args')

    def __init__(self, op, args):
        self.op = op
        self.args = args


class Definition(ASTNode):
    __slots__ = ('name', 'value_expr')

    def __init__(self, name, value_expr):
        self.name = name
        self.value_expr = value_expr


class Program(ASTNode):
    __slots__ = ('definitions', 'main_expr')

    def __init__(self, definitions, main_expr):
        self.definitions = definitions
        self.main_expr = main_expr


class ConfigError(Exception):
    def __init__(self, message, token=None):
        if token:
            message = f"Line {token.line}, Col {token.col}: {message}"
        super().__init__(message)


def tokenize(s):
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
        ('NAME', r'[A-Za-z_][A-Za-z0-9_]*'),  # Изменено: поддержка строчных букв и _
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
        ('MISMATCH', r'.'),
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specs)
    line = 1
    col = 1
    tokens = []
    for mo in re.finditer(tok_regex, s):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'COMMENT' or kind == 'WHITESPACE':
            for char in value:
                if char == '\n':
                    line += 1
                    col = 1
                else:
                    col += 1
            continue
        elif kind == 'MISMATCH':
            raise ConfigError(f"Unexpected character '{value}'", Token('MISMATCH', value, line, col))

        token = Token(kind, value, line, col)
        tokens.append(token)

        # Update line and column
        for char in value:
            if char == '\n':
                line += 1
                col = 1
            else:
                col += 1
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None

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
            raise ConfigError(f"Expected {token_type}, got {self.current_token.type}", self.current_token)
        token = self.current_token
        self.advance()
        return token

    def parse_program(self):
        definitions = []
        while self.current_token and self.current_token.type == 'LPAREN':
            next_token = self.peek()
            if next_token and next_token.type == 'DEF':
                definitions.append(self.parse_definition())
            else:
                break
        main_expr = self.parse_expr()
        if self.current_token:
            raise ConfigError(f"Unexpected token after main expression: {self.current_token.type}", self.current_token)
        return Program(definitions, main_expr)

    def parse_definition(self):
        self.consume('LPAREN')
        def_token = self.consume('DEF', "Expected 'def' after '('")

        # Проверяем, что после def идет имя (теперь может быть с маленькой буквы или _)
        if self.current_token is None:
            raise ConfigError("Expected name after 'def'", def_token)

        if self.current_token.type != 'NAME':
            raise ConfigError(f"Expected name after 'def', got {self.current_token.type}", self.current_token)

        name_token = self.consume('NAME', "Expected constant name after 'def'")
        value_expr = self.parse_expr()
        self.consume('RPAREN', "Expected ')' after constant value")
        self.consume('SEMICOLON', "Expected ';' after definition")
        return Definition(name_token.value, value_expr)

    def parse_expr(self):
        if self.current_token is None:
            raise ConfigError("Unexpected end of input")

        token_type = self.current_token.type
        if token_type == 'NUMBER':
            token = self.consume('NUMBER')
            return NumberNode(token.value)
        elif token_type == 'STRING':
            token = self.consume('STRING')
            raw_str = token.value[1:-1]
            unescaped = ''
            i = 0
            while i < len(raw_str):
                if raw_str[i] == '\\':
                    i += 1
                    if i < len(raw_str):
                        c = raw_str[i]
                        if c == '"':
                            unescaped += '"'
                        elif c == '\\':
                            unescaped += '\\'
                        elif c == 'n':
                            unescaped += '\n'
                        elif c == 't':
                            unescaped += '\t'
                        else:
                            unescaped += c
                        i += 1
                    else:
                        unescaped += '\\'
                else:
                    unescaped += raw_str[i]
                    i += 1
            return StringNode(unescaped)
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
            raise ConfigError(f"Unexpected token in expression: {token_type}", self.current_token)

    def parse_array_expr(self):
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
        self.consume('DICT_OPEN')
        pairs = []
        if self.current_token and self.current_token.type != 'DICT_CLOSE':
            while True:
                # Проверяем, что ключ словаря - это допустимое имя
                if self.current_token.type != 'NAME':
                    raise ConfigError(f"Expected key name in dictionary, got {self.current_token.type}",
                                      self.current_token)

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
        self.consume('LBRACE')
        if self.current_token is None:
            raise ConfigError("Unexpected end of input in brace expression")

        op_token = self.current_token
        # Поддерживаем операторы как в верхнем, так и в нижнем регистре
        if op_token.type in ['PLUS', 'MINUS', 'TIMES', 'DIV']:
            op_str = op_token.value
            self.advance()
        elif op_token.type in ['CHR', 'LEN'] or \
                (op_token.type == 'NAME' and op_token.value.lower() in ['chr', 'len']):
            # Приводим к нижнему регистру для единообразия
            op_str = op_token.value.lower()
            self.advance()
        else:
            raise ConfigError(f"Expected operator in brace expression, got {op_token.type}", op_token)

        args = []
        while self.current_token and self.current_token.type != 'RBRACE':
            args.append(self.parse_expr())

        self.consume('RBRACE', "Expected '}' to close brace expression")
        return BraceNode(op_str, args)


class Evaluator:
    def __init__(self, env=None):
        self.env = env if env is not None else {}

    def evaluate(self, node):
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
        try:
            args = [self.evaluate(arg) for arg in node.args]
        except Exception as e:
            raise ConfigError(f"Error evaluating arguments for {node.op}: {str(e)}")

        op = node.op.lower()  # Приводим к нижнему регистру для единообразия
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


def main():
    parser = argparse.ArgumentParser(description='Config to JSON converter')
    parser.add_argument('--input', required=True, help='Path to input config file')
    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()

        tokens = tokenize(content)
        parser = Parser(tokens)
        program = parser.parse_program()

        env = {}
        evaluator = Evaluator(env)

        # Evaluate definitions
        for defn in program.definitions:
            try:
                value = evaluator.evaluate(defn.value_expr)
                env[defn.name] = value
            except Exception as e:
                raise ConfigError(f"Error in definition '{defn.name}': {str(e)}")

        # Evaluate main expression
        result = evaluator.evaluate(program.main_expr)

        # Output JSON
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