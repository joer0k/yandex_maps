import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from utils import get_static_api_image
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import uic


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.map_ll = [38.913250, 45.038852]
        self.z = 17
        uic.loadUi('untitled.ui', self)  # Загружаем дизайн
        self.refresh_map()

    def refresh_map(self):
        response = get_static_api_image(self.map_ll, z=self.z)
        if response:
            with open('image.png', mode='wb') as file:
                file.write(response)
            pixmap = QPixmap()
            pixmap.load('image.png')
            self.label.setPixmap(pixmap)
            self.label.setScaledContents(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            self.z = min(self.z + 1, 21)
        if event.key() == Qt.Key.Key_PageDown:
            self.z = max(self.z - 1, 0)
        self.refresh_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
