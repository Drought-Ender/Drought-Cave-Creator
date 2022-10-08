from PyQt6.QtWidgets import QMainWindow, QCheckBox, QPushButton
import configparser
config = configparser.ConfigParser()
config.read("config.ini")
show_useless_teki = config["Display Settings"].getboolean("HiddenTeki")
show_captype = config["Display Settings"].getboolean("CapType")
show_item_weight = config["Display Settings"].getboolean("ItemWeight")
show_gate_name = config["Display Settings"].getboolean("GateName")
use_internal_names = config["Display Settings"].getboolean("UseInternalNames")
use_internal_groups = config["Display Settings"].getboolean("UseInternalGroups")

teki_text = config["Behavior Settings"].getboolean("TekiIsText")
item_text = config["Behavior Settings"].getboolean("ItemIsText")

class SettingsGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.useless = QCheckBox("Show Useless Teki", self)
        self.useless.setChecked(show_useless_teki)
        self.useless.move(30, 30)
        self.useless.setFixedSize(300, 20)
        self.cap_type = QCheckBox("Show Captype Slider", self)
        self.cap_type.setChecked(show_captype)
        self.cap_type.move(30, 50)
        self.cap_type.setFixedSize(300, 20)
        self.item_weight = QCheckBox("Show Item Weight Slider", self)
        self.item_weight.setChecked(show_item_weight)
        self.item_weight.move(30, 70)
        self.item_weight.setFixedSize(300, 20)
        self.gate_name = QCheckBox("Show Gate Names", self)
        self.gate_name.setChecked(show_gate_name)
        self.gate_name.move(30, 90)
        self.gate_name.setFixedSize(300, 20)
        self.internal_groups = QCheckBox("Show Interal Group Names", self)
        self.internal_groups.setChecked(use_internal_groups)
        self.internal_groups.move(30, 110)
        self.internal_groups.setFixedSize(300, 20)
        self.internal_names = QCheckBox("Show Internal Names", self)
        self.internal_names.setChecked(use_internal_names)
        self.internal_names.move(30, 130)
        self.internal_names.setFixedSize(300, 20)
        self.teki_text = QCheckBox("Show Teki as text boxes", self)
        self.teki_text.setChecked(teki_text)
        self.teki_text.move(30, 150)
        self.teki_text.setFixedSize(300, 20)
        self.save_button = QPushButton("Save Settings", self)
        self.save_button.pressed.connect(self.save)
        self.save_button.move(400, 300)
        self.setGeometry(200, 200, 600, 400)
        self.setWindowTitle('Settings')
        self.show()
    
    def save(self):
        print("save")
        global show_useless_teki, show_captype, show_item_weight, show_gate_name, use_internal_groups, use_internal_names, teki_text
        show_useless_teki = self.useless.isChecked()
        show_captype = self.cap_type.isChecked()
        show_item_weight = self.item_weight.isChecked()
        show_gate_name = self.gate_name.isChecked()
        use_internal_groups = self.internal_groups.isChecked()
        use_internal_names = self.internal_names.isChecked()
        teki_text = self.teki_text.isChecked()
        config_write = configparser.ConfigParser()
        config_write["Display Settings"] = {"HiddenTeki" : show_useless_teki,
            "CapType" : show_captype, 
            "ItemWeight" : show_item_weight,
            "GateName" : show_gate_name,
            "UseInternalNames" : use_internal_names,
            "UseInternalGroups" : use_internal_groups}
        config_write["Behavior Settings"] = {"TekiIsText" : teki_text, "ItemisText" : item_text}
        with open ("config.ini", "w") as f:
            config_write.write(f)



