from PyQt6.QtWidgets import (QMainWindow, QFileDialog, QApplication, QPushButton, QMessageBox, QLabel, QWidget, QHBoxLayout)
from PyQt6.QtGui import QPixmap
import pickle
import cave, light
import pathlib
import sys

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
        super().__init__()
        self.home_dir = str(pathlib.Path.home())

        logo = Image(self, "./Assets/logo.png")

        version = QLabel("ver 0.1.1", self)
        version.move(10, 440)

        open_cave = QPushButton("Open Cave", self)
        open_cave.move(100, 100)
        open_cave.clicked.connect(self.open_cave)

        new_cave = QPushButton("New Cave", self)
        new_cave.move(100, 125)
        new_cave.clicked.connect(self.new_cave)

        load_cave = QPushButton(" Backup Cave", self)
        load_cave.move(100, 150)
        load_cave.clicked.connect(self.load_cave)

        open_cave = QPushButton("Open Light", self)
        open_cave.move(200, 100)
        open_cave.clicked.connect(self.open_light)

        new_cave = QPushButton("New Light", self)
        new_cave.move(200, 125)
        new_cave.clicked.connect(self.new_light)

        load_cave = QPushButton("Backup Light", self)
        load_cave.move(200, 150)
        load_cave.clicked.connect(self.load_light)

        options = QPushButton("Options", self)
        options.move(400, 400)
        options.clicked.connect(self.open_settings)


        self.setCentralWidget(logo)
        self.setGeometry(300, 300, 550, 450)
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

    def open_settings(self):
        self.show_dialog = settings.SettingsGUI()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    import cave_editor, settings, light_editor
    ex = Main()
    sys.exit(app.exec())
