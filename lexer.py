import re
from error import LexerError


class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"


class Lexer:
    # Регулярные выражения для токенов
    tokens_regex = [
        ('COMMENT', r'%.*'),  # Комментарии
        ('NUMBER', r'\d+(\.\d+)?'),  # Числа (целые и с плавающей точкой)
        ('STRING', r'"[^"\\]*(?:\\.[^"\\]*)*"'),  # Строки с экранированием
        ('NAME', r'[A-Z_][A-Z0-9_]*'),  # Имена констант (заглавные буквы и цифры)
        ('ARRAY', r'array'),  # Ключевое слово array
        ('DEF', r'def'),  # Ключевое слово def
        ('OPERATOR', r'\+|\-|\*|\/|chr|len'),  # Операторы и функции
        ('LBRACE', r'\{'),  # {
        ('RBRACE', r'\}'),  # }
        ('LPAREN', r'\('),  # (
        ('RPAREN', r'\)'),  # )
        ('LBRACKET', r'\['),  # [
        ('RBRACKET', r'\]'),  # ]
        ('COLON', r':'),  # :
        ('COMMA', r','),  # ,
        ('SEMICOLON', r';'),  # ;
        ('WHITESPACE', r'\s+'),  # Пробельные символы
    ]

    def __init__(self, text):
        self.text = text
        self.tokens = []
        self.line = 1
        self.column = 1
        self.pos = 0

    def tokenize(self):
        """Разбивает текст на токены"""
        while self.pos < len(self.text):
            matched = False

            # Пропускаем комментарии и пробелы, но учитываем переводы строк
            for token_type, pattern in self.tokens_regex:
                regex = re.compile(pattern)
                match = regex.match(self.text, self.pos)

                if match:
                    matched = True
                    value = match.group(0)
                    start_pos = self.pos
                    self.pos = match.end()

                    # Обновляем счетчик строк и столбцов
                    lines = value.count('\n')
                    if lines > 0:
                        self.line += lines
                        last_newline = value.rfind('\n')
                        self.column = len(value) - last_newline
                    else:
                        self.column += len(value)

                    # Сохраняем только значимые токены
                    if token_type not in ('COMMENT', 'WHITESPACE'):
                        token = Token(token_type, value,
                                      self.line - lines if lines > 0 else self.line,
                                      self.column - len(value) if lines == 0 else 1)
                        self.tokens.append(token)

                    break

            if not matched:
                # Нераспознанный символ
                raise LexerError(
                    f"Unexpected character: '{self.text[self.pos]}'",
                    self.line, self.column
                )

        return self.tokens

