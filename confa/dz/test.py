import unittest
import tkinter as tk
from zipfile import ZipFile
from io import BytesIO
from main import EmulatorGUI  # Замените your_script_name на имя вашего файла


class TestEmulatorGUI(unittest.TestCase):
    def setUp(self):
        # Создаем временный ZIP-файл в памяти
        self.test_zip = BytesIO()
        with ZipFile(self.test_zip, 'w') as zipf:
            zipf.writestr("dir1/file1.txt", "Content of file1")
            zipf.writestr("dir1/file2.txt", "Content of file2")
            zipf.writestr("dir2/file3.txt", "Content of file3")

        self.test_zip.seek(0)

        # Создаем интерфейс, связанный с этим ZIP-файлом
        self.root = tk.Tk()
        self.app = EmulatorGUI(self.root)
        self.app.myzip = ZipFile(self.test_zip, 'a')  # Используем тестовый ZIP

    def tearDown(self):
        self.app.myzip.close()
        self.root.destroy()

    def test_ls(self):
        self.app.entry.insert(0, "ls")
        self.app.process_command(None)
        output = self.app.output.get(1.0, tk.END).strip()
        self.assertIn("dir1", output)
        self.assertIn("dir2", output)

    def test_cd(self):
        self.app.entry.insert(0, "cd dir1")
        self.app.process_command(None)
        self.assertEqual(self.app.current_dir, "dir1/")

        self.app.entry.insert(0, "ls")
        self.app.process_command(None)
        output = self.app.output.get(1.0, tk.END).strip()
        self.assertIn("file1.txt", output)
        self.assertIn("file2.txt", output)

    def test_cat(self):
        self.app.entry.insert(0, "cat dir1/file1.txt")
        self.app.process_command(None)
        output = self.app.output.get(1.0, tk.END).strip()
        self.assertIn("Content of file1", output)

    def test_touch(self):
        self.app.entry.insert(0, "touch new_file.txt")
        self.app.process_command(None)
        output = self.app.output.get(1.0, tk.END).strip()
        self.assertIn("Файл new_file.txt создан", output)

        # Проверяем, что файл появился в ZIP
        self.assertIn("new_file.txt", self.app.myzip.namelist())

    def test_du(self):
        self.app.entry.insert(0, "cd dir1")
        self.app.process_command(None)

        self.app.entry.insert(0, "du")
        self.app.process_command(None)
        output = self.app.output.get(1.0, tk.END).strip()
        self.assertIn("Размер текущей директории", output)

    def test_invalid_command(self):
        self.app.entry.insert(0, "invalid_cmd")
        self.app.process_command(None)
        output = self.app.output.get(1.0, tk.END).strip()
        self.assertIn("Неизвестная команда", output)


if __name__ == "__main__":
    unittest.main()
