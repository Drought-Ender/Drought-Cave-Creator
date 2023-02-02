import random
import pathlib
import os
import pickle
import copy
import datetime
import settings
from CaveLibrary.cave_optimiser import optimise_cave
import CaveLibrary.cave as cave
import CaveGenLinker
from PyQt6.QtWidgets import (
    QMainWindow, QLineEdit, QLabel, QMessageBox, QVBoxLayout, QGridLayout, QCheckBox, 
    QScrollArea, QComboBox, QListView, QHBoxLayout, QFileDialog, QWidget, QPushButton,
    QSpinBox, QDoubleSpinBox, QTabWidget, QDialog, QTabBar, QInputDialog, QMenu)
from PyQt6.QtGui import (QIcon, QAction, QPixmap, QMouseEvent, QDrag,
 QDragEnterEvent, QDragLeaveEvent, QDropEvent, QContextMenuEvent, QCursor)
from PyQt6.QtCore import Qt, QMimeData
from extra_widgets import betterSpinBox, betterSpinBoxFloat, AddSubButtons, lineEditLable, directoryButton


class Keys:
    def __init__(self):
        self.teki_keys = []
        self.all_teki = []
        self.all_item = []
        self.settings = copy.deepcopy(settings.settings)
    
    def init_items(self):
        self.settings = copy.deepcopy(settings.settings)
        self.teki_keys = [teki for teki in self.settings.teki_dict if self.settings.show_useless_teki or self.settings.teki_dict[teki]["use"]]
        if  self.settings.use_internal_names:
            self.all_teki = [(QIcon(f"presets/{ self.settings.preset}/tekiIcons/{teki}.png"), teki) for teki in  self.settings.teki_dict if self.settings.show_useless_teki or self.settings.teki_dict[teki]["use"]]
            self.all_item = [(QIcon(f"presets/{ self.settings.preset}/itemIcons/{item}.png"), item) for item in  self.settings.item_dict]
        else:
            self.all_teki = [(QIcon(f"presets/{ self.settings.preset}/tekiIcons/{teki}.png"), self.settings.teki_dict[teki]["common"]) for teki in  self.settings.teki_dict if self.settings.show_useless_teki or self.settings.teki_dict[teki]["use"]]
            self.all_item = [(QIcon(f"presets/{ self.settings.preset}/itemIcons/{item}.png"), self.settings.item_dict[item]) for item in  self.settings.item_dict]

keys = Keys()

class ItemWidget(QWidget):
    def __init__(self, parent, item):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.vlayout = QGridLayout()
        self.treasure = item
        if self.treasure.name in list(keys.settings.item_dict.keys()):
            self.item_index = list(keys.settings.item_dict.keys()).index(self.treasure.name)
        else:
            self.item_index = 0
        self.itemcombo = DefaultInfoMenu(self, keys.all_item, self.item_index)
        self.itemcombo.setToolTip("The name of the treasure to be spawned")
        self.spawn_count = QSpinBox()
        self.spawn_count.setValue(self.treasure.fill)
        self.spawn_count.setToolTip("Spawn Num")
        self.weight = QSpinBox()
        self.weight.setValue(self.treasure.weight)
        self.weight.setMaximum(9)
        self.weight.setToolTip("Weight")
        if keys.settings.show_item_weight:
            self.vlayout.addWidget(self.itemcombo, 0, 0, 1, 2)
            self.vlayout.addWidget(self.spawn_count, 1, 0)
            self.vlayout.addWidget(self.weight, 1, 1)
        else:
            self.vlayout.addWidget(self.itemcombo, 0, 0)
            self.vlayout.addWidget(self.spawn_count, 0, 1)

        self.setLayout(self.vlayout)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        self.menu = QMenu(self)
        delete = QAction("Delete", self)
        delete.triggered.connect(self.removeThisWidget)

        insert = QAction("Insert", self)
        insert.triggered.connect(self.addWidgetHere)
        self.menu.addAction(delete)
        self.menu.addAction(insert)
        self.menu.popup(QCursor().pos())

    def removeThisWidget(self):
        self.parent.sub_obj_at(self)

    def addWidgetHere(self):
        self.parent.add_obj_at(self)

