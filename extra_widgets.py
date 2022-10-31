from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, QVBoxLayout, 
    QPushButton, QFileDialog)
from PyQt6.QtGui import QColor, QPixmap, QPainter, QBrush

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

class betterSpinBox(QWidget):
    def __init__(self, parent, text, mini, maxi, val):
        super(QWidget, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.parent = parent
        self.lab = QLabel(text, self)
        self.slide = QSpinBox(self)
        self.slide.setMinimum(mini)
        self.slide.setMaximum(maxi)
        self.slide.setValue(val)
        self.layout.addWidget(self.lab, 0)
        self.layout.addWidget(self.slide, 0)
        self.setLayout(self.layout)
        self.val = val
        self.slide.valueChanged.connect(self.on_change_value)

    def on_change_value(self, val):
        self.val = int(val)


class betterSpinBoxFloat(QWidget):
    def __init__(self, parent, text, mini, maxi, val):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout()
        self.lab = QLabel(text, self)
        self.slide = QDoubleSpinBox(self)
        self.slide.setMinimum(mini)
        self.slide.setMaximum(maxi)
        self.slide.setValue(val)
        self.layout.addWidget(self.lab, 0)
        self.layout.addWidget(self.slide, 0)
        self.setLayout(self.layout)
        self.val = val
        self.slide.valueChanged.connect(self.on_change_value)

    def on_change_value(self, val):
        self.val = float(val)

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

class ColorBox(QWidget):
    def __init__(self, parent, color:QColor):
        super(QWidget, self).__init__(parent)
        self.color = color
        self.layout = QHBoxLayout()
        # convert image file into pixmap
        self.pixmap_image = QPixmap("./Assets/AlphaGrad.png")

        self.label = QLabel()

        # create painter instance with pixmap
        self.painterInstance = QPainter(self.pixmap_image)

        # set rectangle color and thickness
        self.brush = QBrush(self.color)

        # draw rectangle on painter
        self.painterInstance.setBrush(self.brush)
        self.painterInstance.drawRect(0,0,100,100)
        # set pixmap onto the label widget
        self.painterInstance.end()
        self.label.setPixmap(self.pixmap_image)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        #self.painter = QPainter(self)
        #self.painter.setBrush(QBrush(self.color))
        #self.painter.drawRect(0, 0, 100, 100)
    
    def update_color(self, color:QColor):
        self.color = color
        self.pixmap_image = QPixmap("./Assets/AlphaGrad.png")
        self.painterInstance = QPainter(self.pixmap_image)

        # set rectangle color and thickness
        self.brush = QBrush(self.color)
        # draw rectangle on painter
        self.painterInstance.setBrush(self.brush)
        self.painterInstance.drawRect(0, 0, 100,100)
        # set pixmap onto the label widget
        self.painterInstance.end()
        self.label.setPixmap(self.pixmap_image)
        #self.painter.setBrush(QBrush(self.color))
        #self.painter.drawRect(0, 0, 100, 100)