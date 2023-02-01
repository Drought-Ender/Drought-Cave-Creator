import copy
import pickle
import datetime
import UnitsLibrary.units as units
import os
import pathlib
import settings
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QMessageBox, QVBoxLayout,
    QGridLayout, QScrollArea, QComboBox,
    QHBoxLayout, QFileDialog, QWidget, QPushButton,
    QSpinBox, QCompleter, QDialog, QMenu)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QContextMenuEvent, QCursor
from PyQt6.QtCore import Qt, QSortFilterProxyModel
from extra_widgets import betterSpinBox, betterSpinBoxFloat, AddSubButtons, lineEditLable



class Keys:
    def __init__(self):
        self.teki_keys = []
        self.all_teki = []
        self.all_item = []
        self.unit_dict = {}
        self.settings = settings.settings
    
    def init_items(self):
        self.settings = copy.deepcopy(settings.settings)
        with open(f"./presets/{self.settings.preset}/all_units.txt", "rb") as f:
            self.unit_dict = {unit.name : unit for unit in units.read_unitstxt(f.readlines()).units}

        self.teki_keys = [teki for teki in self.settings.teki_dict if  self.settings.show_useless_teki or  self.settings.teki_dict[teki]["use"]]
        if  self.settings.use_internal_names:
            self.all_teki = [(QIcon(f"presets/{self.settings.preset}/tekiIcons/{teki}.png"), teki) for teki in  self.settings.teki_dict if  self.settings.show_useless_teki or  self.settings.teki_dict[teki]["use"]]
            self.all_item = [(QIcon(f"presets/{self.settings.preset}/itemIcons/{item}.png"), item) for item in  self.settings.item_dict]
        else:
            self.all_teki = [(QIcon(f"presets/{self.settings.preset}/tekiIcons/{teki}.png"),  self.settings.teki_dict[teki]["common"]) for teki in  self.settings.teki_dict if  self.settings.show_useless_teki or  self.settings.teki_dict[teki]["use"]]
            self.all_item = [(QIcon(f"presets/{self.settings.preset}/itemIcons/{item}.png"),  self.settings.item_dict[item]) for item in  self.settings.item_dict]
            

keys = Keys()

class DefaultInfoMenu(QComboBox):
    def __init__(self, parent, items, index):
        super(DefaultInfoMenu, self).__init__(parent)
        self.items = items
        self.addItems(items)
        self.setCurrentIndex(index)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)
        # connect signals
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    # on selection of an item from the completer, select the corresponding item from combobox
    def on_completer_activated(self, text):
        if text in self.items:
            index = self.findText(text)
            self.setCurrentIndex(index)

    # on model change, update the models of the filter and completer as well
    def setModel(self, model):
        super(DefaultInfoMenu, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)


    # on model column change, update the model column of the filter and completer as well
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(DefaultInfoMenu, self).setModelColumn(column)    

class PointEdit(QWidget):
    def __init__(self, parent, name, point:units.Size2i):
        super(QWidget, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.name = QLabel(f"{name} (")
        self.x_box = QSpinBox()
        self.x_box.setValue(point.x)
        self.point1 = QLabel(", ")
        self.y_box = QSpinBox()
        self.y_box.setValue(point.y)
        self.point2 = QLabel(")")
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.x_box)
        self.layout.addWidget(self.point1)
        self.layout.addWidget(self.y_box)
        self.layout.addWidget(self.point2)
        self.setLayout(self.layout)
    
    def get_point(self):
        return units.Size2i(self.x_box.value(), self.y_box.value())

class LinkWidget(QWidget):
    def __init__(self, parent, link:units.DoorLink):
        super(QWidget, self).__init__(parent)
        self.link = link
        self.layout = QHBoxLayout()
        self.dist = betterSpinBoxFloat(self, "Distance: ", 0, 99999, link.dist)
        self.id = betterSpinBox(self, "Door-Id: ", 0, 99, link.id)
        self.tekiflag = betterSpinBox(self, "Teki Flag: ", 0, 99, link.flag)
        self.layout.addWidget(self.dist)
        self.layout.addWidget(self.id)
        self.layout.addWidget(self.tekiflag)
        self.setLayout(self.layout)

