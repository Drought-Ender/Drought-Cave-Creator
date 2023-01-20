import copy
import pickle
import datetime
import LightLibrary.light as light
import os
import pathlib
import settings
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QMessageBox, QGridLayout,
    QFileDialog, QWidget, QPushButton, QColorDialog, QTabWidget)
from PyQt6.QtGui import QIcon, QAction, QColor
from extra_widgets import betterSpinBox, betterSpinBoxFloat, ColorBox



class Keys:
    def __init__(self):
        self.teki_keys = []
        self.all_teki = []
        self.all_item = []
        self.settings = copy.deepcopy(settings.settings)
    
    def init_items(self):
        self.teki_keys = [teki for teki in self.settings.teki_dict if  self.settings.show_useless_teki or  self.settings.teki_dict[teki]["use"]]
        if  self.settings.use_internal_names:
            self.all_teki = [(QIcon(f"presets/{ self.settings.preset}/tekiIcons/{teki}.png"), teki) for teki in  self.settings.teki_dict if  self.settings.show_useless_teki or  self.settings.teki_dict[teki]["use"]]
            self.all_item = [(QIcon(f"presets/{ self.settings.preset}/itemIcons/{item}.png"), item) for item in  self.settings.item_dict]
        else:
            self.all_teki = [(QIcon(f"presets/{ self.settings.preset}/tekiIcons/{teki}.png"),  self.settings.teki_dict[teki]["common"]) for teki in  self.settings.teki_dict if  self.settings.show_useless_teki or  self.settings.teki_dict[teki]["use"]]
            self.all_item = [(QIcon(f"presets/{ self.settings.preset}/itemIcons/{item}.png"),  self.settings.item_dict[item]) for item in  self.settings.item_dict]
            self.settings = copy.deepcopy(settings.settings)

keys = Keys()



class ColorSubWidget(QWidget):
    def __init__(self, parent, color:light.Colors):
        super(QWidget, self).__init__(parent)
        self.color = color
        self.parent = parent
        self.layout = QGridLayout()
        self.r = betterSpinBox(self, "Red:", 0, 255, self.color.red)
        self.g = betterSpinBox(self, "Green:", 0, 255, self.color.green)
        self.b = betterSpinBox(self, "Blue:", 0, 255, self.color.blue)
        self.a = betterSpinBox(self, "Alpha:", 0, 255, self.color.alpha)
        self.r.slide.valueChanged.connect(self.color_change)
        self.g.slide.valueChanged.connect(self.color_change)
        self.b.slide.valueChanged.connect(self.color_change)
        self.a.slide.valueChanged.connect(self.color_change)
        self.layout.addWidget(self.r, 0, 0)
        self.layout.addWidget(self.g, 0, 1)
        self.layout.addWidget(self.b, 1, 0)
        self.layout.addWidget(self.a, 1, 1)
        self.setLayout(self.layout)
        self.update_color(color)
        
    def update_color(self, color:light.Colors):
        self.color = color
        self.r.slide.setValue(color.red)
        self.g.slide.setValue(color.green)
        self.b.slide.setValue(color.blue)
        self.a.slide.setValue(color.alpha)

    def color_change(self, _):
        self.color = light.Colors(self.r.slide.value(),
        self.g.slide.value(),
        self.b.slide.value(),
        self.a.slide.value())
        self.parent.update_box(self.color)


class ColorWidget(QWidget):
    def __init__(self, parent, name:str, color:light.Colors):
        super(QWidget, self).__init__(parent)
        self.layout = QGridLayout()
        self.color = color
        self.subcolor = ColorSubWidget(self, self.color)
        self.label = QLabel(name, self)
        self.button = QPushButton("Edit Color", self)
        self.button.clicked.connect(self.on_click)
        self.box = ColorBox(self, ColorToQColor(self.color))
        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.button, 0, 1)
        self.layout.addWidget(self.box, 1, 0)
        self.layout.addWidget(self.subcolor, 1, 1)
        self.setLayout(self.layout)

    def update_color(self):
        self.color = light.Colors(
            self.subcolor.r.slide.value(),
            self.subcolor.g.slide.value(),
            self.subcolor.b.slide.value(),
            self.subcolor.a.slide.value())

    def update_box(self, color):
        self.box.update_color(ColorToQColor(color))
        self.color = color
    
    def on_click(self):
        self.update_color()
        before_typecast = QColorDialog.getColor(ColorToQColor(self.color))
        self.color = QColorToColor(before_typecast)
        self.box.update_color(before_typecast)
        self.subcolor.update_color(self.color)


