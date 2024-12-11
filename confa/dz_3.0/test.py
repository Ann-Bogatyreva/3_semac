import unittest
from io import StringIO
import sys
from main import ConfigToToml  # Импортируем ваш класс из файла config_to_toml.py

class TestConfigToToml(unittest.TestCase):
    def setUp(self):
        """Инициализация экземпляра ConfigToToml перед каждым тестом."""
        self.parser = ConfigToToml()

    def parse_and_get_output(self, input_text):
        """Парсинг текста и возврат результата TOML."""
        self.parser.process(input_text)
        return self.parser.to_toml()

    def test_constants(self):
        """Тест на объявление и использование констант."""
        input_text = """
        CONST := 42
        PI := 3.14
        value = CONST
        """
        expected_output = "value = 42"
        output = self.parse_and_get_output(input_text)
        self.assertEqual(output, expected_output)

    def test_arrays(self):
        """Тест на обработку массивов."""
        input_text = """
        CONST := 10
        numbers = [1; 2; CONST]
        """
        expected_output = "numbers = [1, 2, 10]"
        output = self.parse_and_get_output(input_text)
        self.assertEqual(output, expected_output)

    def test_dicts(self):
        """Тест на обработку словарей."""
        input_text = """
        PI := 3.14
        data = { key = 'value'; another = PI }
        """
        expected_output = "[data]\nkey = 'value'\nanother = 3.14"
        output = self.parse_and_get_output(input_text)
        self.assertEqual(output, expected_output)

    def test_postfix_expressions(self):
        """Тест на обработку постфиксных выражений."""
        input_text = """
        CONST := 10
        result := |CONST 2 *|
        value = result
        """
        expected_output = "value = 20"
        output = self.parse_and_get_output(input_text)
        self.assertEqual(output, expected_output)

    def test_ord_function(self):
        """Тест на функцию ord()."""
        input_text = """
        CHAR := |'A' ord|
        value = CHAR
        """
        expected_output = "value = 65"  # Код символа 'A' в таблице ASCII
        output = self.parse_and_get_output(input_text)
        self.assertEqual(output, expected_output)

    def test_multiline_comment(self):
        """Тест на обработку многострочных комментариев."""
        input_text = """
        (comment
        Это многострочный комментарий.
        Он должен быть проигнорирован.
        )
        CONST := 42
        value = CONST
        """
        expected_output = "value = 42"
        output = self.parse_and_get_output(input_text)
        self.assertEqual(output, expected_output)

    def test_combined_features(self):
        """Тест на комбинацию всех возможностей."""
        input_text = """
        CONST := 42
        PI := 3.14
        result := |CONST 2 *|
        value = result
        numbers = [1; 2; CONST]
        data = { key = 'value'; another = PI }
        (comment
        Это пример комментария
        )
        """
        expected_output = (
            "value = 84\n"
            "numbers = [1, 2, 42]\n"
            "[data]\n"
            "key = 'value'\n"
            "another = 3.14"
        )
        output = self.parse_and_get_output(input_text)
        self.assertEqual(output, expected_output)

    def test_invalid_syntax(self):
        """Тест на обработку ошибок синтаксиса."""
        input_text = """
        CONST := 42
        invalid line
        """
        with self.assertRaises(SyntaxError):
            self.parser.process(input_text)

if __name__ == "__main__":
    unittest.main()
