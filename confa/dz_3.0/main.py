import re
import math

class ConfigToToml:
    def __init__(self):
        self.constants = {}  # Хранение констант
        self.current_scope = {}  # Хранение текущего состояния
        self.line_num = 0  # Номер строки для отслеживания ошибок

    def evaluate(self, expr):
        """Вычисление значения (числа, строки, постфиксные выражения)."""
        if re.match(r"^\d+(\.\d+)?$", expr):  # Число
            return float(expr) if '.' in expr else int(expr)
        elif re.match(r"^'.*'$", expr):  # Строка
            return expr.strip("'")
        elif expr in self.constants:  # Константа
            return self.constants[expr]
        elif expr.startswith("|") and expr.endswith("|"):  # Постфиксное выражение
            return self.evaluate_postfix(expr[1:-1].strip())
        else:
            raise ValueError(f"Unknown token in expression: {expr}")

    def evaluate_postfix(self, expr):
        """Вычисление постфиксных выражений (например, |CONST 2 *|)."""
        tokens = expr.split()
        stack = []
        for token in tokens:
            if re.match(r"^\d+(\.\d+)?$", token):  # Число
                stack.append(float(token) if '.' in token else int(token))
            elif token in self.constants:  # Константа
                stack.append(self.constants[token])
            elif token in "+-*/":  # Операции
                b = stack.pop()
                a = stack.pop()
                if token == "+":
                    stack.append(a + b)
                elif token == "-":
                    stack.append(a - b)
                elif token == "*":
                    stack.append(a * b)
                elif token == "/":
                    stack.append(a / b)
            elif token == "sqrt":  # Квадратный корень
                a = stack.pop()
                stack.append(math.sqrt(a))
            elif token == "ord":  # Функция ord()
                a = stack.pop()
                stack.append(ord(str(a)))
            else:
                raise ValueError(f"Unknown token in expression: {token}")
        if len(stack) != 1:
            raise ValueError(f"Invalid postfix expression: {expr}")
        return stack.pop()

    def process_array(self, text):
        """Парсинг массива."""
        items = text[1:-1].split(";")  # Убираем квадратные скобки и разделяем элементы
        return [self.evaluate(item.strip()) for item in items if item.strip()]

    def process_dict(self, text):
        """Парсинг словаря."""
        text = text[1:-1].strip()  # Убираем фигурные скобки и пробелы
        items = text.split(";")  # Разделяем элементы словаря по ;
        result = {}
        for item in items:
            if "=" in item:
                name, value = map(str.strip, item.split("=", 1))
                result[name] = self.evaluate(value)
        return result

    def process_line(self, line):
        """Обработка строки входного текста."""
        self.line_num += 1
        # Удаляем лишний символ ; в конце строки
        if line.endswith(";"):
            line = line[:-1].strip()

        # Обработка констант
        if ":=" in line:
            name, value = map(str.strip, line.split(":=", 1))
            self.constants[name] = self.evaluate(value)
        # Присваивание значения
        elif "=" in line:
            name, value = map(str.strip, line.split("=", 1))
            if value.startswith("[") and value.endswith("]"):  # Массив
                self.current_scope[name] = self.process_array(value)
            elif value.startswith("{") and value.endswith("}"):  # Словарь
                self.current_scope[name] = self.process_dict(value)
            else:
                self.current_scope[name] = self.evaluate(value)
        else:
            raise SyntaxError(f"Invalid syntax on line {self.line_num}: {line}")

    def process(self, input_text):
        """Основной процесс парсинга."""
        for line in input_text.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("(comment"):  # Игнорируем комментарии
                continue
            self.process_line(line)

    def to_toml(self):
        """Преобразование результата в TOML."""
        result = []
        for key, value in self.current_scope.items():
            if isinstance(value, dict):  # Словарь
                result.append(f"[{key}]")
                for sub_key, sub_value in value.items():
                    result.append(f"{sub_key} = {self.format_value(sub_value)}")
            else:
                result.append(f"{key} = {self.format_value(value)}")
        return "\n".join(result)

    def format_value(self, value):
        """Форматирование значения для TOML."""
        if isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, list):
            return f"[{', '.join(map(str, value))}]"
        else:
            return str(value)

if __name__ == "__main__":
    import sys
    input_text = sys.stdin.read()
    parser = ConfigToToml()
    try:
        parser.process(input_text)
        print(parser.to_toml())
    except Exception as e:
        print(f"Error: {e}")
