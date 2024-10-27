from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor

def run():
    app = QApplication.instance()
    if app:
        # Меняем цвет фона главного окна
        new_color = QColor(100, 150, 200)  # Задаем новый цвет (RGB)
        app.setStyleSheet(f"background-color: {new_color.name()};")
        print('Цвет фона изменен!')
    else:
        print('Приложение не запущено, цвет фона не может быть изменен.')
