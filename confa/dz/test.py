import pytest
from zipfile import ZipFile
import os

# Тестируемая функция (в вашем случае это основной код)
def test_zip_commands():
    # Создаем временный zip-файл для тестирования
    zip_file_path = "test.zip"

    # Создаем zip-файл и добавляем некоторые файлы
    with ZipFile(zip_file_path, 'w') as myzip:
        myzip.writestr("file1.txt", "Hello World!")
        myzip.writestr("dir1/file2.txt", "Hello from dir1!")
        myzip.writestr("dir2/file3.txt", "Hello from dir2!")

    # Теперь мы можем тестировать команды
    with ZipFile(zip_file_path, 'a') as myzip:
        current_dir = ""

        # Тест команды ls
        items = set()
        for name in myzip.namelist():
            if name.startswith(current_dir):
                relative_name = name[len(current_dir):].split('/')[0]
                items.add(relative_name)
        assert sorted(items) == sorted(["dir1", "dir2", "file1.txt"])

        # Тест команды cat
        content = myzip.read("file1.txt").decode()
        assert content == "Hello World!"

        # Тест команды cd
        current_dir = "dir1/"
        items = set()
        for name in myzip.namelist():
            if name.startswith(current_dir):
                relative_name = name[len(current_dir):].split('/')[0]
                items.add(relative_name)
        assert sorted(items) == sorted(["file2.txt"])

        # Тест команды du
        def get_dir_size(myzip, dir_path):
            total_size = 0
            for name in myzip.namelist():
                if name.startswith(dir_path):
                    info = myzip.getinfo(name)
                    total_size += info.file_size
            return total_size

        size = get_dir_size(myzip, current_dir)
        assert size == len("Hello from dir1!")  # Размер содержимого file2.txt

        # Тест команды touch
        new_file = "dir1/new_file.txt"
        if new_file not in myzip.namelist():
            myzip.writestr(new_file, "")
            assert new_file in myzip.namelist()

    # Удаляем временный zip-файл после тестирования
    os.remove(zip_file_path)

if __name__ == "__main__":
    pytest.main()
