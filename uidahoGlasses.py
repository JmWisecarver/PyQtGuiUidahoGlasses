from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

class CellWidget(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #808080;")  # Set initial color
        self.setStyleSheet("background-color: white;")  # Set the background color to white
        self.resize(40, 40)

    def mousePressEvent(self, event):
        selected_color = self.parent().parent().parent().parent().parent().color_selection.currentText()
        if selected_color:  # Check if a color was selected
            self.setStyleSheet("background-color: " + selected_color + ";")  # Set the selected color

class SquareGridWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)
        size = min(self.width(), self.height())
        self.resize(size, size)
        self.setStyleSheet("background-color: black;")  # Set the background color of the main window
        

    #def resizeEvent(self, event):
        #size = min(self.width(), self.height())
        #self.resize(size, size)

    def populate_grid(self, row_count, column_count, cell_size=50, spacing=1):
        for i in range(row_count):
            for j in range(column_count):
                cell_widget = CellWidget(self)
                self.grid_layout.addWidget(cell_widget, i, j)
        self.grid_layout.setSpacing(1)  # set minimum spacing in pixels
        self.grid_layout.setContentsMargins(1, 1, 1, 1)  # set margins in pixels
        total_size = cell_size * row_count + spacing * (row_count - 1)
        self.setFixedSize(cell_size * column_count + spacing * (column_count - 1), cell_size * row_count + spacing * (row_count - 1))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.central_widget = QtWidgets.QWidget(self)  # Create a new central widget
        self.setCentralWidget(self.central_widget)

        self.central_layout = QtWidgets.QHBoxLayout(self.central_widget)
        

        
        self.scroll_area = QtWidgets.QScrollArea(self.central_widget)
        self.square_grid_widget = SquareGridWidget(self.scroll_area)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.square_grid_widget)
        self.central_layout.addWidget(self.scroll_area, 3)

        # Create a dropdown menu for color selection
        self.color_selection = QtWidgets.QComboBox(self.central_widget)
        self.color_selection.addItem('#FFFFFF')  # Add white
        self.color_selection.addItem('#FF0000')  # Add red
        self.color_selection.addItem('#00FF00')  # Add green
        self.color_selection.addItem('#0000FF')  # Add blue
        self.central_layout.addWidget(self.color_selection, 1)

        # Create an input box for integer input
        self.integer_input = QtWidgets.QLineEdit(self.central_widget)
        self.central_layout.addWidget(self.integer_input)

        self.square_grid_widget.populate_grid(30, 30)

    

        
        #self.resize(1000, 1000)  # Set the initial size of the window


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    main_win = MainWindow()
    main_win.show()

    app.exec_()
