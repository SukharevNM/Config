import sys
import json
import argparse
from pathlib import Path

# Импортируем наши модули
try:
    from lexer import Lexer
    from parser import Parser
    from evaluator import Evaluator
    from error import ConfigLanguageError
except ImportError:
    # Если модули в той же директории
    import os
    import importlib.util
    # Динамический импорт
    from lexer import Lexer
    from parser import Parser
    from evaluator import Evaluator
    from error import ConfigLanguageError


def load_config_file(filepath):
    """Загружает текст конфигурационного файла"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)


def translate_to_json(config_text):
    """Преобразует текст конфигурации в JSON"""
    try:
        # Лексический анализ
        lexer = Lexer(config_text)
        tokens = lexer.tokenize()

        # Синтаксический анализ
        parser = Parser(tokens)

        # Вычисление
        evaluator = Evaluator(parser)
        result = evaluator.evaluate()

        # Преобразование в JSON
        return json.dumps(result, indent=2, ensure_ascii=False)

    except ConfigLanguageError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Translate configuration language to JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input config.txt
  %(prog)s -i example.conf
        """
    )

    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help='Path to input configuration file'
    )

    args = parser.parse_args()

    # Проверяем существование файла
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Загружаем и обрабатываем файл
    config_text = load_config_file(args.input)
    json_output = translate_to_json(config_text)

    # Выводим результат
    print(json_output)


if __name__ == '__main__':
    main()