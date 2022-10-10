import cave
import copy
import datetime
import settings
from PyQt6.QtWidgets import (
    QMainWindow, QLineEdit, QLabel, QMessageBox, QVBoxLayout,
    QGridLayout, QCheckBox, QScrollArea, QComboBox, QListView,
    QHBoxLayout, QFileDialog, QWidget, QPushButton,
    QSpinBox, QDoubleSpinBox, QTabWidget)
from PyQt6.QtGui import QIcon, QAction
import pathlib
import os
import pickle



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

class betterSpinBox(QWidget):
    def __init__(self, parent, text, min, max, val):
        super(QWidget, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.parent = parent
        self.lab = QLabel(text, self)
        self.slide = QSpinBox(self)
        self.slide.setMinimum(min)
        self.slide.setMaximum(max)
        self.slide.setValue(val)
        self.layout.addWidget(self.lab, 0)
        self.layout.addWidget(self.slide, 0)
        self.setLayout(self.layout)
        self.val = val
        self.slide.valueChanged.connect(self.on_change_value)

    def on_change_value(self, val):
        self.val = int(val)


class betterSpinBoxFloat(QWidget):
    def __init__(self, parent, text, min, max, val):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout()
        self.lab = QLabel(text, self)
        self.slide = QDoubleSpinBox(self)
        self.slide.setMinimum(min)
        self.slide.setMaximum(max)
        self.slide.setValue(val)
        self.layout.addWidget(self.lab, 0)
        self.layout.addWidget(self.slide, 0)
        self.setLayout(self.layout)
        self.val = val
        self.slide.valueChanged.connect(self.on_change_value)

    def on_change_value(self, val):
        self.val = float(val)

class ItemWidget(QWidget):
    def __init__(self, parent, item):
        super(QWidget, self).__init__(parent)
        self.layout = QGridLayout()
        self.treasure = item
        if self.treasure.name in list(keys.settings.item_dict.keys()):
            self.item_index = list(keys.settings.item_dict.keys()).index(self.treasure.name)
        else:
            self.item_index = 0
        if keys.settings.item_text:
            self.itemcombo = QLineEdit(self.treasure.name)
        else:
            self.itemcombo = DefaultInfoMenu(self, keys.all_item, self.item_index)
        self.spawn_count = QSpinBox()
        self.spawn_count.setValue(self.treasure.fill)
        self.weight = QSpinBox()
        self.weight.setValue(self.treasure.weight)
        self.weight.setMaximum(9)
        if keys.settings.show_item_weight:
            self.layout.addWidget(self.itemcombo, 0, 0, 1, 2)
            self.layout.addWidget(self.spawn_count, 1, 0)
            self.layout.addWidget(self.weight, 1, 1)
        else:
            self.layout.addWidget(self.itemcombo, 0, 0)
            self.layout.addWidget(self.spawn_count, 0, 1)

        self.setLayout(self.layout)

class AddSubButtons(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.add_item = QPushButton("+")
        self.sub_item = QPushButton("-")
        self.add_item.clicked.connect(parent.add_obj)
        self.sub_item.clicked.connect(parent.sub_obj)
        self.layout.addWidget(self.add_item)
        self.layout.addWidget(self.sub_item)
        self.setLayout(self.layout)
    
    def check_disable(self, num):
        if num == 0:
            self.sub_item.blockSignals(True)
        else:
            self.sub_item.blockSignals(False)

class ItemInfoBox(QScrollArea):
    def __init__(self, parent, iteminfo):
        super(QWidget, self).__init__(parent)
        self.this_widget = QWidget()
        self.name = QLabel("iteminfo")
        self.iteminfo = iteminfo
        self.layout = QVBoxLayout(self.this_widget)
        self.layout.addWidget(self.name)
        self.items = []
        for i, item in enumerate(self.iteminfo.items):
            if i < self.iteminfo.item_count:
                next_widget = ItemWidget(self, item)
                self.items.append(next_widget)
                self.layout.addWidget(next_widget)
        self.buttons = AddSubButtons(self)
        self.buttons.check_disable(len(self.iteminfo.items))
        self.layout.addWidget(self.buttons)
        self.setWidget(self.this_widget)
        self.setWidgetResizable(True)

    def update_item(self):
        self.iteminfo = cave.ItemInfo()
        for item in self.this_widget.children():
            new_item = cave.Treasure()
            if type(item) != ItemWidget:
                continue
            if keys.settings.item_text:
                new_item.name = item.itemcombo.text()
            else:
                new_item.name = list(keys.settings.item_dict.keys())[item.itemcombo.currentIndex()]
            new_item.fill = item.spawn_count.value()
            new_item.weight = item.weight.value()
            self.iteminfo.items.append(copy.deepcopy(new_item))
        self.iteminfo.item_count = len(self.iteminfo.items)
        return self.iteminfo

    def add_obj(self):
        self.iteminfo.items.append(cave.Treasure())
        new_widget = ItemWidget(self, cave.Treasure())
        self.items += [new_widget]
        self.layout.insertWidget(len(self.items), new_widget)
        self.buttons.check_disable(len(self.iteminfo.items))
    
    def sub_obj(self):
        self.iteminfo.items.pop()
        remove = self.items.pop()
        self.layout.removeWidget(remove)
        self.buttons.check_disable(len(self.iteminfo.items))

class GateWidget(QWidget):
    def __init__(self, parent, gate):
        super(QWidget, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.gate = gate
        self.name = QLineEdit(self.gate.name)
        self.life = QDoubleSpinBox()
        self.life.setMaximum(999999.999999)
        self.life.setValue(self.gate.life)
        self.weight = QSpinBox()
        self.weight.setValue(self.gate.weight)
        self.weight.setMaximum(9)
        self.weight.setMinimum(1)
        if keys.settings.show_gate_name:
            self.layout.addWidget(self.name)
        self.layout.addWidget(self.life)
        self.layout.addWidget(self.weight)

        self.setLayout(self.layout)

class GateInfoBox(QScrollArea):
    def __init__(self, parent, gateinfo):
        super(QWidget, self).__init__(parent)
        self.this_widget = QWidget()
        self.name = QLabel("Gateinfo")
        self.gateinfo = gateinfo
        self.layout = QVBoxLayout(self.this_widget)
        self.layout.addWidget(self.name)
        self.gates = []
        for i, gate in enumerate(self.gateinfo.gates):
            if i < self.gateinfo.gate_count:
                next_widget = GateWidget(self, gate)
                self.gates.append(next_widget)
                self.layout.addWidget(next_widget)
        self.buttons = AddSubButtons(self)
        self.buttons.check_disable(len(self.gateinfo.gates))
        self.layout.addWidget(self.buttons)
        self.setWidget(self.this_widget)
        self.setWidgetResizable(True)
    
    def update_gate(self):
        self.gateinfo = cave.GateInfo()
        for gate in self.this_widget.children():
            new_gate = cave.Gate()
            if type(gate) != GateWidget:
                continue
            new_gate.name = gate.name.text()
            new_gate.fill = gate.life.value()
            new_gate.weight = gate.weight.value()
            self.gateinfo.gates.append(copy.deepcopy(new_gate))
        self.gateinfo.gate_count = len(self.gateinfo.gates)
        return self.gateinfo

    def add_obj(self):
        self.gateinfo.gates.append(cave.Gate())
        new_widget = GateWidget(self, cave.Gate())
        self.gates += [new_widget]
        self.layout.insertWidget(len(self.gates), new_widget)
        self.buttons.check_disable(len(self.gateinfo.gates))
    
    def sub_obj(self):
        self.gateinfo.gates.pop()
        remove = self.gates.pop()
        self.layout.removeWidget(remove)
        self.buttons.check_disable(len(self.gateinfo.gates))

class TekiInfoBox(QScrollArea):
    def __init__(self, parent, tekiinfo):
        super(QWidget, self).__init__(parent)
        self.this_widget = QWidget()
        self.name = QLabel("TekiInfo")
        self.tekiinfo = tekiinfo



        self.layout = QVBoxLayout(self.this_widget)
        self.layout.addWidget(self.name)
        self.tekis = []
        for i, teki in enumerate(self.tekiinfo.tekis):
            if i < self.tekiinfo.teki_count:
                self.tekis.append(TekiWidget(self, teki))
                self.layout.addWidget(self.tekis[-1])

        self.buttons = AddSubButtons(self)
        self.buttons.check_disable(len(self.tekiinfo.tekis))
        self.layout.addWidget(self.buttons)
        self.setWidget(self.this_widget)


        self.setWidgetResizable(True)
    
    def update_teki(self):
        self.tekiinfo = cave.TekiInfo()
        for teki in self.this_widget.children():
            new_teki = cave.Teki()
            if type(teki) != TekiWidget:
                continue
            if keys.settings.teki_text:
                new_teki.teki.name = teki.tekicombo.text()
            else:
                new_teki.teki.name = keys.teki_keys[teki.tekicombo.currentIndex()]
            if teki.itemcombo.currentIndex() == 0:
                new_teki.teki.item = list(keys.settings.item_dict.keys())[0]
                new_teki.teki.has_item = False
            else:
                new_teki.teki.item = list(keys.settings.item_dict.keys())[teki.itemcombo.currentIndex() - 1]
                new_teki.teki.has_item = True
            new_teki.teki.falltype = teki.fall.currentIndex()
            new_teki.teki.fill = teki.spawn_count.value()
            new_teki.teki.weight = teki.weight.value()
            new_teki.spawn = teki.spawn.currentIndex()
            self.tekiinfo.tekis.append(copy.deepcopy(new_teki))
        self.tekiinfo.teki_count = len(self.tekiinfo.tekis)
        return self.tekiinfo

    def add_obj(self):
        self.tekiinfo.tekis.append(cave.Teki())
        new_widget = TekiWidget(self, cave.Teki())
        self.tekis += [new_widget]
        self.layout.insertWidget(len(self.tekis), new_widget)
        self.buttons.check_disable(len(self.tekiinfo.tekis))
    
    def sub_obj(self):
        self.tekiinfo.tekis.pop()
        remove = self.tekis.pop()
        self.layout.removeWidget(remove)
        self.buttons.check_disable(len(self.tekiinfo.tekis))

class CapWidget(QWidget):
    def __init__(self, parent, cap):
        super(QWidget, self).__init__(parent)
        self.layout = QGridLayout()
        self.cap = cap
        self.teki_base_obj = self.cap.teki
        name = self.teki_base_obj.name
        self.index = keys.teki_keys.index(name)
        if keys.settings.teki_text:
            self.tekicombo = QLineEdit(name)
        else:
            self.tekicombo = DefaultInfoMenu(self, keys.all_teki, self.index)
        self.spawn_count = QSpinBox()
        self.spawn_count.setValue(self.teki_base_obj.fill)
        
        self.weight = QSpinBox()
        self.weight.setValue(self.teki_base_obj.weight)
        self.weight.setMaximum(9)
        self.fall = QComboBox()
        self.fall.addItems(["None", "All", "Pikmin", "Captain", "Carry", "Purple"])
        self.fall.setCurrentIndex(self.teki_base_obj.falltype)
        if self.teki_base_obj.item in list(keys.settings.item_dict.keys()):
            self.item_index = list(keys.settings.item_dict.keys()).index(self.teki_base_obj.item)
        else:
            self.item_index = 0
        item_with_none = [(QIcon(f"presets/{keys.settings.preset}/itemIcons/None.png"), "None")] + keys.all_item
        if (self.teki_base_obj.has_item):
            self.itemcombo = DefaultInfoMenu(self, item_with_none, self.item_index + 1)
        else:
            self.itemcombo = DefaultInfoMenu(self, item_with_none, 0)
        self.double = QCheckBox("Only One")
        self.double.setChecked(self.cap.dont_dupe)
        self.cap_type = QSpinBox()
        self.cap_type.setValue(self.cap.cap_type)
        

        self.layout.addWidget(self.tekicombo, 0, 0, 1, 3)
        self.layout.addWidget(self.itemcombo, 1, 0, 1, 2)
        self.layout.addWidget(self.fall, 1, 2)
        self.layout.addWidget(self.spawn_count, 2, 0)
        self.layout.addWidget(self.weight, 2, 1)
        self.layout.addWidget(self.double, 2, 2)
        if keys.settings.show_captype:
            self.layout.addWidget(self.cap_type, 3, 0)

        self.setLayout(self.layout)


class betterComboBox(QWidget):
    def __init__(self, parent, text, items, val):
        super(QWidget, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.parent = parent
        self.lab = QLabel(text, self)
        self.box = QComboBox()
        self.box.addItems(items)
        self.box.setCurrentIndex(val)
        self.layout.addWidget(self.lab, 0)
        self.layout.addWidget(self.box, 0)
        self.setLayout(self.layout)
        self.val = val
        self.box.currentIndexChanged.connect(self.on_change_value)

    def on_change_value(self, val):
        self.val = int(val)


class CapInfoBox(QScrollArea):
    def __init__(self, parent, capinfo):
        super(QWidget, self).__init__(parent)
        self.this_widget = QWidget()
        self.name = QLabel("Capinfo")
        self.capinfo = capinfo
        self.layout = QVBoxLayout(self.this_widget)
        self.layout.addWidget(self.name)
        self.caps = []
        for i, cap in enumerate(self.capinfo.caps):
            if i < self.capinfo.cap_count:
                self.caps.append(CapWidget(self, cap))
                self.layout.addWidget(self.caps[-1])
        self.buttons = AddSubButtons(self)
        self.buttons.check_disable(len(self.capinfo.caps))
        self.layout.addWidget(self.buttons)
        self.setWidget(self.this_widget)


        self.setWidgetResizable(True)
    
    def update_cap(self):
        self.capinfo = cave.CapInfo()
        for cap in self.this_widget.children():
            new_cap = cave.Cap()
            if type(cap) != CapWidget:
                continue
            if keys.settings.teki_text:
                new_cap.teki.name = cap.tekicombo.text()
            else:
                new_cap.teki.name = keys.teki_keys[cap.tekicombo.currentIndex()]
            if cap.itemcombo.currentIndex() == 0:
                new_cap.teki.item = list(keys.settings.item_dict.keys())[0]
                new_cap.teki.has_item = False
            else:
                new_cap.teki.item = list(keys.settings.item_dict.keys())[cap.itemcombo.currentIndex() - 1]
                new_cap.teki.has_item = True
            new_cap.teki.falltype = cap.fall.currentIndex()
            new_cap.teki.fill = cap.spawn_count.value()
            new_cap.teki.weight = cap.weight.value()
            new_cap.dont_dupe = cap.double.isChecked()
            new_cap.cap_type = cap.cap_type.value()
            self.capinfo.caps.append(copy.deepcopy(new_cap))
        self.capinfo.cap_count = len(self.capinfo.caps)
        return self.capinfo

    def add_obj(self):
        self.capinfo.caps.append(cave.Cap())
        new_widget = CapWidget(self, cave.Cap())
        self.caps += [new_widget]
        self.layout.insertWidget(len(self.caps), new_widget)
        self.buttons.check_disable(len(self.capinfo.caps))
    
    def sub_obj(self):
        self.capinfo.caps.pop()
        remove = self.caps.pop()
        self.layout.removeWidget(remove)
        self.buttons.check_disable(len(self.capinfo.caps))


class TekiWidget(QWidget):
    def __init__(self, parent, teki):
        super(QWidget, self).__init__(parent)
        self.layout = QGridLayout()
        self.teki = teki
        self.teki_base_obj = self.teki.teki
        name = self.teki_base_obj.name
        self.index = keys.teki_keys.index(name)
        if keys.settings.teki_text:
            self.tekicombo = QLineEdit(name)
        else:
            self.tekicombo = DefaultInfoMenu(self, keys.all_teki, self.index)
        self.spawn_count = QSpinBox()
        self.spawn_count.setValue(self.teki_base_obj.fill)
        
        self.weight = QSpinBox()
        self.weight.setValue(self.teki_base_obj.weight)
        self.weight.setMaximum(9)
        self.fall = QComboBox()
        self.fall.addItems(["None", "All", "Pikmin", "Captain", "Carry", "Purple"])
        self.fall.setCurrentIndex(self.teki_base_obj.falltype)
        if self.teki_base_obj.item in list(keys.settings.item_dict.keys()):
            self.item_index = list(keys.settings.item_dict.keys()).index(self.teki_base_obj.item)
        else:
            self.item_index = 0
        item_with_none = [(QIcon(f"presets/{keys.settings.preset}/itemIcons/None.png"), "None")] + keys.all_item
        if (self.teki_base_obj.has_item):
            self.itemcombo = DefaultInfoMenu(self, item_with_none, self.item_index + 1)
        else:
            self.itemcombo = DefaultInfoMenu(self, item_with_none, 0)
        self.spawn = QComboBox()
        if keys.settings.use_internal_groups:
            self.spawn.addItems(["Teki A", "Teki B", "Item", "None", "FixObj", "Teki C", "Plant", "Start", "Teki F"])
        else:
            self.spawn.addItems(["Easy", "Hard", "Item", "None", "Hole", "Seams", "Plant", "Pod", "Special"])
        self.spawn.setCurrentIndex(self.teki.spawn)
        self.spawn.setView(QListView())

        self.layout.addWidget(self.tekicombo, 0, 0, 1, 3)
        self.layout.addWidget(self.itemcombo, 1, 0, 1, 2)
        self.layout.addWidget(self.fall, 1, 2)
        self.layout.addWidget(self.spawn_count, 2, 0)
        self.layout.addWidget(self.weight, 2, 1)
        self.layout.addWidget(self.spawn, 2, 2)

        self.setLayout(self.layout)


class DefaultInfoMenu(QComboBox):
    def __init__(self, parent, items, index):
        super(QComboBox, self).__init__(parent)
        for args in items:
            self.addItem(*args)
        self.setCurrentIndex(index)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.resize(self.sizeHint())
        self.setView(QListView())

class lineEditLable(QWidget):
    def __init__(self, parent, text, val):
        super(QWidget, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.parent = parent
        self.lab = QLabel(text, self)
        self.text = QLineEdit(val)
        self.val = val
        self.layout.addWidget(self.lab, 0)
        self.layout.addWidget(self.text, 0)
        self.setLayout(self.layout)
        self.text.textChanged.connect(self.on_change_value)

    def on_change_value(self, val):
        self.val = val

class directoryButton(QWidget):
    def __init__(self, parent, text, default, cave_dir):
        super(QWidget, self).__init__(parent)
        self.cave_dir = cave_dir
        self.layout = QVBoxLayout()
        self.parent = parent
        self.lab = QLabel(text)
        self.button = QPushButton("Open Directory")
        self.button.pressed.connect(self.open_file)
        self.edit = QLineEdit(default)
        self.layout.addWidget(self.lab)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.edit)
        self.setLayout(self.layout)

    def open_file(self):
        file = QFileDialog.getOpenFileName(self, "Open Cave File", self.cave_dir)
        text = file[0].split("/")[-1]
        self.edit.setText(text)

class Floorinfo_tab(QWidget):
    def __init__(self, parent, floorinfo, cave_dir):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.cave_dir = cave_dir
        self.floorinfo = floorinfo
        self.dead_end = betterSpinBox(self, "Dead End %:", 0, 100, self.floorinfo.dead_end)
        self.echo = betterComboBox(self, "Echo Type:", ["Soil", "Metal", "Concrete", "Tile", "Garden", "Toy"], self.floorinfo.echo)
        self.music = betterComboBox(self, "Music type:", ["Normal", "Boss", "Rest"], self.floorinfo.music)
        self.rooms = betterSpinBox(self, "Room Number:", 0, 99, self.floorinfo.room_num)
        self.corridor_chance = betterSpinBoxFloat(self, "Corridor Probability:", 0, 1, self.floorinfo.corridor_chance)
        self.timer = betterSpinBoxFloat(self, "Wraith Timer:", 0, 99999, self.floorinfo.timer)
        self.corridor_chance.slide.setSingleStep(0.1)
        self.teki_num = betterSpinBox(self, "Teki Number:", 0, 999, self.floorinfo.teki_num)
        self.item_num = betterSpinBox(self, "Item Number:", 0, 999, self.floorinfo.item_num)
        self.gate_num = betterSpinBox(self, "Gate Number:", 0, 999, self.floorinfo.gate_num)
        self.skybox = lineEditLable(self, "Skybox:", self.floorinfo.skybox)
        self.lighting = directoryButton(self, "Lighting File", self.floorinfo.lighting_file, keys.settings.light_path)
        self.units = directoryButton(self, "Unit File", self.floorinfo.unit_file, keys.settings.unit_path)
        self.plane = QCheckBox("Spawn Collision Plane")
        self.capinfo = QCheckBox("Use Capinfo")
        self.geyser = QCheckBox("Spawn Geyser")
        self.clog = QCheckBox("Clogged Hole")
        self.seesaw = QCheckBox("Spawn Seesaws")
        self.layout = QGridLayout()
        self.plane.setChecked(self.floorinfo.plane)
        self.geyser.setChecked(self.floorinfo.geyser)
        self.clog.setChecked(self.floorinfo.is_clogged)
        self.seesaw.setChecked(self.floorinfo.seesaw)
        self.capinfo.setChecked(self.floorinfo.use_cap)
        
        
        self.layout.addWidget(self.units, 0, 0)
        self.layout.addWidget(self.lighting, 0, 1)
        self.layout.addWidget(self.skybox, 1, 0)
        self.layout.addWidget(self.plane, 1, 1)

        self.layout.addWidget(self.geyser, 2, 0)
        self.layout.addWidget(self.clog, 2, 1)

        self.layout.addWidget(self.teki_num, 3, 0)
        self.layout.addWidget(self.item_num, 3, 1)
        self.layout.addWidget(self.gate_num, 4, 0)
        self.layout.addWidget(self.rooms, 4, 1)
        self.layout.addWidget(self.corridor_chance, 5, 0)
        self.layout.addWidget(self.dead_end, 5, 1)

        self.layout.addWidget(self.echo, 6, 0)
        self.layout.addWidget(self.music, 6, 1)

        self.layout.addWidget(self.timer, 7, 0)
        self.layout.addWidget(self.seesaw, 7, 1)
        self.layout.addWidget(self.capinfo, 8, 0)
        
        self.capinfo.stateChanged.connect(self.hide_capinfo)
        
        self.setLayout(self.layout)

    def update_floor(self):

        self.floorinfo.teki_num = self.teki_num.val
        self.floorinfo.item_num = self.item_num.val
        self.floorinfo.gate_num = self.gate_num.val
        self.floorinfo.room_num = self.rooms.val
        self.floorinfo.corridor_chance = self.corridor_chance.val
        self.floorinfo.geyser = self.geyser.isChecked()
        self.floorinfo.unit_file = self.units.edit.text()
        self.floorinfo.lighting_file = self.lighting.edit.text()
        self.floorinfo.skybox = self.skybox.text.text()
        self.floorinfo.is_clogged = self.clog.isChecked()
        self.floorinfo.echo = self.echo.val
        self.floorinfo.music = self.music.val
        self.floorinfo.plane = self.plane.isChecked()
        self.floorinfo.dead_end = self.dead_end.val
        self.floorinfo.use_cap = self.capinfo.isChecked()
        self.floorinfo.timer = self.timer.val
        self.floorinfo.seesaw = self.seesaw.isChecked()
        return self.floorinfo

    def hide_capinfo(self, val):
        self.parent.capinfo.setVisible(bool(val))

class Floor_tab(QWidget):
    def __init__(self, parent, floor, cave_dir, i):
        super(QWidget, self).__init__(parent)
        self.i = i
        self.floor = floor
        self.cave_dir = cave_dir
        self.layout = QGridLayout()
        self.floorinfo = Floorinfo_tab(self, floor.floorinfo, self.cave_dir)
        self.tekiinfo = TekiInfoBox(self, floor.tekiinfo)
        self.iteminfo = ItemInfoBox(self, floor.iteminfo)
        self.gateinfo = GateInfoBox(self, floor.gateinfo)
        self.layout.addWidget(self.floorinfo, 0, 0)
        self.layout.addWidget(self.tekiinfo, 0, 1, 2, 1)
        self.layout.addWidget(self.iteminfo, 1, 2)
        self.layout.addWidget(self.gateinfo, 1, 0)
        if self.floor.floorinfo.use_cap:
            self.capinfo = CapInfoBox(self, floor.capinfo)
            self.layout.addWidget(self.capinfo, 0, 2)
        else:
            self.capinfo = CapInfoBox(self, cave.CapInfo())
            self.capinfo.hide()
        self.setLayout(self.layout)
    
    def update_contents(self):
        floorinfo = self.floorinfo.update_floor()
        floorinfo.floor_end = self.i
        floorinfo.floor_start = self.i
        tekiinfo = self.tekiinfo.update_teki()
        iteminfo = self.iteminfo.update_item()
        gateinfo = self.gateinfo.update_gate()
        return_floor = cave.Floor(floorinfo, tekiinfo, iteminfo, gateinfo)
        if self.floor.floorinfo.use_cap:
            capinfo = self.capinfo.update_cap()
            return_floor.capinfo = capinfo
        return return_floor
    


class FloorTab(QWidget):
    
    def __init__(self, parent, cave_dir):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.cave_dir = cave_dir
        self.floors = parent.caveinfo.floors
        self.floor_num = parent.caveinfo.floor_count
        self.layout = QGridLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        
        # Add tabs
        self.initTabs()
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
    
    def initTabs(self):
        self.resize(1325, 800)
        for i, floor in enumerate(self.floors, 1):
            newtab = Floor_tab(self, floor, self.cave_dir, i - 1)
            if self.floor_num < 20:
                self.tabs.addTab(newtab, f"{i}")
    
    def add_tab(self, floors, floor_num):
        self.floors = floors
        self.floor_num = floor_num
        if len(floors) >= floor_num:
            self.tabs.addTab(Floor_tab(self, self.floors[self.tabs.count()], self.cave_dir, self.tabs.count()), f"{self.tabs.count() + 1}")
        else:
            self.floors.append(cave.get_default_floor())
            self.tabs.addTab(Floor_tab(self, cave.get_default_floor(), self.cave_dir, self.tabs.count()), f"{self.tabs.count() + 1}")

    def remove_tab(self, floors, floor_num):
        self.floors = floors
        self.floor_num = floor_num
        self.tabs.removeTab(self.tabs.count() - 1)

    def update_contents(self):
        for i in range(self.tabs.count()):
            self.floors[i] = self.tabs.widget(i).update_contents()
        return cave.CaveInfo(self.floor_num, self.floors)

class CaveTab(QMainWindow):
    def __init__(self, caveinfo:cave.CaveInfo, cave_dir:str):
        super().__init__()
        keys.init_items()
        self.caveinfo = caveinfo
        self.cave_dir = cave_dir

        self.floor_tabs = FloorTab(self, self.cave_dir)
        self.floor_tabs.move(75, 0)
        self.add_button = QPushButton(self)
        self.add_button.setText("Add Floor")
        self.add_button.move(550, 50)
        self.add_button.setFixedSize(100, 30)
        self.add_button.pressed.connect(self.add_floor)

        self.sub_button = QPushButton(self)
        self.sub_button.setText("Remove Floor")
        self.sub_button.move(750, 50)
        self.sub_button.setFixedSize(100, 30)
        self.sub_button.pressed.connect(self.sub_floor)

        openFile = QAction(QIcon('open.png'), '&Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new Cave')
        openFile.triggered.connect(self.open_new_cave)
        saveFile = QAction(QIcon('save.png'), '&Save', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save Cave to file')
        saveFile.triggered.connect(self.save_cave)
        saveAsFile = QAction(QIcon('save.png'), 'Save &As', self)
        saveAsFile.setShortcut('Ctrl+Shift+S')
        saveAsFile.setStatusTip('Save Cave to new file')
        saveAsFile.triggered.connect(self.save_as_cave)
        backup = QAction(QIcon('save.png'), '&Backup', self)
        backup.setShortcut('Ctrl+B')
        backup.setStatusTip('Save cave to backup file')
        backup.triggered.connect(self.save_backup)
        load_backup = QAction(QIcon('save.png'), '&Load Backup', self)
        load_backup.setShortcut('Ctrl+L')
        load_backup.setStatusTip('load cave from backup file')
        load_backup.triggered.connect(self.load_backup)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        fileMenu.addAction(saveAsFile)
        fileMenu.addAction(backup)
        fileMenu.addAction(load_backup)

        self.setGeometry(50, 50, 1400, 1000)
        self.setWindowTitle('Cave Editor')
        self.setCentralWidget(self.floor_tabs)
        self.show()

    def add_floor(self):
        self.caveinfo.floor_count += 1
        if self.caveinfo.floor_count == 35:
            self.add_button.blockSignals(True)
        self.sub_button.blockSignals(False)
        self.floor_tabs.update_contents()
        if len(self.caveinfo.floors) < self.caveinfo.floor_count:
            self.caveinfo.floors += [cave.get_default_floor()]
        self.floor_tabs.add_tab(self.caveinfo.floors, self.caveinfo.floor_count)
        self.floor_tabs.update_contents()

    def sub_floor(self):
        self.caveinfo.floor_count -= 1
        if self.caveinfo.floor_count == 1:
            self.sub_button.blockSignals(True)
        self.add_button.blockSignals(False)
        self.floor_tabs.update_contents()
        self.floor_tabs.remove_tab(self.caveinfo.floors, self.caveinfo.floor_count)
        self.floor_tabs.update_contents()

    def open_new_cave(self):
        cave_file = QFileDialog.getOpenFileName(self, "Open Cave File", self.cave_dir)
        if cave_file[0]:
            with open(cave_file[0], 'rb') as f:
                try:
                    self.cave_dir = cave_file[0]
                    data = f.readlines()
                    self.caveinfo = cave.read_cave(data)
                    self.floor_tabs.hide()
                    self.floor_tabs = FloorTab(self, self.cave_dir)
                    self.setCentralWidget(self.floor_tabs)
                    self.floor_tabs.show()
                    self.add_button.hide()
                    self.add_button = QPushButton(self)
                    self.add_button.setText("Add Floor")
                    self.add_button.move(110, 25)
                    self.add_button.setFixedSize(100, 30)
                    self.add_button.pressed.connect(self.add_floor)
                    self.add_button.show()
                    self.sub_button = QPushButton(self)
                    self.sub_button.setText("Remove Floor")
                    self.sub_button.move(260, 25)
                    self.sub_button.setFixedSize(100, 30)
                    self.sub_button.pressed.connect(self.sub_floor)
                    self.sub_button.hide()
                    self.sub_button.show()
                except Exception as e:
                    QMessageBox.critical(self, "Error reading cave", str(e))
    
    def save_cave(self):
        self.caveinfo = self.floor_tabs.update_contents()
        cave_file = self.cave_dir
        if not os.path.exists(cave_file):
            cave_file = QFileDialog.getSaveFileName(self, "Save Cave as", self.cave_dir)[0]
            if not cave_file.endswith(".txt"):
                cave_file += ".txt"
        with open(cave_file, 'w') as f:
            f.writelines(cave.export_cave(self.caveinfo))

    def save_as_cave(self):
        self.caveinfo = self.floor_tabs.update_contents()
        cave_file = QFileDialog.getSaveFileName(self, "Save Cave as", self.cave_dir)[0]
        if not cave_file.endswith(".txt"):
            cave_file += ".txt"
        self.cave_dir = cave_file
        with open(cave_file, 'w') as f:
            f.writelines(cave.export_cave(self.caveinfo))
    
    def save_backup(self):
        self.caveinfo = self.floor_tabs.update_contents()
        this = f"{pathlib.Path(__file__).parent.resolve()}/Backups/Cave/"
        try:
            with open(os.path.join(this, f"{datetime.datetime.now()}.pickle"), "wb+") as f:
                pickle.dump(self.caveinfo, f)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error saving backup", "Unable to save backup; backups folder is missing")

    
    def load_backup(self):
        this = f"{pathlib.Path(__file__).parent.resolve()}/Backups/Cave/"
        pickel_file = QFileDialog.getOpenFileName(self, "Open pickel data file", this, "Drought-Cave Pickle Data files (*.pickle)")
        if pickel_file[0]:
            with open(pickel_file[0], 'rb') as f:
                try:
                    self.caveinfo = pickle.load(f)
                    self.floor_tabs.hide()
                    self.floor_tabs = FloorTab(self, self.cave_dir)
                    self.setCentralWidget(self.floor_tabs)
                    self.floor_tabs.show()
                    self.add_button.hide()
                    self.add_button = QPushButton(self)
                    self.add_button.setText("Add Floor")
                    self.add_button.move(110, 25)
                    self.add_button.setFixedSize(100, 30)
                    self.add_button.pressed.connect(self.add_floor)
                    self.add_button.show()
                    self.sub_button = QPushButton(self)
                    self.sub_button.setText("Remove Floor")
                    self.sub_button.move(260, 25)
                    self.sub_button.setFixedSize(100, 30)
                    self.sub_button.pressed.connect(self.sub_floor)
                    self.sub_button.hide()
                    self.sub_button.show()
                except:
                    QMessageBox.critical(self, "Error reading cave", f"Backup is corrupt")