class DoorWidget(QScrollArea):
    def __init__(self, parent, door:units.Door):
        super(QWidget, self).__init__(parent)
        self.door = door
        self.this_widget = QWidget()
        self.layout = QVBoxLayout(self.this_widget)
        self.subname = QLabel("Links:")
        self.index = betterSpinBox(self, "Door Index:", 0, 99, door.index)
        self.dir = QComboBox()
        self.dir.addItems(["North", "East", "South", "West"])
        self.dir.setCurrentIndex(door.position.dir)
        self.offs = betterSpinBox(self, "Offset Right", 0, 99, door.position.offs)
        self.wpindex = betterSpinBox(self, "Waypoint Index", 0, 999, door.position.index)
        self.links = []
        self.layout.addWidget(self.index)
        self.layout.addWidget(self.dir)
        self.layout.addWidget(self.offs)
        self.layout.addWidget(self.wpindex)
        self.layout.addWidget(self.subname)
        for link in door.links:
            self.links.append(LinkWidget(self, link))
            self.layout.addWidget(self.links[-1])
        self.buttons = AddSubButtons(self)
        self.buttons.check_disable(len(self.links))
        self.layout.addWidget(self.buttons)
        self.setWidget(self.this_widget)
        self.setWidgetResizable(True)
    
    def add_obj(self):
        new_link = units.DoorLink(0, 0, 0)
        self.links.append(LinkWidget(self, new_link))
        self.layout.insertWidget(len(self.links) + 4, self.links[-1])
        self.buttons.check_disable(len(self.links))
    
    def sub_obj(self):
        remove = self.links.pop()
        self.layout.removeWidget(remove)
        remove.deleteLater()
        self.buttons.check_disable(len(self.links))
    
    def get_links(self):
        return [
            units.DoorLink(
                link.dist.slide.value(), link.id.slide.value(), link.tekiflag.slide.value()
            ) for link in self.links
        ]


class DoorEditBox(QScrollArea):
    def __init__(self, parent, doors):
        super(QWidget, self).__init__(parent)
        self.this_widget = QWidget()
        self.name = QLabel("Doors:")
        self.layout = QVBoxLayout(self.this_widget)
        self.layout.addWidget(self.name)
        self.doors = []
        for door in doors:
            self.doors.append(DoorWidget(self, door))
            self.layout.addWidget(self.doors[-1])

        self.buttons = AddSubButtons(self)
        self.buttons.check_disable(len(self.doors))
        self.layout.addWidget(self.buttons)
        self.setWidget(self.this_widget)
        self.setWidgetResizable(True)

    def add_obj(self):
        newdoor = units.Door(0, units.DoorPos(0, 0, 0), [])
        self.doors.append(DoorWidget(self, newdoor))
        self.layout.insertWidget(len(self.doors), self.doors[-1])
        self.buttons.check_disable(len(self.doors))
    
    def sub_obj(self):
        remove = self.doors.pop()
        self.layout.removeWidget(remove)
        remove.deleteLater()
        self.buttons.check_disable(len(self.doors))

    def get(self):
        return [units.Door(
            door.index.slide.value(), units.DoorPos
            (
                door.dir.currentIndex(), door.offs.slide.value(), door.wpindex.slide.value()
            ), door.get_links()
            ) for door in list[DoorWidget](self.doors)
        ]

class UnitEdit(QDialog):
    def __init__(self, parent, unit:units.CaveUnit):
        super().__init__(parent)
        self.setWindowTitle("Units File Unit Editor")
        self.layout = QGridLayout()
        self.parent = parent
        self.unit = unit
        self.ver = betterSpinBox(self, "Version:", 0, 1, unit.ver)
        self.name = lineEditLable(self, "Unit File Name:", unit.name)
        self.unit_size = PointEdit(self, "Size:", unit.size)
        self.room_type = QComboBox()
        self.room_type.addItems(["Alcove", "Room", "Hall"])
        self.room_type.setCurrentIndex(unit.type)
        self.flag1 = betterSpinBox(self, "Flag 1:", 0, 99, unit.flags[0])
        self.flag2 = betterSpinBox(self, "Flag 2:", 0, 99, unit.flags[1])
        self.doors = DoorEditBox(self, unit.doors)
        self.save_button = QPushButton("Save", self)
        self.save_button.pressed.connect(self.save)
        self.layout.addWidget(self.ver, 0, 0)
        self.layout.addWidget(self.name, 1, 0)
        self.layout.addWidget(self.unit_size, 2, 0)
        self.layout.addWidget(self.room_type, 3, 0)
        self.layout.addWidget(self.flag1, 4, 0)
        self.layout.addWidget(self.flag2, 5, 0)
        self.layout.addWidget(self.save_button, 6, 0)
        self.layout.addWidget(self.doors, 0, 1, 7, 1)
        self.setLayout(self.layout)
    
    def save(self):
        unit_ver = self.ver.slide.value()
        unit_name = self.name.text.text()
        unit_size = units.Size2i(self.unit_size.x_box.value(), self.unit_size.y_box.value())
        unit_type = self.room_type.currentIndex()
        unit_flags = [self.flag1.slide.value(), self.flag2.slide.value()]
        unit_doors = self.doors.get()
        self.parent.update_unit(units.CaveUnit(unit_ver, unit_name, unit_size, unit_type, unit_flags, unit_doors))