def ColorToQColor(color:light.Colors):
    return QColor(color.red, color.green, color.blue, color.alpha)

def QColorToColor(color:QColor):
    return light.Colors(color.red(), color.green(), color.blue(), color.alpha())

class SpotLight(QWidget):
    def __init__(self, parent, name:str, spotlight:light.SpotLight):
        super(QWidget, self).__init__(parent)
        self.layout = QGridLayout()
        self.spotlight = spotlight
        self.label = QLabel(name, self)
        self.colors = ColorWidget(self, "Color Params:", self.spotlight.color)
        self.cutoff = betterSpinBoxFloat(self, "Spotlight Cutoff:", 0, 99999.99999, self.spotlight.cutoff)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.colors)
        self.layout.addWidget(self.cutoff)
        self.setLayout(self.layout)

    def get_light(self):
        self.spotlight.color = self.colors.color
        self.spotlight.cutoff = self.cutoff.slide.value()
        return self.spotlight

class FogLight(QWidget):
    def __init__(self, parent, name:str, foglight:light.FogLight):
        super(QWidget, self).__init__(parent)
        self.layout = QGridLayout()
        self.foglight = foglight
        self.label = QLabel(name, self)
        self.colors = ColorWidget(self, "Color Params:", self.foglight.color)
        self.fog_start = betterSpinBoxFloat(self, "Fog Start:", 0, 99999.99999, self.foglight.fog_parms.start)
        self.fog_end = betterSpinBoxFloat(self, "Fog End:", 0, 999999.99999, self.foglight.fog_parms.end)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.colors)
        self.layout.addWidget(self.fog_start)
        self.layout.addWidget(self.fog_end)
        self.setLayout(self.layout)
    
    def get_light(self):
        self.foglight.color = self.colors.color
        self.foglight.fog_parms.start = self.fog_start.slide.value()
        self.foglight.fog_parms.end = self.fog_end.slide.value()
        return self.foglight


class LightParamWidget(QWidget):
    def __init__(self, parent, light_params:light.lightParameter):
        super(QWidget, self).__init__(parent)
        self.layout = QGridLayout()
        self.light_parms = light_params
        self.dist = betterSpinBoxFloat(self, "Distance from light source:", 0.0, 999999.999999, self.light_parms.move_dist)
        self.main = SpotLight(self, "Main Light:", self.light_parms.main)
        self.sub = SpotLight(self, "Sub Light:", self.light_parms.sub)
        self.specular = ColorWidget(self, "Specular Light:", self.light_parms.specular)
        self.ambient = ColorWidget(self, "Ambient Light:", self.light_parms.ambient)
        self.fog = FogLight(self, "Fog:", self.light_parms.fog)
        self.shadow = ColorWidget(self, "Shadows:", self.light_parms.shadow)
        self.layout.addWidget(self.dist, 0, 0)
        self.layout.addWidget(self.main, 1, 0)
        self.layout.addWidget(self.sub, 2, 0)
        self.layout.addWidget(self.specular, 1, 1)
        self.layout.addWidget(self.ambient, 2, 1)
        self.layout.addWidget(self.fog, 1, 2)
        self.layout.addWidget(self.shadow, 2, 2)
        self.setLayout(self.layout)

    def get_light(self):
        self.light_parms.move_dist = self.dist.slide.value()
        self.light_parms.main = self.main.get_light()
        self.light_parms.sub = self.sub.get_light()
        self.light_parms.specular = self.specular.color
        self.light_parms.ambient = self.ambient.color
        self.light_parms.fog = self.fog.get_light()
        self.light_parms.shadow = self.shadow.color
        return self.light_parms




