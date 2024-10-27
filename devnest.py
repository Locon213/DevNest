import sys
import io
import os
import base64
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QTabWidget, QStatusBar, QTextEdit, QFileDialog,
    QPlainTextEdit, QVBoxLayout, QWidget, QInputDialog, QMenu, QColorDialog, QListWidget,
    QPushButton, QMessageBox, QFontDialog,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont,QIcon
from syntax_highlighter import PythonHighlighter
from git import Repo
import webbrowser
import importlib
import builtins
import venv

GITHUB_TOKEN = 'Secret(NOPUBLIC)'
REPO_NAME = 'Locon213/DevNest'  #
LIBS_FOLDER = 'libs'  


class Logger(io.StringIO):
    def __init__(self, log_terminal):
        super().__init__()
        self.log_terminal = log_terminal

    def write(self, message):
        if message.strip():
            self.log_terminal.appendPlainText(message.strip())

    def flush(self):
        pass

class PluginManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление плагинами")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.plugin_list = QListWidget()
        self.layout.addWidget(self.plugin_list)

        self.install_button = QPushButton("Установить плагин")
        self.install_button.clicked.connect(self.install_plugin)
        self.layout.addWidget(self.install_button)

        self.create_plugin_button = QPushButton("Создать новый плагин")
        self.create_plugin_button.clicked.connect(self.create_plugin)
        self.layout.addWidget(self.create_plugin_button)

        # Создание поля для логов
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)  # Сделаем текстовое поле только для чтения
        self.layout.addWidget(self.log_output)

        self.setLayout(self.layout)

        self.load_plugins()

    def log(self, message):
        """Метод для записи сообщений в логовое поле."""
        self.log_output.append(message)

    def load_plugins(self):
        # URL для получения списка плагинов из репозитория
        repo_url = f'https://api.github.com/repos/{REPO_NAME}/contents/{LIBS_FOLDER}'
        try:
            response = requests.get(repo_url,timeout=30)
            response.raise_for_status()  # Проверка на ошибки

            # Получение списка плагинов из ответа
            plugins = [item['name'] for item in response.json() if item['type'] == 'dir']
            self.plugin_list.addItems(plugins)
        except requests.RequestException as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить плагины: {str(e)}")

    def install_plugin(self):
        selected_plugin = self.plugin_list.currentItem()
        if selected_plugin:
            plugin_name = selected_plugin.text()
            self.load_plugin(plugin_name)

    def load_plugin(self, plugin_name):
        # Удаление плагина из кэша модулей
        if plugin_name in sys.modules:
            del sys.modules[plugin_name]

        # Загрузка и инициализация плагина
        plugin_path = f'https://raw.githubusercontent.com/{REPO_NAME}/main/{LIBS_FOLDER}/{plugin_name}/plugin.py'
        try:
            response = requests.get(plugin_path,timeout=30)
            response.raise_for_status()  # Проверка на ошибки

            # Импортирование плагина
            spec = importlib.util.spec_from_loader(plugin_name, loader=None)
            plugin_module = importlib.util.module_from_spec(spec)

            # Создание объекта StringIO для захвата вывода
            output_capture = io.StringIO()
            original_stdout = sys.stdout  # Сохраняем оригинальный стандартный вывод
            sys.stdout = output_capture  # Перенаправляем стандартный вывод

            # Выполнение кода плагина
            exec(response.text, plugin_module.__dict__)

            # Если в плагине есть функция `run`, вызовем её
            if hasattr(plugin_module, 'run'):
                # Запускаем функцию run внутри DevNest
                plugin_module.run()
                output = output_capture.getvalue()  # Получаем все, что было выведено
                self.log(output)  # Записываем вывод в лог

                self.log(f"Плагин '{plugin_name}' успешно загружен и выполнен.")
            else:
                self.log(f"Ошибка: в плагине '{plugin_name}' не найдена функция 'run'.")
            
            # Восстанавливаем оригинальный стандартный вывод
            sys.stdout = original_stdout
        except requests.RequestException as e:
            self.log(f"Ошибка: не удалось загрузить плагин: {str(e)}")
        except Exception as e:
            self.log(f"Ошибка при загрузке плагина: {str(e)}")
        finally:
            # Убедимся, что стандартный вывод всегда восстанавливается
            sys.stdout = original_stdout

    def create_plugin(self):
        plugin_name, ok = QInputDialog.getText(self, "Создание плагина", "Введите имя нового плагина:")
        if ok and plugin_name:
            # Создание плагина на GitHub
            self.create_plugin_on_github(plugin_name)

    def create_plugin_on_github(self, plugin_name):
        url = f'https://api.github.com/repos/{REPO_NAME}/contents/{LIBS_FOLDER}/{plugin_name}/plugin.py'
        content = '''print("Hello, World!")\n\ndef run():\n    print("Плагин запущен!")\n'''

        # Подготовка данных для запроса
        data = {
            "message": f"Создан плагин {plugin_name}",
            "content": self.encode_content(content)
        }

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            response = requests.put(url, json=data, headers=headers,timeout=30)
            response.raise_for_status()  # Проверка на ошибки

            QMessageBox.information(self, "Успех", 
                                    f"Плагин '{plugin_name}' успешно создан! \n\n"
                                    f"Перейдите по ссылке для редактирования: "
                                    f"https://github.com/{REPO_NAME}/tree/main/{LIBS_FOLDER}/{plugin_name}")

            self.load_plugins()  # Обновляем список плагинов
        except requests.RequestException as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать плагин: {str(e)}")

    @staticmethod
    def encode_content(content):
        """ Кодирование контента в base64 для GitHub API. """
        return base64.b64encode(content.encode()).decode()

