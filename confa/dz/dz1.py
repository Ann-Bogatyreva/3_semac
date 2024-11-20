import tkinter as tk
from zipfile import ZipFile

def get_dir_size(myzip, dir_path):
    total_size = 0
    for name in myzip.namelist():
        if name.startswith(dir_path):
            info = myzip.getinfo(name)
            total_size += info.file_size
    return total_size

class EmulatorGUI:
    def __init__(self, master):
        self.master = master
        master.title("ZIP Emulator")
        self.current_dir = ""

        self.history_area = tk.Text(master, wrap='word', height=20, width=50)
        self.history_area.pack(pady=10)
        self.history_area.config(state=tk.NORMAL)  # Разрешаем редактирование для вывода команды
        self.history_area.insert(tk.END, "История команд:\n")  # Заголовок для области истории
        self.history_area.config(state=tk.DISABLED)

        self.entry = tk.Entry(master, width=50)
        self.entry.pack(pady=10)
        self.entry.bind('<Return>', self.process_command)
        self.entry.bind('<Up>', self.previous_command)
        self.entry.bind('<Down>', self.next_command)

        self.output = tk.Text(master, wrap='word', height=10, width=50)
        self.output.pack(pady=10)
        self.output.config(state=tk.DISABLED)

        self.myzip = ZipFile("rar.zip", 'a')
        self.command_history = []  # Список для хранения истории команд
        self.history_index = -1  # Индекс для навигации по истории

    def process_command(self, event):
        command = self.entry.get().strip()
        if command:  # Проверяем, что команда не пустая
            self.command_history.append(command)  # Сохраняем команду в истории
            self.history_index = len(self.command_history)  # Обновляем индекс истории

            # Отображаем команду в области истории
            self.history_area.config(state=tk.NORMAL)  # Разрешаем редактирование
            self.history_area.insert(tk.END, f"> {command}\n")  # Формат команды в консоли
            self.history_area.config(state=tk.DISABLED)

        self.entry.delete(0, tk.END)
        self.output.config(state=tk.NORMAL)
        self.output.delete(1.0, tk.END)

        if command == 'ls':
            items = set()
            for name in self.myzip.namelist():
                if name.startswith(self.current_dir):
                    relative_name = name[len(self.current_dir):].split('/')[0]
                    items.add(relative_name)
            self.output.insert(tk.END, "\n".join(sorted(items)) + "\n")
        elif command == "exit":
            self.master.quit()
        elif command.startswith('cat '):
            file_path = command.split()[1]
            full_path = self.current_dir + file_path if not file_path.startswith('/') else file_path
            try:
                content = self.myzip.read(full_path).decode()
                self.output.insert(tk.END, content + "\n")
            except KeyError:
                self.output.insert(tk.END, f"cat: {file_path}: Нет такого файла\n")
        elif command.startswith('cd '):
            target_dir = command.split()[1]
            if target_dir == "/":
                self.current_dir = ""
            else:
                if target_dir.startswith("/"):
                    new_dir = target_dir.strip("/") + "/"
                else:
                    new_dir = (self.current_dir + target_dir).strip("/") + "/"
                if any(name.startswith(new_dir) for name in self.myzip.namelist()):
                    self.current_dir = new_dir
                else:
                    self.output.insert(tk.END, f"cd: {target_dir}: Нет такого файла или каталога\n")
        elif command == "du":
            size = get_dir_size(self.myzip, self.current_dir)
            self.output.insert(tk.END, f"Размер текущей директории: {size} байт\n")
        elif command.startswith('touch '):
            file_name = command.split()[1]
            full_path = self.current_dir + file_name if not file_name.startswith('/') else file_name
            if full_path not in self.myzip.namelist():
                self.myzip.writestr(full_path, "")
                self.output.insert(tk.END, f"Файл {file_name} создан.\n")
            else:
                self.output.insert(tk.END, f"touch: {file_name}: Файл уже существует\n")
        else:
            self.output.insert(tk.END, f"Неизвестная команда: {command}\n")

        self.output.config(state=tk.DISABLED)

    def previous_command(self, event):
        if self.history_index > 0:
            self.history_index -= 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.command_history[self.history_index])

    def next_command(self, event):
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.command_history[self.history_index])
        else:
            self.history_index = len(self.command_history)  # Сброс индекс, чтобы избежать ошибок в дальнейшем
            self.entry.delete(0, tk.END)  # Очищаем поле ввода

if __name__ == "__main__":
    root = tk.Tk()
    app = EmulatorGUI(root)
    root.mainloop()
