import pickle
import pathlib
import sys
from os import chdir
from pathlib import Path

if __name__ == "__main__":
    chdir(f"{pathlib.Path(__file__).parent.resolve()}")

import cave, light, units
from PyQt6.QtWidgets import (QMainWindow, QFileDialog, QApplication, QPushButton, QMessageBox, QLabel, QWidget, QHBoxLayout)
from PyQt6.QtGui import QPixmap


class Image(QWidget):
    def __init__(self, parent, image):
        super(QWidget, self).__init__(parent)
        self.layout = QHBoxLayout(self)
        img = QLabel(self)
        pixmap = QPixmap(image)
        img.setPixmap(pixmap)
        self.layout.addWidget(img)
        self.setLayout(self.layout)

class Main(QMainWindow):

    def __init__(self):
        self.caveinfo = cave.DEFAULT_CAVEINFO
        self.light = light.DEFAULT_LIGHT
        self.units = units.DEFAULT_UNITS
        super().__init__()
        self.home_dir = str(pathlib.Path.home())

        logo = Image(self, "./Assets/logo.png")

        # version = QLabel("ver 1.0.0", self)
        # version.move(10, 440)

        open_cave = QPushButton("Open Cave", self)
        open_cave.move(230, 250)
        open_cave.clicked.connect(self.open_cave)

        new_cave = QPushButton("New Cave", self)
        new_cave.move(230, 275)
        new_cave.clicked.connect(self.new_cave)

        load_cave = QPushButton(" Backup Cave", self)
        load_cave.move(230, 300)
        load_cave.clicked.connect(self.load_cave)

        open_cave = QPushButton("Open Light", self)
        open_cave.move(175, 325)
        open_cave.clicked.connect(self.open_light)

        new_cave = QPushButton("New Light", self)
        new_cave.move(175, 350)
        new_cave.clicked.connect(self.new_light)

        load_cave = QPushButton("Backup Light", self)
        load_cave.move(175, 375)
        load_cave.clicked.connect(self.load_light)

        open_cave = QPushButton("Open Units", self)
        open_cave.move(285, 325)
        open_cave.clicked.connect(self.open_units)

        new_cave = QPushButton("New Units", self)
        new_cave.move(285, 350)
        new_cave.clicked.connect(self.new_units)

        load_cave = QPushButton("Backup Units", self)
        load_cave.move(285, 375)
        load_cave.clicked.connect(self.load_units)

        options = QPushButton("Options", self)
        options.move(450, 420)
        options.clicked.connect(self.open_settings)


        self.setCentralWidget(logo)
        self.setGeometry(300, 300, 550, 450)
        self.setMaximumSize(self.sizeHint())
        self.setWindowTitle('Cave Creator')
        self.show()


    def open_cave(self):
        cave_file = QFileDialog.getOpenFileName(self, "Open cave file", settings.settings.cave_path, "Cave Files (*.txt)")
        if cave_file[0]:
            with open(cave_file[0], 'rb') as f:
                try:
                    data = f.readlines()
                    self.caveinfo = cave.read_cave(data)
                except BaseException as e:
                    QMessageBox.critical(self, "Error reading cave", f"Error Reading Cave: {e}")
                else:
                    self.show_dialog = cave_editor.CaveTab(self.caveinfo, cave_file[0])


    def new_cave(self):
        self.caveinfo = cave.CaveInfo(1, [cave.get_default_floor()])
        self.show_dialog = cave_editor.CaveTab(self.caveinfo, "")

    def load_cave(self):
        this = f"{pathlib.Path(__file__).parent.resolve()}/Backups/Cave/"
        pickel_file = QFileDialog.getOpenFileName(self, "Open Pickle Backup", this, "Drought-Cave Pickle Data files (*.pickle)")
        if pickel_file[0]:
            with open(pickel_file[0], 'rb') as f:
                try:
                    self.caveinfo = pickle.load(f)
                    self.show_dialog = cave_editor.CaveTab(self.caveinfo, "")
                except:
                    QMessageBox.critical(self, "Error reading cave", "Cave Backup is corrupt")


    def open_light(self):

        light_file = QFileDialog.getOpenFileName(self, "Open light file", settings.settings.cave_path, "Lighting Files (*.ini)")
        if light_file[0]:
            with open(light_file[0], 'rb') as f:
                try:
                    data = f.readlines()
                    self.light = light.read_light(data)
                except BaseException as e:
                    QMessageBox.critical(self, "Error reading Light", f"Error Reading Light: {e}")
                else:
                        self.show_dialog = light_editor.LightTab(self.light, light_file[0])


    def new_light(self):
        self.show_dialog = light_editor.LightTab(light.DEFAULT_LIGHT, "")

    def load_light(self):
        this = f"{pathlib.Path(__file__).parent.resolve()}/Backups/Light/"
        pickel_file = QFileDialog.getOpenFileName(self, "Open Pickle Backup", this, "Drought-Light Pickle Data files (*.pickle)")
        if pickel_file[0]:
            with open(pickel_file[0], 'rb') as f:
                try:
                    self.light = pickle.load(f)
                    self.show_dialog = light_editor.LightTab(self.light, "")
                except:
                    QMessageBox.critical(self, "Error reading Light", "Light Backup is corrupt")

    def new_units(self):
        self.show_dialog = units_editor.UnitsTab(self.units, "")

    def open_units(self):
        unit_file = QFileDialog.getOpenFileName(self, "Open unit file", settings.settings.units_path, "Unit Files (*.txt)")
        if unit_file[0]:
            with open(unit_file[0], 'rb') as f:
                try:
                    data = f.readlines()
                    self.units = units.read_unitstxt(data)
                except BaseException as e:
                    QMessageBox.critical(self, "Error reading Units", f"Error Reading Units: {e}")
                else:
                    self.show_dialog = units_editor.UnitsTab(self.units, unit_file[0])

    def load_units(self):
        this = f"{pathlib.Path(__file__).parent.resolve()}/Backups/Units/"
        pickel_file = QFileDialog.getOpenFileName(self, "Open Pickle Backup", this, "Drought-Units Pickle Data files (*.pickle)")
        if pickel_file[0]:
            with open(pickel_file[0], 'rb') as f:
                try:
                    self.units = pickle.load(f)
                    self.show_dialog = units_editor.UnitsTab(self.units, "")
                except:
                    QMessageBox.critical(self, "Error reading Unit", "Unit Backup is corrupt")
    

    def open_settings(self):
        self.show_dialog = settings.SettingsGUI()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    import cave_editor, settings, light_editor, units_editor
    ex = Main()
    sys.exit(app.exec())