class DevNest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.virtual_env_path = os.path.join(os.path.dirname(__file__), 'venv')
        self.setWindowTitle("DevNest")
        self.setGeometry(100, 100, 1000, 700)
        self.setWindowIcon(QIcon("logo.ico"))  # Установка иконки

        self.repo = None
        self.copilot_token = None
        self.selected_font = "Courier New"  # Шрифт по умолчанию

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.create_toolbar()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.log_terminal = QPlainTextEdit(self)
        self.log_terminal.setReadOnly(True)
        self.log_terminal.setPlaceholderText("Логи будут отображаться здесь...")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.log_terminal)

        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.add_new_tab()



    def create_toolbar(self):
        toolbar = self.addToolBar("Основные операции")
        toolbar.setMovable(False)

        # Меню "Файл"
        file_menu = QMenu("Файл", self)

        # Объединенные действия
        open_action = QAction("Открыть", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        run_action = QAction("Запустить", self)
        run_action.triggered.connect(self.run_python_code)
        file_menu.addAction(run_action)

        toolbar.addAction(file_menu.menuAction())

        # Кнопка для управления плагинами
        plugin_manager_action = QAction("Плагины", self)
        plugin_manager_action.triggered.connect(self.open_plugin_manager)
        toolbar.addAction(plugin_manager_action)

        # Git меню
        git_menu = QMenu("Git", self)
        git_init_action = QAction("Инициализировать Git", self)
        git_init_action.triggered.connect(self.init_git_repo)
        git_menu.addAction(git_init_action)

        git_commit_action = QAction("Commit", self)
        git_commit_action.triggered.connect(self.commit_changes)
        git_menu.addAction(git_commit_action)

        github_auth_action = QAction("GitHub Авторизация", self)
        github_auth_action.triggered.connect(self.github_auth)
        git_menu.addAction(github_auth_action)

        toolbar.addAction(git_menu.menuAction())

        # Copilot действия
        copilot_token_action = QAction("Ввести токен Copilot", self)
        copilot_token_action.triggered.connect(self.set_copilot_token)
        toolbar.addAction(copilot_token_action)

        copilot_suggestion_action = QAction("Copilot Подсказка", self)
        copilot_suggestion_action.triggered.connect(self.get_copilot_suggestion)
        toolbar.addAction(copilot_suggestion_action)

        # Меню тем
        theme_menu = QMenu("Темы", self)
        default_theme_action = QAction("Тема по умолчанию", self)
        default_theme_action.triggered.connect(self.set_default_theme)
        theme_menu.addAction(default_theme_action)

        dark_theme_action = QAction("Темная тема", self)
        dark_theme_action.triggered.connect(self.set_dark_theme)
        theme_menu.addAction(dark_theme_action)

        custom_theme_action = QAction("Настроить тему", self)
        custom_theme_action.triggered.connect(self.customize_theme)
        theme_menu.addAction(custom_theme_action)

        toolbar.addAction(theme_menu.menuAction())

        # Действие выбора шрифта
        change_font_action = QAction("Выбрать шрифт", self)
        change_font_action.triggered.connect(self.select_font)
        toolbar.addAction(change_font_action)

    def open_plugin_manager(self):
        self.plugin_manager = PluginManager()
        self.plugin_manager.show()

    def select_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.selected_font = font.family()
            editor = self.get_current_editor()
            if editor:
                editor.setFont(font)
            self.log_message(f"Выбранный шрифт: {self.selected_font}")

    def set_copilot_token(self):
        token, ok = QInputDialog.getText(self, "Ввести токен GitHub Copilot", "Введите свой токен GitHub:")
        if ok and token:
            self.copilot_token = token
            self.log_message("Токен GitHub Copilot сохранен.")

    def init_git_repo(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку для репозитория Git")
        if directory:
            self.repo = Repo.init(directory)
            self.log_message(f"Инициализирован новый репозиторий Git в {directory}")

    def commit_changes(self):
        if self.repo:
            self.repo.git.add(A=True)
            commit_message, ok = QInputDialog.getText(self, "Сообщение коммита", "Введите сообщение коммита:")
            if ok:
                self.repo.index.commit(commit_message)
                self.log_message("Изменения закоммичены с сообщением: " + commit_message)
        else:
            self.log_message("Репозиторий Git не инициализирован.")

    def github_auth(self):
        client_id = "NO PUBLIC"
        scope = "repo"
        auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope={scope}"
        try:
            webbrowser.open(auth_url)
            self.log_message("Открыта страница для авторизации GitHub")
        except Exception as e:
            self.log_message(f"Ошибка при открытии страницы авторизации: {str(e)}")

    def get_copilot_suggestion(self):
        editor = self.get_current_editor()
        if editor:
            code = editor.toPlainText()
            suggestion = self.request_copilot_suggestion(code)
            if suggestion:
                editor.append(suggestion)

    def request_copilot_suggestion(self, code):
        api_url = "https://api.github.com/copilot/suggestions"  # Это примерный URL; замените на актуальный
        headers = {"Authorization": f"Bearer {self.copilot_token}"}
        data = {"code": code}
        response = requests.post(api_url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json().get("suggestion")
        else:
            self.log_message(f"Ошибка при запросе: {response.status_code}, {response.text}")
            return None

    def set_default_theme(self):
        self.setStyleSheet("")
        self.log_message("Выбрана тема по умолчанию.")

    def set_dark_theme(self):
        dark_style = """
            QMainWindow { background-color: #2E2E2E; }
            QTabWidget { background-color: #2E2E2E; color: #FFFFFF; }
            QPlainTextEdit { background-color: #2E2E2E; color: #FFFFFF; }
            QToolBar { background-color: #3E3E3E; }
            QMenuBar { background-color: #3E3E3E; color: #FFFFFF; }
            QMenu { background-color: #3E3E3E; color: #FFFFFF; }
            QStatusBar { background-color: #3E3E3E; color: #FFFFFF; }
        """
        self.setStyleSheet(dark_style)
        self.log_message("Выбрана темная тема.")

    def customize_theme(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.setStyleSheet(f"QMainWindow {{ background-color: {color.name()}; }}")
            self.log_message("Тема настроена.")

    def log_message(self, message):
        self.log_terminal.appendPlainText(message)

    def update_status_bar(self):
        editor = self.get_current_editor()
        if editor:
            text_length = len(editor.toPlainText())
            self.status_bar.showMessage(f"Количество символов: {text_length}")

    def add_new_tab(self):
        editor = QTextEdit()
        editor.setFont(QFont(self.selected_font, 10))
        self.tab_widget.addTab(editor, "Новая вкладка")

        highlighter = PythonHighlighter(editor.document())
        editor.textChanged.connect(self.update_status_bar)  # Подключение сигнала к методу обновления статус-бара

    def get_current_editor(self):
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            return self.tab_widget.widget(current_index)
        return None

    def open_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'r') as f:
                code = f.read()
            editor = self.get_current_editor()
            if editor:
                editor.setPlainText(code)
            self.log_message(f"Файл '{file_path}' открыт.")

    def save_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Python Files (*.py);;All Files (*)", options=options)
        if file_path:
            editor = self.get_current_editor()
            if editor:
                with open(file_path, 'w') as f:
                    f.write(editor.toPlainText())
            self.log_message(f"Файл '{file_path}' сохранен.")

    def run_python_code(self):
     editor = self.get_current_editor()
     if editor:
        code = editor.toPlainText()
        
        # Сохраняем оригинальный sys.stdout, чтобы восстановить его позже
        original_stdout = sys.stdout

        try:
            # Перенаправляем вывод в лог
            sys.stdout = Logger(self.log_terminal)
            
            # Определяем безопасные встроенные функции
            safe_builtins = {key: value for key, value in builtins.__dict__.items() if key in ['print', 'len', 'range']}

            # Выполняем код с доступом к определенным безопасным встроенным функциям
            exec(code, {"__builtins__": safe_builtins})

            self.log_message("Код успешно выполнен.")
        except Exception as e:
            self.log_message(f"Ошибка выполнения кода: {str(e)}")
        finally:
            # Восстанавливаем оригинальный sys.stdout
            sys.stdout = original_stdout


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dev_nest = DevNest()
    dev_nest.show()
    sys.exit(app.exec_())
