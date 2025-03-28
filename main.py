import math
import os
import sys

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMainWindow, QApplication

from utils import get_static_api_image, get_ll, search_organization, get_distance


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.map_ll = [38.913250, 45.038852]
        self.full_address = ''
        self.postcode = ''
        self.z = 10
        self.points = set()
        uic.loadUi('untitled.ui', self)  # Загружаем дизайн
        self.type_map = 'light'
        self.setfocus_buttons()
        self.btn_light.toggled.connect(self.change_theme)
        self.btn_search.clicked.connect(self.search)
        self.btn_del.clicked.connect(self.delete)
        self.checkbox_index.stateChanged.connect(self.show_address)
        self.refresh_map()

    def setfocus_buttons(self):  # чтобы не загромождать init
        self.btn_light.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_dark.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_del.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.edit_search.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.btn_search.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.checkbox_index.setFocusPolicy(Qt.FocusPolicy.NoFocus)

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
            self.statusBar.clearMessage()
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

    def show_address(self):
        if self.points:
            if self.checkbox_index.isChecked():
                self.label_result.setText(
                    f'Полный адрес: {self.full_address}\nПочтовый индекс: {self.postcode}')
            else:
                self.label_result.setText(f'Полный адрес: {self.full_address}')

    def search(self, coords=None, type_point='pmwtm'):
        data = self.edit_search.text()
        if data.strip(' ') != '':
            res = get_ll(data)
            if res:
                if coords is None:
                    self.map_ll = list(map(float, res['Point']['pos'].split()))
                    self.points.add(','.join(map(str, res['Point']['pos'].split())))
                else:
                    self.points.add(coords)
                if 'postal_code' in res['metaDataProperty']['GeocoderMetaData']['Address']:

                    self.full_address = res['metaDataProperty']['GeocoderMetaData']['text']
                    self.postcode = res['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']

                else:
                    self.full_address = res['metaDataProperty']['GeocoderMetaData']['text']
                    self.postcode = 'отсутствует'
                self.statusBar.clearMessage()
                self.show_address()
                self.refresh_map()
            else:
                self.statusBar.showMessage('Ничего не найдено, попробуйте снова')
        else:
            self.statusBar.showMessage('Неверный запрос')

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
            self.edit_organization.clearFocus()
        self.refresh_map()

    def get_coordinates(self, x, y):
        coord_geo_x, coord_geo_y = 0.0000428, 0.0000428
        y = self.label.height() // 2 - y
        x = x - self.label.width() // 2

        lx = float(self.map_ll[0]) + x * coord_geo_x * 2 ** (15 - self.z)
        ly = float(self.map_ll[1]) + y * coord_geo_y * math.cos(math.radians(float(self.map_ll[1]))) * 2 ** (
                15 - self.z)
        if lx > 180:
            lx -= 360
        elif lx < -180:
            lx += 360
        return lx, ly

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            x, y = event.pos().x() - self.label.pos().x(), event.pos().y() - self.label.pos().y()
            if not (0 <= x <= self.label.width() and 0 <= y <= self.label.height()):
                return None
            if self.z < 10:
                self.statusBar.showMessage('Увеличьте масштаб')
                return None
            lx, ly = self.get_coordinates(x, y)
            self.edit_search.setText(f'{lx},{ly}')
            self.search(coords=f'{lx},{ly}')
            self.edit_search.setText('')
        if event.button() == Qt.MouseButton.RightButton:
            x, y = event.pos().x() - self.label.pos().x(), event.pos().y() - self.label.pos().y()
            if not (0 <= x <= self.label.width() and 0 <= y <= self.label.height()):
                return None
            if self.z < 14:
                self.statusBar.showMessage('Увеличьте масштаб')
                return None
            lx, ly = self.get_coordinates(x, y)
            res = search_organization(f'{lx},{ly}', self.edit_organization.text())
            if res is not None:
                for org in res:
                    org_coords = org['geometry']['coordinates']
                    s = get_distance(a=(lx, ly), b=org_coords)
                    if get_distance((lx, ly), org_coords) <= 50:
                        self.edit_search.setText(org['properties']['description'])
                        self.search(coords=f'{lx},{ly}')
                        self.edit_search.setText('')
                        break


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
