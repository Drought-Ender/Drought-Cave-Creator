import configparser
import json
import os
from PyQt6.QtWidgets import QMainWindow, QCheckBox, QPushButton, QLineEdit, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QFileDialog
import file_reader

class lineEditLable(QWidget):
    def __init__(self, parent, text, val):
        super(QWidget, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.parent = parent
        self.lab = QLabel(text, self)
        self.text = QLineEdit(val)
        self.val = val
        self.layout.addWidget(self.lab, 0)
        self.layout.addWidget(self.text, 1)
        self.setLayout(self.layout)
        self.text.textChanged.connect(self.on_change_value)
        self.setFixedSize(300, 50)
        self.show()

    def on_change_value(self, val):
        self.val = val

class directoryButton(QWidget):
    def __init__(self, parent, text, default, cave_dir):
        super(QWidget, self).__init__(parent)
        self.cave_dir = cave_dir
        self.layout = QVBoxLayout()
        self.parent = parent
        self.button = QPushButton(text)
        self.button.pressed.connect(self.open_file)
        self.edit = QLineEdit(default)
        self.layout.addWidget(self.button, 0)
        self.layout.addWidget(self.edit, 1)
        self.setLayout(self.layout)
        self.setFixedSize(200, 100)
        self.show()

    def open_file(self):
        file = QFileDialog.getExistingDirectory(self, "Open Cave File", self.cave_dir)
        self.edit.setText(file)

class rootButton(QWidget):
    def __init__(self, parent, text, cave_dir=""):
        super(QWidget, self).__init__(parent)
        self.cave_dir = cave_dir
        self.layout = QVBoxLayout()
        self.parent = parent
        self.button = QPushButton(text)
        self.button.pressed.connect(self.open_file)
        self.layout.addWidget(self.button, 0)
        self.setLayout(self.layout)
        self.setFixedSize(200, 100)
        self.show()

    def open_file(self):
        file = QFileDialog.getExistingDirectory(self, "Open Cave File", self.cave_dir)
        self.parent.root(file)

class Settings:
    def __init__(self):
        self.show_useless_teki = False
        self.show_captype = False
        self.show_item_weight = False
        self.show_gate_name = False
        self.use_internal_names = False
        self.use_internal_groups = False
        self.always_capinfo = True
        self.autoteki = True

        self.preset = "pikmin2"
        self.teki_dict = {}
        self.item_dict = {}

        self.cave_path = "none"
        self.units_path = "none"
        self.light_path = "none"
        self.unit_path = "none"

    def init_settings(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.show_useless_teki = config["Display Settings"].getboolean("HiddenTeki")
        self.show_captype = config["Display Settings"].getboolean("CapType")
        self.show_item_weight = config["Display Settings"].getboolean("ItemWeight")
        self.show_gate_name = config["Display Settings"].getboolean("GateName")
        self.use_internal_names = config["Display Settings"].getboolean("UseInternalNames")
        self.use_internal_groups = config["Display Settings"].getboolean("UseInternalGroups")
        self.always_capinfo = config["Behavior Settings"].getboolean("Capinfo")
        self.autoteki = config["Behavior Settings"].getboolean("autoTekiBox")
        self.preset = config["Behavior Settings"]["preset"]

    def init_preset_settings(self, preset=None):
        
        if preset is None:
            preset = self.preset
        if not os.path.exists(f"./presets/{preset}"):
            preset = "pikmin2"
        self.preset = preset
        preset_config = configparser.ConfigParser()
        preset_config.read(f"./presets/{preset}/preset.ini")
        self.cave_path = preset_config["Preset Settings"]["caveDirectory"]
        self.units_path = preset_config["Preset Settings"]["unitsDirectory"]
        self.light_path = preset_config["Preset Settings"]["lightDirectory"]
        self.unit_path = preset_config["Preset Settings"]["unitDirectory"]
        with open(f"presets/{self.preset}/teki.json", "r") as tekif:
            f = tekif.read()
            self.teki_dict = dict(json.loads(f))

        with open(f"presets/{self.preset}/item.json", "r") as itemf:
            f = itemf.read()
            self.item_dict = dict(json.loads(f))

settings = Settings()
settings.init_settings()
settings.init_preset_settings()

class SettingsGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.useless = QCheckBox("Show Useless Teki", self)
        self.useless.setChecked(settings.show_useless_teki)
        self.useless.move(30, 30)
        self.useless.setFixedSize(300, 20)
        self.useless.setToolTip("Shows teki that dont spawn or crash")
        self.cap_type = QCheckBox("Show Captype Slider", self)
        self.cap_type.setChecked(settings.show_captype)
        self.cap_type.move(30, 50)
        self.cap_type.setFixedSize(300, 20)
        self.cap_type.setToolTip("Shows the captype slider, which us usually useless")
        self.item_weight = QCheckBox("Show Item Weight Slider", self)
        self.item_weight.setChecked(settings.show_item_weight)
        self.item_weight.move(30, 70)
        self.item_weight.setFixedSize(300, 20)
        self.item_weight.setToolTip("Shows the item weight, which should never be used")
        self.gate_name = QCheckBox("Show Gate Names", self)
        self.gate_name.setChecked(settings.show_gate_name)
        self.gate_name.move(30, 90)
        self.gate_name.setFixedSize(300, 20)
        self.gate_name.setToolTip("Shows the gate name, which does nothing")
        self.internal_groups = QCheckBox("Show Interal Group Names", self)
        self.internal_groups.setChecked(settings.use_internal_groups)
        self.internal_groups.move(30, 110)
        self.internal_groups.setFixedSize(300, 20)
        self.internal_groups.setToolTip("Displays the internal group names on the spawn type drop-down")
        self.internal_names = QCheckBox("Show Internal Names", self)
        self.internal_names.setChecked(settings.use_internal_names)
        self.internal_names.move(30, 130)
        self.internal_names.setFixedSize(300, 20)
        self.internal_names.setToolTip("Uses the internal names for treasures and teki rather than their piklopeida names")
        self.capinfo = QCheckBox("Always Enable Capinfo", self)
        self.capinfo.setChecked(settings.always_capinfo)
        self.capinfo.move(30, 150)
        self.capinfo.setFixedSize(300, 20)
        self.capinfo.setToolTip("Capinfo will allways be shown, hides the 'use capinfo' button")
        self.autoteki = QCheckBox("Remove Useless Teki Options", self)
        self.autoteki.setChecked(settings.autoteki)
        self.autoteki.move(30, 170)
        self.autoteki.setFixedSize(300, 20)
        self.autoteki.setToolTip("Removes options that would do nothing in gameplay")

        self.save_button = QPushButton("Save Settings", self)
        self.save_button.pressed.connect(self.save)
        self.save_button.move(350, 300)
        self.save_button.setFixedSize(200, 50)
        self.preset = lineEditLable(self, "Preset in use:", settings.preset)
        self.preset.move(30, 250)
        self.preset.setToolTip("Used with Cavegen and recomended to be copied")
        self.preset_settings = QPushButton("Open Preset Settings", self)
        self.preset_settings.setFixedSize(300, 50)
        self.preset_settings.move(30, 300)
        self.preset_settings.pressed.connect(self.open_preset)

        self.update_cavegen = QPushButton("Update Cavgen Units (takes a while)", self)
        self.update_cavegen.setFixedSize(300, 50)
        self.update_cavegen.move(250, 25)
        self.update_cavegen.pressed.connect(self.try_update)
        self.update_cavegen.setToolTip("Update the units that CaveGen is using based on the current preset,\ncould take up to a minute or more")

        self.setGeometry(200, 200, 575, 375)
        self.setWindowTitle('Settings')
        self.show()
    
    def try_update(self):
        if os.path.exists(f"./presets/{self.preset.val}"):
            settings.init_preset_settings(self.preset.val)
            file_reader.run_cavegen_setup()
    
    def save(self):
        show_useless_teki = self.useless.isChecked()
        show_captype = self.cap_type.isChecked()
        show_item_weight = self.item_weight.isChecked()
        show_gate_name = self.gate_name.isChecked()
        use_internal_groups = self.internal_groups.isChecked()
        use_internal_names = self.internal_names.isChecked()
        capinfo = self.capinfo.isChecked()
        auto_teki = self.autoteki.isChecked()

        preset = self.preset.val
        config_write = configparser.ConfigParser()
        config_write["Display Settings"] = {
            "HiddenTeki" : show_useless_teki,
            "CapType" : show_captype,
            "ItemWeight" : show_item_weight,
            "GateName" : show_gate_name,
            "UseInternalNames" : use_internal_names,
            "UseInternalGroups" : use_internal_groups}
        if not os.path.exists(f"./presets/{preset}/"):
            QMessageBox.warning(self, "Error saving preset", f'Preset "{self.preset.val}" does not exist, defaulting to "pikmin2"')
            self.preset.val = "pikmin2"
        config_write["Behavior Settings"] = {
                "Capinfo" : capinfo, "autoTekiBox" : auto_teki, "preset" : self.preset.val
                }
        with open ("config.ini", "w") as f:
            config_write.write(f)
        settings.init_settings()

    def open_preset(self):
        settings.preset = self.preset.val
        if os.path.exists(f"./presets/{self.preset.val}"):
            settings.init_preset_settings(self.preset.val)
            PresetGUI(self.preset.val)
        else:
            QMessageBox.warning(self, "Folder does not exist", f'Preset "{self.preset.val}" does not exist')

class PresetGUI(QMainWindow):
    def __init__(self, preset):
        super().__init__()
        settings.preset = preset
        settings.init_preset_settings(preset)
        self.connect_root = rootButton(self, "Set all from Root folder")
        self.connect_root.move(25, 220)
        self.cave_folder = directoryButton(self, "Open Caves from folder", settings.cave_path, settings.cave_path)
        self.cave_folder.move(225, 20)
        self.units_folder = directoryButton(self, "Open units from folder", settings.units_path, settings.units_path)
        self.units_folder.move(25, 20)
        self.light_folder = directoryButton(self, "Open lighting from folder", settings.light_path, settings.light_path)
        self.light_folder.move(225, 120)
        self.unit_folder = directoryButton(self, "Open units arc from folder", settings.unit_path, settings.unit_path)
        self.unit_folder.move(25, 120)
        self.save_button = QPushButton("Save Preset Settings", self)
        self.save_button.move(225, 230)
        self.save_button.setFixedSize(200, 50)
        self.save_button.pressed.connect(self.save)
        self.setGeometry(300, 300, 450, 325)
        self.setWindowTitle('Preset Settings')
        self.show()
    
    def root(self, file):
        mapunits_folder = f"{file}/files/user/Mukki/mapunits/"

        cave_light_folder = f"{file}/files/user/Abe/cave/"

        # try and see if this is a wii filesystem
        if os.path.exists(f"{file}/files/pikmin2/user/"):
            print("detected wii filesystem")
            mapunits_folder = f"{file}/files/pikmin2/user/Mukki/mapunits/"
            cave_light_folder = f"{file}/files/pikmin2/user/Abe/cave/"

            

        if os.path.exists(f"{mapunits_folder}caveinfo/"):
            self.cave_folder.edit.setText(f"{mapunits_folder}caveinfo/")
        else:
            QMessageBox.warning(self, "Folder not found", "Could not find caveinfo folder")
        if os.path.exists(f"{mapunits_folder}units/"):
            self.units_folder.edit.setText(f"{mapunits_folder}units/")
        else:
            QMessageBox.warning(self, "Folder not found", "Could not find units folder")
        if os.path.exists(f"{mapunits_folder}arc/"):
            self.unit_folder.edit.setText(f"{mapunits_folder}arc/")
        else:
            QMessageBox.warning(self, "Folder not found", "Could not find arc folder")
        if os.path.exists(cave_light_folder):
            self.light_folder.edit.setText(cave_light_folder)
        else:
            QMessageBox.warning(self, "Folder not found", "Could not find light folder")
    
    def save(self):
        preset_write = configparser.ConfigParser()
        preset_write["Preset Settings"] = {
            "caveDirectory" : self.cave_folder.edit.text(),
            "lightDirectory" : self.light_folder.edit.text(),
            "unitsDirectory" : self.units_folder.edit.text(),
            "unitDirectory" : self.unit_folder.edit.text()}
        with open (f"./presets/{settings.preset}/preset.ini", "w") as f:
            preset_write.write(f)
        settings.init_preset_settings()

