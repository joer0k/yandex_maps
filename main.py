import os
import sys

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QApplication

from utils import get_static_api_image, get_ll


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.map_ll = [38.913250, 45.038852]
        self.z = 10
        self.points = set()
        uic.loadUi('untitled.ui', self)  # Загружаем дизайн
        self.type_map = 'light'
        self.btn_light.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_dark.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_light.toggled.connect(self.change_theme)
        self.btn_search.clicked.connect(self.search)
        self.refresh_map()

    def refresh_map(self):
        response = get_static_api_image(self.map_ll, z=self.z, size=[self.width(), self.height()], theme=self.type_map,
                                        points=self.points)
        if response:
            with open('image.png', mode='wb') as file:
                file.write(response)
            pixmap = QPixmap()
            pixmap.load('image.png')
            self.label.resize(pixmap.size())
            self.label.setPixmap(pixmap)
            os.remove('image.png')

    def change_theme(self):
        if self.btn_light.isChecked():
            self.type_map = 'light'
        elif self.btn_dark.isChecked():
            self.type_map = 'dark'
        self.refresh_map()

    def search(self):
        data = self.edit_search.text()
        if data.strip(' ') != '':
            res = get_ll(data)
            if res:
                self.map_ll = list(map(float, res['Point']['pos'].split()))
                self.points.add(','.join(map(str, res['Point']['pos'].split())))
                self.label_result.setText('')
                self.refresh_map()
            else:
                self.label_result.setText('Ничего не найдено, попробуйте снова')
        else:
            self.label_result.setText('Неверный запрос')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            self.z = min(self.z + 1, 21)
        if event.key() == Qt.Key.Key_PageDown:
            self.z = max(self.z - 1, 0)
        if event.key() == Qt.Key.Key_Right:
            self.map_ll[0] += self.z / 100
        if event.key() == Qt.Key.Key_Left:
            self.map_ll[0] -= self.z / 100
        if event.key() == Qt.Key.Key_Up:
            self.map_ll[1] += self.z / 100
        if event.key() == Qt.Key.Key_Down:
            self.map_ll[1] -= self.z / 100
        if event.key() == Qt.Key.Key_Enter:
            self.search()
        self.refresh_map()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
