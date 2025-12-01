import math
from error import EvaluationError, NameError


class Evaluator:
    def __init__(self, parser):
        self.parser = parser
        self.constants = {}  # Здесь будут вычисленные значения констант

    def evaluate(self):
        """Вычисляет AST и возвращает результат"""
        # Сначала вычисляем все константы
        self._evaluate_constants()

        # Находим главный словарь (последний узел)
        main_dict = None
        for node in reversed(self.parser.tokens):
            if isinstance(node, dict) or (hasattr(node, 'type') and node.type in ['LBRACKET', 'DICT']):
                # Вернемся к парсеру для поиска главного словаря
                pass

        # Парсим и вычисляем главное выражение
        ast = self.parser.parse()
        return self._evaluate_node(ast)

    def _evaluate_constants(self):
        """Вычисляет значения всех объявленных констант"""
        # Проходим по всем узлам ConstantDefNode
        for name, node in self.parser.constants.items():
            if isinstance(node, ConstantDefNode):
                value = self._evaluate_node(node.value)
                self.constants[name] = value

    def _evaluate_node(self, node):
        """Рекурсивно вычисляет значение узла AST"""
        if isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, NameNode):
            # Поиск значения константы
            if node.name in self.constants:
                return self.constants[node.name]
            else:
                raise NameError(
                    f"Constant '{node.name}' is not defined",
                    getattr(node, 'line', None),
                    getattr(node, 'column', None)
                )
        elif isinstance(node, ArrayNode):
            return [self._evaluate_node(elem) for elem in node.elements]
        elif isinstance(node, DictNode):
            return {key: self._evaluate_node(value) for key, value in node.pairs}
        elif isinstance(node, ExpressionNode):
            return self._evaluate_expression(node)
        elif isinstance(node, ConstantDefNode):
            # При вычислении константы возвращаем ее значение
            return self._evaluate_node(node.value)
        else:
            raise EvaluationError(f"Unknown node type: {type(node)}")

    def _evaluate_expression(self, node):
        """Вычисляет выражение"""
        # Сначала вычисляем все аргументы
        args = [self._evaluate_node(arg) for arg in node.args]

        # Проверяем типы аргументов для некоторых операций
        if node.operator in ('chr', 'len'):
            if len(args) != 1:
                raise EvaluationError(f"Function {node.operator} expects 1 argument, got {len(args)}")

        # Выполняем операцию
        if node.operator == '+':
            # Конкатенация строк или сложение чисел
            if all(isinstance(arg, (int, float)) for arg in args):
                return sum(args)
            elif all(isinstance(arg, str) for arg in args):
                return ''.join(args)
            else:
                # Преобразуем все к строкам и конкатенируем
                return ''.join(str(arg) for arg in args)
        elif node.operator == '-':
            if len(args) != 2:
                raise EvaluationError("Subtraction expects 2 arguments")
            return args[0] - args[1]
        elif node.operator == '*':
            result = 1
            for arg in args:
                result *= arg
            return result
        elif node.operator == '/':
            if len(args) != 2:
                raise EvaluationError("Division expects 2 arguments")
            if args[1] == 0:
                raise EvaluationError("Division by zero")
            return args[0] / args[1]
        elif node.operator == 'chr':
            # Преобразуем число в символ
            if not isinstance(args[0], (int, float)):
                raise EvaluationError("chr() expects a number argument")
            return chr(int(args[0]))
        elif node.operator == 'len':
            # Длина строки или массива
            if isinstance(args[0], str):
                return len(args[0])
            elif isinstance(args[0], list):
                return len(args[0])
            else:
                raise EvaluationError("len() expects string or array argument")
        else:
            raise EvaluationError(f"Unknown operator: {node.operator}")