class UnitImage(QWidget):
    def __init__(self, parent, unit:units.CaveUnit, uwindow):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.parent = parent
        self.uwindow = uwindow
        self.unit = unit
        self.name = unit.name
        self.pix = f"./presets/{keys.settings.preset}/units/{self.name}"
        self.label = QPushButton(self.name, self)
        self.img = QLabel()
        self.label.setFixedSize(self.label.sizeHint())
        self.img.setPixmap(QPixmap(self.pix).scaled(100, 100))
        self.layout.addWidget(self.img)
        self.layout.addWidget(self.label)
        self.label.pressed.connect(self.open_unit_editor)
        self.setLayout(self.layout)
        self.setFixedSize(150, 150)
    
    def open_unit_editor(self):
        unit_editor = UnitEdit(self, self.unit)
        unit_editor.show()
    
    def update_unit(self, unit):
        self.unit = unit
        self.name = unit.name
        self.label.setText(self.name)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        self.menu = QMenu(self)
        delete = QAction("Delete", self)
        delete.triggered.connect(self.removeThisWidget)

        #insert = QAction("Insert", self)
        #insert.triggered.connect(self.addWidgetHere)
        self.menu.addAction(delete)
        #self.menu.addAction(insert)
        self.menu.popup(QCursor().pos())


    def removeThisWidget(self):
        self.uwindow.sub_obj_at(self)

    def addWidgetHere(self):
        self.uwindow.add_obj_at(self)