class ItemInfoBox(QScrollArea):
    def __init__(self, parent, iteminfo):
        super(QWidget, self).__init__(parent)
        self.this_widget = QWidget()
        self.name = QLabel("ItemInfo")
        self.name.setToolTip("Decides how treasures on the floor are spawned")
        self.iteminfo = iteminfo
        self.vlayout = QVBoxLayout(self.this_widget)
        self.vlayout.addWidget(self.name)
        self.items = []
        for i, item in enumerate(self.iteminfo.items):
            if i < self.iteminfo.item_count:
                next_widget = ItemWidget(self, item)
                self.items.append(next_widget)
                self.vlayout.addWidget(next_widget)
        self.buttons = AddSubButtons(self)
        self.buttons.check_disable(len(self.iteminfo.items))
        self.vlayout.addWidget(self.buttons)
        self.setWidget(self.this_widget)
        self.setWidgetResizable(True)

    def update_item(self):
        self.iteminfo = cave.ItemInfo(0, [])
        for item in self.this_widget.children():
            new_item = cave.Treasure("ahiru", 0, 0)
            if not isinstance(item, ItemWidget):
                continue
            new_item.name = list(keys.settings.item_dict.keys())[item.itemcombo.currentIndex()]
            new_item.fill = item.spawn_count.value()
            new_item.weight = item.weight.value()
            self.iteminfo.items.append(copy.deepcopy(new_item))
        self.iteminfo.item_count = len(self.iteminfo.items)
        return self.iteminfo

    def add_obj(self):
        self.iteminfo.items.append(cave.Treasure("ahiru", 0, 0))
        new_widget = ItemWidget(self, cave.Treasure("ahiru", 0, 0))
        self.items += [new_widget]
        self.vlayout.insertWidget(len(self.items), new_widget)
        self.buttons.check_disable(len(self.iteminfo.items))
    
    def sub_obj(self):
        self.iteminfo.items.pop()
        remove = self.items.pop()
        self.vlayout.removeWidget(remove)
        self.buttons.check_disable(len(self.iteminfo.items))


    def sub_obj_at(self, widget):
        widgetIdx:int = self.vlayout.indexOf(widget)
        self.iteminfo.items.pop(widgetIdx - 1)
        self.items.pop(widgetIdx - 1)
        self.vlayout.removeWidget(widget)
        self.buttons.check_disable(len(self.iteminfo.items))

    def add_obj_at(self, widget):
        widgetIdx:int = self.vlayout.indexOf(widget)
        self.iteminfo.items.insert(widgetIdx - 1, cave.Treasure("ahiru", 0, 0))
        new_widget = ItemWidget(self, cave.Treasure("ahiru", 0, 0))
        self.items.insert(widgetIdx - 1, new_widget)
        self.vlayout.insertWidget(widgetIdx, new_widget)
        self.buttons.check_disable(len(self.iteminfo.items))

class GateWidget(QWidget):
    def __init__(self, parent, gate):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout()
        self.gate = gate
        self.name = QLineEdit(self.gate.name)
        self.name.setToolTip("Gate Name, does nothing")
        self.life = QDoubleSpinBox()
        self.life.setMaximum(999999.999999)
        self.life.setValue(self.gate.life)
        self.life.setToolTip("Gate Health")
        self.weight = QSpinBox()
        self.weight.setValue(self.gate.weight)
        self.weight.setMaximum(9)
        self.weight.setMinimum(1)
        self.weight.setToolTip("Weight")
        if keys.settings.show_gate_name:
            self.layout.addWidget(self.name)
        self.layout.addWidget(self.life)
        self.layout.addWidget(self.weight)

        self.setLayout(self.layout)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        self.menu = QMenu(self)
        delete = QAction("Delete", self)
        delete.triggered.connect(self.removeThisWidget)

        insert = QAction("Insert", self)
        insert.triggered.connect(self.addWidgetHere)
        self.menu.addAction(delete)
        self.menu.addAction(insert)
        self.menu.popup(QCursor().pos())

    def removeThisWidget(self):
        self.parent.sub_obj_at(self)

    def addWidgetHere(self):
        self.parent.add_obj_at(self)

class GateInfoBox(QScrollArea):
    def __init__(self, parent, gateinfo):
        super(QWidget, self).__init__(parent)
        self.this_widget = QWidget()
        self.name = QLabel("GateInfo")
        self.name.setToolTip("Sets the gates that spawn on the floor")
        self.gateinfo = gateinfo
        self.vlayout = QVBoxLayout(self.this_widget)
        self.vlayout.addWidget(self.name)
        self.gates = []
        for i, gate in enumerate(self.gateinfo.gates):
            if i < self.gateinfo.gate_count:
                next_widget = GateWidget(self, gate)
                self.gates.append(next_widget)
                self.vlayout.addWidget(next_widget)
        self.buttons = AddSubButtons(self)
        self.buttons.check_disable(len(self.gateinfo.gates))
        self.vlayout.addWidget(self.buttons)
        self.setWidget(self.this_widget)
        self.setWidgetResizable(True)
    
    def update_gate(self):
        self.gateinfo = cave.GateInfo(0, [])
        for gate in self.this_widget.children():
            new_gate = cave.Gate("gate", 1000.0, 1)
            if not isinstance(gate, GateWidget):
                continue
            new_gate.name = gate.name.text()
            new_gate.life = gate.life.value()
            new_gate.weight = gate.weight.value()
            self.gateinfo.gates.append(copy.deepcopy(new_gate))
        self.gateinfo.gate_count = len(self.gateinfo.gates)
        return self.gateinfo

    def add_obj(self):
        self.gateinfo.gates.append(cave.Gate("gate", 1000.0, 1))
        new_widget = GateWidget(self, cave.Gate("gate", 1000.0, 1))
        self.gates += [new_widget]
        self.vlayout.insertWidget(len(self.gates), new_widget)
        self.buttons.check_disable(len(self.gateinfo.gates))
    
    def sub_obj(self):
        self.gateinfo.gates.pop()
        remove = self.gates.pop()
        self.vlayout.removeWidget(remove)
        self.buttons.check_disable(len(self.gateinfo.gates))


    def sub_obj_at(self, widget):
        widgetIdx:int = self.vlayout.indexOf(widget)
        self.gateinfo.gates.pop(widgetIdx - 1)
        self.gates.pop(widgetIdx - 1)
        self.vlayout.removeWidget(widget)
        self.buttons.check_disable(len(self.gateinfo.gates))

    def add_obj_at(self, widget):
        widgetIdx:int = self.vlayout.indexOf(widget)
        self.gateinfo.gates.insert(widgetIdx - 1, cave.Gate("gate", 1000.0, 1))
        new_widget = GateWidget(self, cave.Gate("gate", 1000.0, 1))
        self.gates.insert(widgetIdx - 1, new_widget)
        self.vlayout.insertWidget(widgetIdx, new_widget)
        self.buttons.check_disable(len(self.gateinfo.gates))

