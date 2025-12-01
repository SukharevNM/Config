class ConfigLanguageError(Exception):
    """Базовый класс для ошибок языка конфигурации"""
    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self._format_message())

    def _format_message(self):
        if self.line is not None:
            if self.column is not None:
                return f"Error at line {self.line}, column {self.column}: {self.message}"
            return f"Error at line {self.line}: {self.message}"
        return f"Error: {self.message}"


class LexerError(ConfigLanguageError):
    """Ошибка лексического анализа"""
    pass


class ParserError(ConfigLanguageError):
    """Ошибка синтаксического анализа"""
    pass


class EvaluationError(ConfigLanguageError):
    """Ошибка вычисления"""
    pass


class NameError(ConfigLanguageError):
    """Ошибка - имя не найдено"""
    pass
