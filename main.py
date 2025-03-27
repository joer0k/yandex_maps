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
        self.btn_del.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.edit_search.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.btn_light.toggled.connect(self.change_theme)
        self.btn_search.clicked.connect(self.search)
        self.btn_del.clicked.connect(self.delete)
        self.checkbox_index.stateChanged.connect(self.search)
        self.refresh_map()

    def delete(self):
        res = get_ll(self.edit_search.text())
        if res:
            data = ','.join(map(str, self.map_ll))
            if data in self.points:
                self.points.remove(data)
                self.label_result.setText('')
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
                if self.checkbox_index.isChecked():
                    if 'postal_code' in res['metaDataProperty']['GeocoderMetaData']['Address']:
                        self.label_result.setText(
                            f'Полный адрес: {res['metaDataProperty']['GeocoderMetaData']['text']}\n'
                            f'Почтовый индекс: '
                            f'{res['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']}')
                    else:
                        self.label_result.setText(
                            f'Полный адрес: {res['metaDataProperty']['GeocoderMetaData']['text']}\n'
                            f'Почтовый индекс: отсутствует')
                else:
                    self.label_result.setText(f'Полный адрес: {res['metaDataProperty']['GeocoderMetaData']['text']}')
                self.label_error.setText('')
                self.refresh_map()
            else:
                self.label_error.setText('Ничего не найдено, попробуйте снова')
        else:
            self.label_error.setText('Неверный запрос')

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
        if event.key() == Qt.Key.Key_Return:
            self.search()
        if event.key() == Qt.Key.Key_Escape:  # нужно чтобы нажатия стрелочек не фокусировались на других кнопках
            self.edit_search.clearFocus()
            self.btn_search.clearFocus()
            self.btn_del.clearFocus()
        self.refresh_map()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