class TekiInfoBox(QScrollArea):
    def __init__(self, parent, tekiinfo):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.dragWidget = None
        self.setAcceptDrops(True)
        self.this_widget = QWidget()
        self.name = QLabel("TekiInfo")
        self.name.setToolTip("Decides how the enemies on the floor are spawned")
        self.tekiinfo = tekiinfo
        self.vlayout = QVBoxLayout(self.this_widget)
        self.vlayout.addWidget(self.name)
        self.tekis = []
        for i, teki in enumerate(self.tekiinfo.tekis):
            if i < self.tekiinfo.teki_count:
                self.tekis.append(TekiWidget(self, teki))
                self.vlayout.addWidget(self.tekis[-1])

        self.buttons = AddSubButtons(self)
        self.buttons.check_disable(len(self.tekiinfo.tekis))
        self.vlayout.addWidget(self.buttons)
        self.setWidget(self.this_widget)


        self.setWidgetResizable(True)
    
    def update_teki(self):
        self.tekiinfo = cave.TekiInfo(0, [])
        for teki in self.this_widget.children():
            new_teki = cave.Teki("Chappy", 1, 0, 0, False, "ahiru", 0)
            if not isinstance(teki, TekiWidget):
                continue
            new_teki.name = keys.teki_keys[teki.tekicombo.currentIndex()]
            if teki.itemcombo.currentIndex() == 0:
                new_teki.item = list(keys.settings.item_dict.keys())[0]
                new_teki.has_item = False
            else:
                new_teki.item = list(keys.settings.item_dict.keys())[teki.itemcombo.currentIndex() - 1]
                new_teki.has_item = True
            new_teki.falltype = teki.fall.currentIndex()
            new_teki.fill = teki.spawn_count.value()
            new_teki.weight = teki.weight.value()
            new_teki.spawn = teki.spawn.currentIndex()
            self.tekiinfo.tekis.append(copy.deepcopy(new_teki))
        self.tekiinfo.teki_count = len(self.tekiinfo.tekis)
        return self.tekiinfo

    def add_obj(self):
        self.tekiinfo.tekis.append(cave.Teki("Chappy", 0, 0, 0, False, "ahiru", 0))
        new_widget = TekiWidget(self, cave.Teki("Chappy", 0, 0, 0, False, "ahiru", 0))
        self.tekis.append(new_widget)
        self.vlayout.insertWidget(len(self.tekis), new_widget)
        self.buttons.check_disable(len(self.tekiinfo.tekis))
    
    def sub_obj(self):
        self.tekiinfo.tekis.pop()
        remove = self.tekis.pop()
        self.vlayout.removeWidget(remove)
        self.buttons.check_disable(len(self.tekiinfo.tekis))

    def sub_obj_at(self, widget):
        widgetIdx:int = self.vlayout.indexOf(widget)
        self.tekiinfo.tekis.pop(widgetIdx - 1)
        self.tekis.pop(widgetIdx - 1)
        self.vlayout.removeWidget(widget)
        self.buttons.check_disable(len(self.tekiinfo.tekis))

    def add_obj_at(self, widget):
        widgetIdx:int = self.vlayout.indexOf(widget)
        self.tekiinfo.tekis.insert(widgetIdx - 1,cave.Teki("Chappy", 0, 0, 0, False, "ahiru", 0))
        new_widget = TekiWidget(self, cave.Teki("Chappy", 0, 0, 0, False, "ahiru", 0))
        self.tekis.insert(widgetIdx - 1, new_widget)
        self.vlayout.insertWidget(widgetIdx, new_widget)
        self.buttons.check_disable(len(self.tekiinfo.tekis))
        
    def dragEnterEvent(self, drag: QDragEnterEvent) -> None:
        self.dragWidget = drag.source()
        self.dragWidget.hide()
        drag.accept()

    def dragLeaveEvent(self, _) -> None:
        self.dragWidget.show()


    def dropEvent(self, drop: QDropEvent) -> None:
        pos = drop.position()
        widget:QWidget = drop.source()
        widget.show()
        widgetIdx = self.vlayout.indexOf(widget) - 1
        print(f"{pos.y()}")
        widgets = (
            (n, self.vlayout.itemAt(n).widget()) for n in range(self.vlayout.count()) 
            if isinstance(self.vlayout.itemAt(n).widget(), TekiWidget)
        )
        for trueIdx, bunch in enumerate(widgets):
            i, w = bunch
            if w == widget:
                continue
            if pos.y() < (w.y() + w.size().height() // 2):
                break
        
        self.vlayout.insertWidget(i, widget)
        
        self.tekis[trueIdx], self.tekis[widgetIdx] = self.tekis[widgetIdx], self.tekis[trueIdx]




        
            
            
            
        

class CapWidget(QWidget):
    def __init__(self, parent, cap:cave.Cap):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.layout = QGridLayout()
        self.cap = cap
        name = self.cap.name
        self.index = keys.teki_keys.index(name)
        self.tekicombo = DefaultInfoMenu(self, keys.all_teki, self.index)
        if keys.settings.autoteki:
            self.tekicombo.currentIndexChanged.connect(self.update_fallheld)
        self.tekicombo.setToolTip("The name of the teki being spawned")
        self.spawn_count = QSpinBox()
        self.spawn_count.setValue(self.cap.fill)
        self.spawn_count.setToolTip("Spawn Num")
        
        self.weight = QSpinBox()
        self.weight.setValue(self.cap.weight)
        self.weight.setMaximum(9)
        self.weight.setToolTip("Weight")
        self.fall = QComboBox()
        self.fall.addItems(["None", "All", "Pikmin", "Captain", "Carry", "Purple"])
        self.fall.setCurrentIndex(self.cap.falltype)
        self.fall.setToolTip("Fall Activation")
        if self.cap.item in list(keys.settings.item_dict.keys()):
            self.item_index = list(keys.settings.item_dict.keys()).index(self.cap.item)
        else:
            self.item_index = 0
        item_with_none = [(QIcon(f"presets/{keys.settings.preset}/itemIcons/None.png"), "None")] + keys.all_item
        if (self.cap.has_item):
            self.itemcombo = DefaultInfoMenu(self, item_with_none, self.item_index + 1)
        else:
            self.itemcombo = DefaultInfoMenu(self, item_with_none, 0)
        self.itemcombo.setToolTip("The name of the Tekis' Held Item")
        self.double = QCheckBox("Only One")
        self.double.setChecked(self.cap.dont_dupe)
        self.double.setToolTip("If left unchecked, will spawn 2 teki in the same cap instead of one")
        self.cap_type = QSpinBox()
        self.cap_type.setValue(self.cap.cap_type)
        self.cap_type.setToolTip("Type of cap to spawn in, if set to 1 or more it does not spawn")
        
        if keys.settings.autoteki:
            self.update_fallheld(self.index)

        self.layout.addWidget(self.tekicombo, 0, 0, 1, 3)
        self.layout.addWidget(self.itemcombo, 1, 0, 1, 2)
        self.layout.addWidget(self.fall, 1, 2)
        self.layout.addWidget(self.spawn_count, 2, 0)
        self.layout.addWidget(self.weight, 2, 1)
        self.layout.addWidget(self.double, 2, 2)
        if keys.settings.show_captype:
            self.layout.addWidget(self.cap_type, 3, 0)

        self.setLayout(self.layout)

    def update_fallheld(self, index):
        if keys.settings.teki_dict[keys.teki_keys[index]]["fall"]:
            self.fall.show()
        else:
            self.fall.setCurrentIndex(0)
            self.fall.hide()
        if keys.settings.teki_dict[keys.teki_keys[index]]["item"]:
            self.itemcombo.show()
        else:
            self.fall.setCurrentIndex(0)
            self.itemcombo.hide()

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        self.menu = QMenu(self)
        delete = QAction("Delete", self)
        delete.triggered.connect(self.removeThisWidget)

        insert = QAction("Insert", self)
        insert.triggered.connect(self.addWidgetHere)
        self.menu.addAction(delete)
        self.menu.addAction(insert)
        self.menu.popup(QCursor().pos())

    def removeThisWidget(self):
        self.parent.sub_obj_at(self)

    def addWidgetHere(self):
        self.parent.add_obj_at(self)


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
        self.name = QLabel("CapInfo")
        self.name.setToolTip("Sets the enemies that spawn in item caps")
        self.capinfo = capinfo
        self.vlayout = QVBoxLayout(self.this_widget)
        self.vlayout.addWidget(self.name)
        self.caps = []
        for i, cap in enumerate(self.capinfo.caps):
            if i < self.capinfo.cap_count:
                self.caps.append(CapWidget(self, cap))
                self.vlayout.addWidget(self.caps[-1])
        self.buttons = AddSubButtons(self)
        self.buttons.check_disable(len(self.capinfo.caps))
        self.vlayout.addWidget(self.buttons)
        self.setWidget(self.this_widget)


        self.setWidgetResizable(True)
    
    def update_cap(self):
        self.capinfo = cave.CapInfo(0, [])
        for cap in self.this_widget.children():
            new_cap = cave.Cap(0, "Chappy", 0, 0, 0, False, "ahiru", True)
            if not isinstance(cap, CapWidget):
                continue
            new_cap.name = keys.teki_keys[cap.tekicombo.currentIndex()]
            if cap.itemcombo.currentIndex() == 0:
                new_cap.item = list(keys.settings.item_dict.keys())[0]
                new_cap.has_item = False
            else:
                new_cap.item = list(keys.settings.item_dict.keys())[cap.itemcombo.currentIndex() - 1]
                new_cap.has_item = True
            new_cap.falltype = cap.fall.currentIndex()
            new_cap.fill = cap.spawn_count.value()
            new_cap.weight = cap.weight.value()
            new_cap.dont_dupe = cap.double.isChecked()
            new_cap.cap_type = cap.cap_type.value()
            self.capinfo.caps.append(copy.deepcopy(new_cap))
        self.capinfo.cap_count = len(self.capinfo.caps)
        return self.capinfo

    def add_obj(self):
        self.capinfo.caps.append(cave.Cap(0, "Chappy", 0, 0, 0, False, "ahiru", True))
        new_widget = CapWidget(self, cave.Cap(0, "Chappy", 0, 0, 0, False, "ahiru", True))
        self.caps += [new_widget]
        self.vlayout.insertWidget(len(self.caps), new_widget)
        self.buttons.check_disable(len(self.capinfo.caps))
    
    def sub_obj(self):
        self.capinfo.caps.pop()
        remove = self.caps.pop()
        self.vlayout.removeWidget(remove)
        self.buttons.check_disable(len(self.capinfo.caps))

    def sub_obj_at(self, widget):
        widgetIdx:int = self.vlayout.indexOf(widget)
        self.capinfo.caps.pop(widgetIdx - 1)
        self.caps.pop(widgetIdx - 1)
        self.vlayout.removeWidget(widget)
        self.buttons.check_disable(len(self.capinfo.caps))

    def add_obj_at(self, widget):
        widgetIdx:int = self.vlayout.indexOf(widget)
        self.capinfo.caps.insert(widgetIdx - 1, cave.Cap(0, "Chappy", 0, 0, 0, False, "ahiru", True))
        new_widget = CapWidget(self, cave.Cap(0, "Chappy", 0, 0, 0, False, "ahiru", True))
        self.caps.insert(widgetIdx - 1, new_widget)
        self.vlayout.insertWidget(widgetIdx, new_widget)
        self.buttons.check_disable(len(self.capinfo.caps))


class TekiWidget(QWidget):
    def __init__(self, parent, teki:cave.Teki):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.setAcceptDrops(True)
        self.glayout = QGridLayout()
        self.teki = teki
        name = self.teki.name
        self.index = keys.teki_keys.index(name)
        self.tekicombo = DefaultInfoMenu(self, keys.all_teki, self.index)
        if keys.settings.autoteki:
            self.tekicombo.currentIndexChanged.connect(self.update_fallheld)
        self.tekicombo.setToolTip("Name of the Teki being spawned")
        self.spawn_count = QSpinBox()
        self.spawn_count.setValue(self.teki.fill)
        self.spawn_count.setToolTip("Spawn Num")
        self.weight = QSpinBox()
        self.weight.setValue(self.teki.weight)
        self.weight.setMaximum(9)
        self.weight.setToolTip("Weight")
        self.fall = QComboBox()
        self.fall.addItems(["None", "All", "Pikmin", "Captain", "Carry", "Purple"])
        self.fall.setCurrentIndex(self.teki.falltype)
        self.fall.setToolTip("Fall Activation")
        if self.teki.item in list(keys.settings.item_dict.keys()):
            self.item_index = list(keys.settings.item_dict.keys()).index(self.teki.item)
        else:
            self.item_index = 0
        item_with_none = [(QIcon(f"presets/{keys.settings.preset}/itemIcons/None.png"), "None")] + keys.all_item
        if (self.teki.has_item):
            self.itemcombo = DefaultInfoMenu(self, item_with_none, self.item_index + 1)
        else:
            self.itemcombo = DefaultInfoMenu(self, item_with_none, 0)
        self.itemcombo.setToolTip("The Teki's held item")
        self.spawn = QComboBox()
        if keys.settings.use_internal_groups:
            self.spawn.addItems(["Teki A", "Teki B", "Item", "None", "FixObj", "Teki C", "Plant", "Start", "Teki F"])
        else:
            self.spawn.addItems(["Easy", "Hard", "Item", "None", "Hole", "Seams", "Plant", "Pod", "Special"])
        self.spawn.setCurrentIndex(self.teki.spawn)
        self.spawn.setView(QListView())
        self.spawn.setToolTip("The type of node the teki will spawn at,\n only Easy, Hard, Seams, Plant, Pod, and Special work")
        if keys.settings.autoteki:
            self.check_autoupdate(self.teki.spawn)
            self.spawn.currentIndexChanged.connect(self.check_autoupdate)
            self.update_fallheld(self.index)

        self.glayout.addWidget(self.tekicombo, 0, 0, 1, 3)
        self.glayout.addWidget(self.itemcombo, 1, 0, 1, 2)
        self.glayout.addWidget(self.fall, 1, 2)
        self.glayout.addWidget(self.spawn_count, 2, 0)
        self.glayout.addWidget(self.weight, 2, 1)
        self.glayout.addWidget(self.spawn, 2, 2)

        self.setLayout(self.glayout)
    
    def check_autoupdate(self, index):
        if index == 6:
            self.weight.hide()
        else:
            self.weight.show()
    
    def update_fallheld(self, index):
        if keys.settings.teki_dict[keys.teki_keys[index]]["fall"]:
            self.fall.show()
        else:
            self.fall.setCurrentIndex(0)
            self.fall.hide()
        if keys.settings.teki_dict[keys.teki_keys[index]]["item"]:
            self.itemcombo.show()
        else:
            self.fall.setCurrentIndex(0)
            self.itemcombo.hide()
    
    def mouseMoveEvent(self, mouse: QMouseEvent) -> None:
        # removing this functionality for now bc it's buggy
        return
        if (mouse.buttons() == Qt.MouseButton.LeftButton):
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec(Qt.DropAction.MoveAction)
    
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        self.menu = QMenu(self)
        delete = QAction("Delete", self)
        delete.triggered.connect(self.removeThisWidget)

        insert = QAction("Insert", self)
        insert.triggered.connect(self.addWidgetHere)
        self.menu.addAction(delete)
        self.menu.addAction(insert)
        self.menu.popup(QCursor().pos())

    def removeThisWidget(self):
        self.parent.sub_obj_at(self)

    def addWidgetHere(self):
        self.parent.add_obj_at(self)
    



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

class Floorinfo_tab(QWidget):
    def __init__(self, parent, floorinfo, cave_dir):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.cave_dir = cave_dir
        self.floorinfo = floorinfo
        self.dead_end = betterSpinBox(self, "Dead End %", 0, 100, self.floorinfo.dead_end)
        self.dead_end.setToolTip("The chance of a hallway being assigned a dead end instead")
        self.echo = betterComboBox(self, "Echo Type:", ["Soil", "Metal", "Concrete", "Tile", "Garden", "Toy"], self.floorinfo.echo)
        self.echo.setToolTip("The potency of the echo on the floor,\nsoil has a lot of echo and toy is almost unnoticeable")
        self.music = betterComboBox(self, "Music type:", ["Normal", "Boss", "Rest"], self.floorinfo.music)
        self.music.setToolTip("The music type,\nnormal plays the normal music,\nboss mutes until fighting the boss,\nrest plays rest floot music")
        self.rooms = betterSpinBox(self, "Room Number:", 0, 99, self.floorinfo.room_num)
        self.rooms.setToolTip("The amount of rooms the floor will try to generate")
        self.corridor_chance = betterSpinBoxFloat(self, "Corridor Probability:", 0, 1, self.floorinfo.corridor_chance)
        self.corridor_chance.setToolTip("The chance of the floor placing a corridor instead of a room")
        self.timer = betterSpinBoxFloat(self, "Wraith Timer:", 0, 99999, self.floorinfo.timer)
        self.timer.setToolTip("Time (in seconds) it takes the Waterwraith to spawn,\nignored on the final floor")
        self.corridor_chance.slide.setSingleStep(0.01)
        self.teki_num = betterSpinBox(self, "Teki Number:", 0, 999, self.floorinfo.teki_num)
        self.teki_num.setToolTip("The maximum number of easy, hard, seams, and special teki the floor will spawn")
        self.item_num = betterSpinBox(self, "Item Number:", 0, 999, self.floorinfo.item_num)
        self.item_num.setToolTip("The maximum number of items the floor will spawn")
        self.gate_num = betterSpinBox(self, "Gate Number:", 0, 999, self.floorinfo.gate_num)
        self.gate_num.setToolTip("The number of gates the floor will spawn")
        self.skybox = lineEditLable(self, "Skybox:", self.floorinfo.skybox)
        self.skybox.setToolTip("The skybox the floor will use")
        self.lighting = directoryButton(self, "Lighting File", self.floorinfo.lighting_file, keys.settings.light_path)
        self.lighting.setToolTip("The lighting file the floor will load")
        self.units = directoryButton(self, "Unit File", self.floorinfo.unit_file, keys.settings.units_path)
        self.units.setToolTip("The units file that the floor will use")
        self.plane = QCheckBox("Spawn Collision Plane")
        self.plane.setToolTip("If checked, spawns an invisable plan at y = 0 that gives flooring skyboxes collision")
        if not keys.settings.always_capinfo:
            self.capinfo = QCheckBox("Use Capinfo")
            self.capinfo.setChecked(self.floorinfo.use_cap)
            self.capinfo.setToolTip("If unchacked, removes the capinfo")
        self.geyser = QCheckBox("Spawn Geyser")
        self.geyser.setToolTip("If checked, spawns an exit geyser on the floor")
        self.clog = QCheckBox("Clogged Hole")
        self.clog.setToolTip("If checked, clogs the next sublevel hole")
        self.seesaw = QCheckBox("Spawn Seesaws")
        self.seesaw.setToolTip("if checked, spawn 2 connected seesaws somewhere in the level")
        self.layout = QGridLayout()
        self.plane.setChecked(self.floorinfo.plane)
        self.geyser.setChecked(self.floorinfo.geyser)
        self.clog.setChecked(self.floorinfo.is_clogged)
        self.seesaw.setChecked(self.floorinfo.seesaw)
        
        
        
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
        if not keys.settings.always_capinfo:
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
        self.floorinfo.use_cap = keys.settings.always_capinfo or self.capinfo.isChecked()
        self.floorinfo.timer = self.timer.val
        self.floorinfo.seesaw = self.seesaw.isChecked()
        return self.floorinfo

    def hide_capinfo(self, val):
        self.parent.capinfo.setVisible(bool(val))

class FloorTab(QWidget):
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
        if keys.settings.always_capinfo:
            if self.floor.floorinfo.use_cap:
                self.capinfo = CapInfoBox(self, floor.capinfo)
            else:
                self.capinfo = CapInfoBox(self, cave.CapInfo(0, []))
            self.floor.floorinfo.use_cap = True
        else:
            if self.floor.floorinfo.use_cap:
                self.capinfo = CapInfoBox(self, floor.capinfo)
            else:
                self.capinfo = CapInfoBox(self, cave.CapInfo(0, []))
                self.capinfo.hide()

        self.layout.addWidget(self.capinfo, 0, 2)
        self.setLayout(self.layout)
    
    def update_contents(self, i):
        floorinfo = self.floorinfo.update_floor()
        floorinfo.floor_end = i
        floorinfo.floor_start = i
        tekiinfo = self.tekiinfo.update_teki()
        iteminfo = self.iteminfo.update_item()
        gateinfo = self.gateinfo.update_gate()
        return_floor = cave.Floor(floorinfo, tekiinfo, iteminfo, gateinfo)
        if self.floor.floorinfo.use_cap:
            capinfo = self.capinfo.update_cap()
            return_floor.capinfo = capinfo
        return return_floor
    

class FloorTabBar(QTabBar):

    def __init__(self, parent):
        super().__init__(parent)

    def mouseDoubleClickEvent(self, mouse: QMouseEvent) -> None:
        idx:int = self.currentIndex()
        ok:bool = True
        newName, ok = QInputDialog.getText(self, "Change Name", "Insert New Floor Name", QLineEdit.EchoMode.Normal, self.tabText(idx))
        if (ok):
            self.setTabText(idx, newName)
        return super().mouseDoubleClickEvent(mouse)
    
class FloorTabHolder(QWidget):
    
    def __init__(self, parent, cave_dir):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.cave_dir = cave_dir
        self.floors = parent.caveinfo.floors
        self.floor_num = parent.caveinfo.floor_count
        self.layout = QVBoxLayout(self)
        self.buttons = AddSubButtons(self)
        self.buttons.add_item.setText("Add Floor")
        self.buttons.sub_item.setText("Remove Floor")
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabs.setTabBar(FloorTabBar(self))
        self.tabs.setMovable(True)
        
        # Add tabs
        self.initTabs()
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    
    def initTabs(self):
        self.resize(1325, 800)
        for i, floor in enumerate(self.floors, 1):
            newtab = FloorTab(self, floor, self.cave_dir, i - 1)
            self.tabs.addTab(newtab, f"Floor {i}")
    
    def add_tab(self, floors, floor_num):
        self.floors = floors
        self.floor_num = floor_num
        if len(floors) >= floor_num:
            self.tabs.addTab(FloorTab(self, self.floors[self.tabs.count()], self.cave_dir, self.tabs.count()), f"Floor {self.tabs.count() + 1}")
        else:
            self.floors.append(cave.get_default_floor())
            self.tabs.addTab(FloorTab(self, cave.get_default_floor(), self.cave_dir, self.tabs.count()), f"Floor {self.tabs.count() + 1}")

    def remove_tab(self, floors, floor_num):
        self.floors = floors
        self.floor_num = floor_num
        self.tabs.removeTab(self.tabs.count() - 1)

    def update_contents(self):
        for i in range(self.tabs.count()):
            self.floors[i] = self.tabs.widget(i).update_contents(i)
        return cave.CaveInfo(self.floor_num, self.floors)

    def add_obj(self):
        self.floor_num += 1
        if self.floor_num == 35:
            self.buttons.add_item.blockSignals(True)
        self.buttons.sub_item.blockSignals(False)
        self.update_contents()
        if len(self.floors) < self.floor_num:
            self.floors += [cave.get_default_floor()]
        self.add_tab(self.floors, self.floor_num)
        self.update_contents()

    def sub_obj(self):
        self.floor_num -= 1
        if self.floor_num == 1:
            self.buttons.sub_item.blockSignals(True)
        self.buttons.add_item.blockSignals(False)
        self.update_contents()
        self.remove_tab(self.floors, self.floor_num)
        self.update_contents()

class CaveGenPopup(QDialog):
    def __init__(self, parent, path, seed = False):
        super().__init__(parent)
        self.setWindowTitle('CaveGen Output')
        self.layout = QVBoxLayout(self)
        self.label = QLabel(self)
        self.label.setScaledContents(True)
        
        self.label.setPixmap(QPixmap(path))
        sz = self.label.pixmap().size()
        self.label.setMaximumSize(800 * sz.width() // sz.height(), 800)
        self.layout.addWidget(self.label)
        if seed:
            self.seed = QLabel(f"Seed: {hex(seed)}", self)
            self.layout.addWidget(self.seed)
        self.setLayout(self.layout)

class CaveTab(QMainWindow):
    def __init__(self, caveinfo:cave.CaveInfo, cave_dir:str):
        super().__init__()
        keys.init_items()
        self.caveinfo = caveinfo
        self.cave_dir = cave_dir

        self.FloorTabs = FloorTabHolder(self, self.cave_dir)
        self.FloorTabs.move(75, 0)

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
        caveGen = QAction('Cave&Gen', self)
        caveGen.setShortcut('Ctrl+G')
        caveGen.setStatusTip('Run CaveGen Preview')
        caveGen.triggered.connect(self.run_cavegen)
        caveInfo = QAction('Cave&Info', self)
        caveInfo.setShortcut('Ctrl+I')
        caveInfo.setStatusTip('Run CaveInfo Preview')
        caveInfo.triggered.connect(self.run_caveinfo)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(saveFile)
        fileMenu.addAction(saveAsFile)
        fileMenu.addAction(backup)
        fileMenu.addAction(load_backup)
        actionMenu = menubar.addMenu("&Actions")
        actionMenu.addAction(caveGen)
        actionMenu.addAction(caveInfo)

        self.setGeometry(50, 50, 1400, 1000)
        self.setWindowTitle('Cave Editor')
        self.setCentralWidget(self.FloorTabs)
        self.show()

    def run_cavegen(self):
        floor = self.FloorTabs.tabs.currentIndex()
        self.caveinfo = self.FloorTabs.update_contents()
        if not os.path.exists(f"{keys.settings.units_path}/{self.caveinfo.floors[floor].floorinfo.unit_file}"):
            QMessageBox.warning(self, "File Missing", "Units file could not be located")
            return
        seed = random.randint(0, 0xFFFFFFFF)
        path = CaveGenLinker.run_cavegen(self.caveinfo, f"{keys.settings.units_path}/{self.caveinfo.floors[floor].floorinfo.unit_file}", floor + 1, seed)
        if os.path.exists(path):
            cavegen = CaveGenPopup(self, path, seed)
            cavegen.show()
        else:
            QMessageBox.critical(self, "Error Loading Cave and Units files", "Error Loading Cave and Units files; Cavegen did not return")

    def run_caveinfo(self):
        floor = self.FloorTabs.tabs.currentIndex()
        self.caveinfo = self.FloorTabs.update_contents()
        if not os.path.exists(f"{keys.settings.units_path}/{self.caveinfo.floors[floor].floorinfo.unit_file}"):
            QMessageBox.warning(self, "File Missing", "Units file could not be located")
            return
        path = CaveGenLinker.run_caveinfo(self.caveinfo, f"{keys.settings.units_path}/{self.caveinfo.floors[floor].floorinfo.unit_file}", floor + 1)
        if os.path.exists(path):
            cavegen = CaveGenPopup(self, path)
            cavegen.show()
        else:
            QMessageBox.critical(self, "Error Loading Cave and Units files", "Error Loading Cave and Units files; Cavegen did not return")

    def open_new_cave(self):
        if os.path.exists(keys.settings.cave_path):
            self.cave_dir = keys.settings.cave_path
        cave_file = QFileDialog.getOpenFileName(self, "Open Cave File", self.cave_dir)
        if cave_file[0]:
            with open(cave_file[0], 'rb') as f:
                try:
                    data = f.readlines()
                    self.caveinfo = cave.read_cave(data)
                except Exception as e:
                    QMessageBox.critical(self, "Error reading cave", str(e))
                else:
                    self.cave_dir = cave_file[0]
                    self.FloorTabs.hide()
                    self.FloorTabs = FloorTabHolder(self, self.cave_dir)
                    self.setCentralWidget(self.FloorTabs)
                    self.FloorTabs.show()

    
    def save_cave(self):
        self.caveinfo = self.FloorTabs.update_contents()
        cave_file = self.cave_dir
        if not os.path.exists(cave_file):
            cave_file = QFileDialog.getSaveFileName(self, "Save Cave as", self.cave_dir)[0]
            if not cave_file.endswith(".txt"):
                cave_file += ".txt"
        with open(cave_file, 'w',  encoding='utf-8') as f:
            f.writelines(cave.export_cave(self.caveinfo))

    def save_as_cave(self):
        self.caveinfo = self.FloorTabs.update_contents()
        cave_file = QFileDialog.getSaveFileName(self, "Save Cave as", self.cave_dir)[0]
        if not cave_file.endswith(".txt"):
            cave_file += ".txt"
        self.cave_dir = cave_file
        with open(cave_file, 'w',  encoding='utf-8') as f:
            f.writelines(cave.export_cave(self.caveinfo))
    
    def save_backup(self):
        self.caveinfo = self.FloorTabs.update_contents()
        this = f"{pathlib.Path(__file__).parent.resolve()}/Backups/Cave/"
        now = str(datetime.datetime.now())
        now = now.replace(":", "_")
        try:
            with open(os.path.join(this, f"{now}.pickle"), "wb+") as f:
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
                    self.FloorTabs.hide()
                    self.FloorTabs = FloorTabHolder(self, self.cave_dir)
                    self.setCentralWidget(self.FloorTabs)
                    self.FloorTabs.show()
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
