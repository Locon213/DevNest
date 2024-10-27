import sys
import io
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QTabWidget, QStatusBar, QTextEdit, QFileDialog,
    QPlainTextEdit, QVBoxLayout, QWidget, QInputDialog, QMenu, QColorDialog, QListWidget,
    QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from syntax_highlighter import PythonHighlighter
from git import Repo
import webbrowser

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

        self.setLayout(self.layout)

        self.load_plugins()

    def load_plugins(self):
        # Здесь можно загрузить список плагинов с GitHub
        plugins = ["Plugin1", "Plugin2", "Plugin3"]  # Пример списка плагинов
        self.plugin_list.addItems(plugins)

    def install_plugin(self):
        selected_plugin = self.plugin_list.currentItem()
        if selected_plugin:
            plugin_name = selected_plugin.text()
            # Загрузка и установка плагина
            self.download_plugin(plugin_name)

    def download_plugin(self, plugin_name):
        # Здесь будет логика для загрузки плагина с GitHub
        url = f"https://github.com/your-repo/{plugin_name}/archive/refs/heads/main.zip"
        try:
            response = requests.get(url)
            with open(f"{plugin_name}.zip", "wb") as f:
                f.write(response.content)
            QMessageBox.information(self, "Успех", f"Плагин {plugin_name} успешно установлен.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось установить плагин: {str(e)}")

class DevNest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DevNest")
        self.setGeometry(100, 100, 1000, 700)

        self.repo = None
        self.copilot_token = None
        
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
        
        open_action = QAction("Открыть", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

        run_action = QAction("Запустить", self)
        run_action.triggered.connect(self.run_python_code)
        toolbar.addAction(run_action)

        # Меню плагинов
        plugins_action = QAction("Управление плагинами", self)
        plugins_action.triggered.connect(self.open_plugin_manager)
        toolbar.addAction(plugins_action)

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

    def open_plugin_manager(self):
        self.plugin_manager = PluginManager()
        self.plugin_manager.show()


class Logger(io.StringIO):
    def __init__(self, log_terminal):
        super().__init__()
        self.log_terminal = log_terminal

    def write(self, message):
        if message.strip():
            self.log_terminal.appendPlainText(message.strip())

    def flush(self):
        pass

class DevNest(QMainWindow):
    def __init__(self):
        super().__init__()
        print("DevNest initialized")
        self.setWindowTitle("DevNest")
        self.setGeometry(100, 100, 1000, 700)

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

        open_action = QAction("Открыть", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

        run_action = QAction("Запустить", self)
        run_action.triggered.connect(self.run_python_code)
        toolbar.addAction(run_action)

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
        client_id = "Ov23lif7mJuFTnC7hduO"
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
                editor.append(f"\n# Copilot Suggestion:\n{suggestion}")
                self.log_message("Получено предложение от Copilot")

    def request_copilot_suggestion(self, code):
        if not self.copilot_token:
            self.log_message("Токен Copilot не задан. Пожалуйста, введите токен.")
            return None
        api_url = "https://api.github.com/copilot/suggestions"
        headers = {
            "Authorization": f"token {self.copilot_token}",
            "Content-Type": "application/json"
        }
        data = {"prompt": code, "max_tokens": 100}
        try:
            response = requests.post(api_url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json().get("choices", [])[0].get("text")
            else:
                self.log_message(f"Ошибка при запросе к Copilot API: {response.status_code}")
                return None
        except Exception as e:
            self.log_message(f"Ошибка подключения к Copilot API: {str(e)}")
            return None

    def set_default_theme(self):
        self.setStyleSheet("")

    def set_dark_theme(self):
        self.setStyleSheet("background-color: #2b2b2b; color: #f0f0f0;")

    def customize_theme(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.setStyleSheet(f"background-color: {color.name()}; color: white;")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
            editor = self.get_current_editor()
            if editor:
                editor.setPlainText(content)
            self.log_message(f"Файл открыт: {file_path}")

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            editor = self.get_current_editor()
            if editor:
                content = editor.toPlainText()
                with open(file_path, "w") as file:
                    file.write(content)
                self.log_message(f"Файл сохранен: {file_path}")

    def run_python_code(self):
        editor = self.get_current_editor()
        if editor:
            code = editor.toPlainText()
            temp_stdout = io.StringIO()
            sys.stdout = temp_stdout
            sys.stderr = temp_stdout
            try:
                exec(code, {})
                output = temp_stdout.getvalue()
                self.log_message("Результат выполнения:\n" + output)
            except Exception as e:
                self.log_message("Ошибка выполнения:\n" + str(e))
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

    def add_new_tab(self, content=""):
        editor = QTextEdit()
        editor.setFont(QFont(self.selected_font, 12))  # Применение выбранного шрифта
        PythonHighlighter(editor)  # Применение подсветки синтаксиса
        editor.setPlainText(content)
        self.tab_widget.addTab(editor, "Новая вкладка")

    def get_current_editor(self):
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            return self.tab_widget.widget(current_index)
        return None

    def log_message(self, message):
        self.log_terminal.appendPlainText(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    devnest = DevNest()
    devnest.show()
    sys.exit(app.exec_())
