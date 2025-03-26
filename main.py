import os
import sys

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QApplication

from utils import get_static_api_image


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.map_ll = [38.913250, 45.038852]
        self.z = 10
        uic.loadUi('untitled.ui', self)  # Загружаем дизайн
        self.refresh_map()

    def refresh_map(self):
        response = get_static_api_image(self.map_ll, z=self.z, size=[self.width(), self.height()])
        if response:
            with open('image.png', mode='wb') as file:
                file.write(response)
            pixmap = QPixmap()
            pixmap.load('image.png')
            self.label.resize(pixmap.size())
            self.label.setPixmap(pixmap)
            os.remove('image.png')

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
        self.refresh_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