class UnitsWindow(QScrollArea):
    def __init__(self, parent, units_:units.UnitsFile):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.units = units_
        self.this_widget = QWidget()
        self.list = []
        self.gridLayout = QGridLayout(self.this_widget)
        for i, unit in enumerate(units_.units):
            new = UnitImage(self, unit, self)
            self.list.append(new)
            self.gridLayout.addWidget(new, i // 5, i % 5)
        self.setWidget(self.this_widget)
        self.setWidgetResizable(True)
        
    def get_units(self):
        return [copy.deepcopy(keys.unit_dict[unitwidget.name]) for unitwidget in self.this_widget.children() if isinstance(unitwidget, UnitImage)]



    def sub_obj_at(self, widget):
        self.parent.sub_obj_at(widget)

    def add_obj_at(self, widget):
        self.parent.add_obj_at(widget)
    


class WindowHolder(QWidget):
    def __init__(self, parent, units_):
        super(QWidget, self).__init__(parent)
        self.boxLayout:QVBoxLayout = QVBoxLayout()
        self.Uwindow = UnitsWindow(self, units_)
        self.boxLayout.addWidget(self.Uwindow)
        self.buttons = AddSubButtonsUnits(self, self.Uwindow)
        self.boxLayout.addWidget(self.buttons)
        self.setLayout(self.boxLayout)

    def add_obj(self):
        unit = self.buttons.get_unit()
        i = 0
        while i < 100:
            nextSpot = self.Uwindow.gridLayout.itemAtPosition(i // 5, i % 5)
            if nextSpot is None:
                break
            i += 1
        self.Uwindow.list.append(unit)
        
        self.Uwindow.gridLayout.addWidget(unit, i // 5, i % 5)
        self.buttons.check_disable(len(self.Uwindow.list))
    
    def sub_obj(self):
        remove = self.Uwindow.list.pop()
        self.Uwindow.gridLayout.removeWidget(remove)
        remove.deleteLater()
        self.buttons.check_disable(len(self.Uwindow.list))

    
    def sub_obj_at(self, widget):
        widgetIdx:int = self.Uwindow.gridLayout.indexOf(widget)
        remove = self.Uwindow.list.pop(widgetIdx)
        self.Uwindow.gridLayout.removeWidget(remove)
        remove.deleteLater()
        self.buttons.check_disable(len(self.Uwindow.list))
        
    def get_units(self):
        return units.UnitsFile(self.Uwindow.get_units())

class AddSubButtonsUnits(QWidget):
    def __init__(self, parent, uwindow):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.uwindow = uwindow
        self.layout = QHBoxLayout()
        self.add_item = QPushButton("+")
        self.sub_item = QPushButton("-")
        self.select_item = DefaultInfoMenu(self, keys.unit_dict.keys(), 0)
        self.add_item.clicked.connect(parent.add_obj)
        self.sub_item.clicked.connect(parent.sub_obj)
        self.layout.addWidget(self.select_item)
        self.layout.addWidget(self.add_item)
        self.layout.addWidget(self.sub_item)
        self.setLayout(self.layout)
        self.unit_name = "cap_conc"
    
    def check_disable(self, num):
        if num == 0:
            self.sub_item.blockSignals(True)
        else:
            self.sub_item.blockSignals(False)
    
    def get_unit(self):
        if len(keys.unit_dict.keys()) <= self.select_item.currentIndex():
            return
        self.unit_name = tuple(keys.unit_dict.keys())[self.select_item.currentIndex()]
        return UnitImage(self, keys.unit_dict[self.unit_name], self.uwindow)

    def add_obj_at(self, widget):
        pass

    def sub_obj_at(self, widget):
        self.parent.sub_obj_at(widget)


class UnitsTab(QMainWindow):
    def __init__(self, units_:units.UnitsFile, units_dir):
        super().__init__()
        keys.init_items()
        self.units = units_
        self.units_dir = units_dir

        openFile = QAction(QIcon('open.png'), '&Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new Light')
        openFile.triggered.connect(self.open_new_units)
        saveFile = QAction(QIcon('save.png'), '&Save', self)
        saveFile.setShortcut('Ctrl+S')
        saveFile.setStatusTip('Save Light to file')
        saveFile.triggered.connect(self.save_units)
        saveAsFile = QAction(QIcon('save.png'), 'Save &As', self)
        saveAsFile.setShortcut('Ctrl+Shift+S')
        saveAsFile.setStatusTip('Save Light to new file')
        saveAsFile.triggered.connect(self.save_as_units)
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

        self.units_window = WindowHolder(self, self.units)
        self.setGeometry(50, 50, 1400, 1000)
        self.setWindowTitle('Units Editor')
        self.setCentralWidget(self.units_window)
        self.show()

    def open_new_units(self):
        units_file = QFileDialog.getOpenFileName(self, "Open Units File", keys.settings.units_path)
        if units_file[0]:
            with open(units_file[0], 'rb') as f:
                try:
                    data = f.readlines()
                    self.units = units.read_unitstxt(data)
                    self.units_dir = units_file[0]
                    self.units_window = WindowHolder(self, self.units)
                    self.setCentralWidget(self.units_window)
                except Exception as e:
                    QMessageBox.critical(self, "Error reading units", str(e))
    
    def save_units(self):
        self.units = self.units_window.get_units()
        units_file = self.units_dir
        if not os.path.exists(self.units_dir):
            units_file = QFileDialog.getSaveFileName(self, "Save units as", keys.settings.units_path)[0]
            if not units_file.endswith(".txt"):
                units_file += ".txt"
        with open(units_file, 'w', encoding='utf-8') as f:
            f.writelines(units.export_file(self.units))

    def save_as_units(self):
        self.units = self.units_window.get_units()
        units_file = QFileDialog.getSaveFileName(self, "Save Units as", keys.settings.units_path)[0]
        if not units_file.endswith(".txt"):
            units_file += ".txt"
        with open(units_file, 'w', encoding='utf-8') as f:
            f.writelines(units.export_file(self.units))
            self.units_dir = units_file
    
    def save_backup(self):
        self.units = self.units_window.get_units()
        this = f"{pathlib.Path(__file__).parent.resolve()}/Backups/Units/"
        try:
            with open(os.path.join(this, f"{datetime.datetime.now()}.pickle"), "wb+") as f:
                pickle.dump(self.units, f)
        except FileNotFoundError:
            QMessageBox.critical(self, "Error saving backup", "Unable to save backup; backups folder is missing")

    
    def load_backup(self):
        this = f"{pathlib.Path(__file__).parent.resolve()}/Backups/Units/"
        pickel_file = QFileDialog.getOpenFileName(self, "Open pickel data file", this, "Drought-Cave Pickle Data files (*.pickle)")
        if pickel_file[0]:
            with open(pickel_file[0], 'rb') as f:
                try:
                    self.units = pickle.load(f)
                    self.units_window = UnitsWindow(self, self.units)
                    self.setCentralWidget(self.units_window)
                except:
                    QMessageBox.critical(self, "Error reading units", f"Backup is corrupt")