from zipfile import ZipFile

def get_dir_size(myzip, dir_path):
    # Вычисляем общий размер файлов в текущей директории
    total_size = 0
    for name in myzip.namelist():
        if name.startswith(dir_path):
            info = myzip.getinfo(name)
            total_size += info.file_size
    return total_size

with ZipFile("rar.zip", 'a') as myzip:
    current_dir = ""

    while True:
        command = input(f"> rar.zip/{current_dir} ")

        if command == 'ls':
            # Список файлов и директорий в текущей директории
            items = set()
            for name in myzip.namelist():
                if name.startswith(current_dir):
                    relative_name = name[len(current_dir):].split('/')[0]
                    items.add(relative_name)
            for item in sorted(items):
                print(item)

        elif command == "exit":
            break

        elif command.startswith('cat '):
            file_path = command.split()[1]
            # Добавляем текущий путь к файлу, если он не абсолютный
            full_path = current_dir + file_path if not file_path.startswith('/') else file_path
            try:
                content = myzip.read(full_path).decode()
                print(content)
            except KeyError:
                print(f"cat: {file_path}: Нет такого файла")

        elif command.startswith('cd '):
            target_dir = command.split()[1]
            # Проверяем, если это перемещение в корень
            if target_dir == "/":
                current_dir = ""
            else:
                # Генерация нового пути
                if target_dir.startswith("/"):
                    new_dir = target_dir.strip("/") + "/"
                else:
                    new_dir = (current_dir + target_dir).strip("/") + "/"

                # Проверка, существует ли такая директория
                if any(name.startswith(new_dir) for name in myzip.namelist()):
                    current_dir = new_dir
                else:
                    print(f"cd: {target_dir}: Нет такого файла или каталога")

        elif command == "du":
            # Если вызывается команда 'du' для текущей директории
            size = get_dir_size(myzip, current_dir)
            print(f"Размер текущей директории: {size} байт")

        elif command.startswith('touch '):
            file_name = command.split()[1]
            # Создаём новый пустой файл в текущей директории
            full_path = current_dir + file_name if not file_name.startswith('/') else file_name
            if full_path not in myzip.namelist():
                myzip.writestr(full_path, "")
                print(f"Файл {file_name} создан.")
            else:
                print(f"touch: {file_name}: Файл уже существует")

        else:
            print(f"Неизвестная команда: {command}")