class LightWindow(QTabWidget):
    def __init__(self, parent, light_:light.LightFile):
        super(QWidget, self).__init__(parent)
        self.light = light_
        self.normal_light = LightParamWidget(self, self.light.normal)
        self.orb_light = LightParamWidget(self, self.light.orb)
        self.addTab(self.normal_light, "No-Orb Lighting")
        self.addTab(self.orb_light, "Stellar Orb Lighting")
    
    def get_light(self):
        self.light.common = light.LightCommon("{0001}", 1)
        self.light.normal = self.normal_light.get_light()
        self.light.orb = self.orb_light.get_light()
        return self.light

class LightTab(QMainWindow):
    def __init__(self, light_:light.LightFile, light_dir):
        super().__init__()
        keys.init_items()
        self.light = light_
        self.light_dir = light_dir

        openFile = QAction(QIcon('open.png'), '&Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new Light')
        openFile.triggered.connect(self.open_new_light)
        saveFile = QAction(QIcon('save.png'), '&Save', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save Light to file')
        saveFile.triggered.connect(self.save_light)
        saveAsFile = QAction(QIcon('save.png'), 'Save &As', self)
        saveAsFile.setShortcut('Ctrl+Shift+S')
        saveAsFile.setStatusTip('Save Light to new file')
        saveAsFile.triggered.connect(self.save_as_light)
        backup = QAction(QIcon('save.png'), '&Backup', self)
        backup.setShortcut('Ctrl+B')
        backup.setStatusTip('Save Light to backup file')
        backup.triggered.connect(self.save_backup)
        load_backup = QAction(QIcon('save.png'), '&Load Backup', self)
        load_backup.setShortcut('Ctrl+L')
        load_backup.setStatusTip('load Light from backup file')
        load_backup.triggered.connect(self.load_backup)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        fileMenu.addAction(saveAsFile)
        fileMenu.addAction(backup)
        fileMenu.addAction(load_backup)


        self.light_window = LightWindow(self, self.light)
        self.setGeometry(50, 50, 1400, 1000)
        self.setWindowTitle('Light Editor')
        self.setCentralWidget(self.light_window)
        self.show()
        

    def open_new_light(self):
        light_file = QFileDialog.getOpenFileName(self, "Open Light File", keys.settings.light_path)
        if light_file[0]:
            with open(light_file[0], 'rb') as f:
                try:
                    data = f.readlines()
                    self.light = light.read_light(data)
                    self.light_dir = light_file[0]
                    self.light_window = LightWindow(self, self.light)
                    self.setCentralWidget(self.light_window)
                except Exception as e:
                    QMessageBox.critical(self, "Error reading light", str(e))
    
    def save_light(self):
        self.light = self.light_window.get_light()
        light_file = self.light_dir
        if not os.path.exists(self.light_dir):
            light_file = QFileDialog.getSaveFileName(self, "Save Light as", keys.settings.light_path)[0]
            if not light_file.endswith(".ini"):
                light_file += ".ini"
        with open(light_file, 'w',  encoding='utf-8') as f:
            f.writelines(light.export_light(self.light))

    def save_as_light(self):
        self.light = self.light_window.get_light()
        light_file = QFileDialog.getSaveFileName(self, "Save Light as", keys.settings.light_path)[0]
        if not light_file.endswith(".ini"):
            light_file += ".ini"
        with open(light_file, 'w',  encoding='utf-8') as f:
            f.writelines(light.export_light(self.light))
            self.light_dir = light_file
    
    def save_backup(self):
        self.light = self.light_window.get_light()
        this = f"{pathlib.Path(__file__).parent.resolve()}/Backups/Light/"
        now = datetime.datetime.now()
        now = now.replace(":", "_")
        try:
            with open(os.path.join(this, f"{now}.pickle"), "wb+") as f:
                pickle.dump(self.light, f)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error saving backup", "Unable to save backup; backups folder is missing")

    
    def load_backup(self):
        this = f"{pathlib.Path(__file__).parent.resolve()}/Backups/Light/"
        pickel_file = QFileDialog.getOpenFileName(self, "Open pickel data file", this, "Drought-Cave Pickle Data files (*.pickle)")
        if pickel_file[0]:
            with open(pickel_file[0], 'rb') as f:
                try:
                    self.light = pickle.load(f)
                    self.light_window = LightWindow(self, self.light)
                    self.setCentralWidget(self.light_window)
                except:
                    QMessageBox.critical(self, "Error reading cave", f"Backup is corrupt")