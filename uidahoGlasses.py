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
        self.resize(35, 35)
        self.value = -1
        self.x_coord = 0
        self.y_coord = 0
        self.update_display()
        self.setAlignment(QtCore.Qt.AlignCenter)

    def mousePressEvent(self, event):
        selected_color = self.parent().parent().parent().parent().parent().color_selection.currentText()
        if selected_color:  # Check if a color was selected
            self.setStyleSheet("background-color: " + selected_color + ";")  # Set the selected color
        selected_value = self.parent().parent().parent().parent().parent().integer_input.text()  # Get the selected value from the input box
        self.value = selected_value  # Update the value
        self.update_display()


    def update_display(self):
        if int(self.value) > -1:
            self.setText(str(self.value))  # Display the value as a string
        else:
            self.setText("") # Show no address in the cell.


class SquareGridWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)
        size = min(self.width(), self.height())
        self.resize(size, size)
        self.setStyleSheet("background-color: black;")  # Set the background color of the main window
        

    def populate_grid(self, row_count, column_count, cell_size=50, spacing=1):
        for i in range(row_count):
            for j in range(column_count):
                cell_widget = CellWidget(self)
                cell_widget.x_coord = j
                cell_widget.y_coord = i
                self.grid_layout.addWidget(cell_widget, i, j)
        self.grid_layout.setSpacing(1)  # set minimum spacing in pixels
        self.grid_layout.setContentsMargins(1, 1, 1, 1)  # set margins in pixels
        #This fixedsize may not be useful later thanks to the scroll area, I may just force the grid to always have an equal number of rows and columns
        self.setFixedSize(cell_size * column_count + spacing * (column_count - 1), cell_size * row_count + spacing * (row_count - 1))

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.central_widget = QtWidgets.QWidget(self)  # Create a new central widget
        self.setCentralWidget(self.central_widget)

        #Make the central layout. This is how the main elements of the gui will be organized. New elements spawn to the right
        self.central_layout = QtWidgets.QHBoxLayout(self.central_widget)
        
        #Make an area with scroll bars where the grid is capable of being placed.
        self.scroll_area = QtWidgets.QScrollArea(self.central_widget)
        self.square_grid_widget = SquareGridWidget(self.scroll_area)
        self.scroll_area.setWidgetResizable(True)
        #Set the widget that has the scroll area to the class known as square_grid_widget
        self.scroll_area.setWidget(self.square_grid_widget)
        #Add the scroll area widget(which includes the square_grid_widget) into the central layout
        self.central_layout.addWidget(self.scroll_area, 3)

        #Make a new widget that will hold the options for interacting with the grid.
        self.side_widget = QtWidgets.QWidget(self.central_widget)
        #Use Qvboxlayout so each new widget added to the side layout is added horizontally
        self.side_layout = QtWidgets.QVBoxLayout(self.side_widget)
        self.central_layout.addWidget(self.side_widget, 1)  # The side widget will take up 1 part of the window
        # Create an input box for integer input
        self.integer_input = QtWidgets.QLineEdit(self.side_widget)
        #add it to the side layout
        self.side_layout.addWidget(self.integer_input)
        # Create a dropdown menu for color selection
        self.color_selection = QtWidgets.QComboBox(self.side_widget)
        self.color_selection.addItem('#FFFFFF')  # Add white
        self.color_selection.addItem('#FF0000')  # Add red
        self.color_selection.addItem('#00FF00')  # Add green
        self.color_selection.addItem('#0000FF')  # Add blue
        self.side_layout.addWidget(self.color_selection, 1)

        # Create a button to reset everything on the grid
        self.button = QPushButton('reset', self.side_widget)
        self.side_layout.addWidget(self.button, 1)
        self.button.clicked.connect(self.on_reset_clicked)

        self.button = QPushButton('save', self.side_widget)
        self.side_layout.addWidget(self.button, 1)
        self.button.clicked.connect(self.on_save_clicked)


        #populate the square_grid we added earlier. This can be changed later based on how comfy the square sizes are.
        self.square_grid_widget.populate_grid(30, 20)

    def on_reset_clicked(self):
        for i in range(self.square_grid_widget.grid_layout.count()):
            cell_widget = self.square_grid_widget.grid_layout.itemAt(i).widget()
            if isinstance(cell_widget, CellWidget):  # Check if the widget is a CellWidget
                cell_widget.setStyleSheet("background-color: white;")  # Change the cell's color to white
                cell_widget.value = -1
                cell_widget.update_display()

    def on_save_clicked(self):
        save_file = open("idahoGlassesSave.txt", "w")
        for i in range(self.square_grid_widget.grid_layout.count()):
            cell_widget = self.square_grid_widget.grid_layout.itemAt(i).widget()
            if isinstance(cell_widget, CellWidget):  # Check if the widget is a CellWidget
                if int(cell_widget.value) > -1: 
                    save_file.write(str(cell_widget.value))
                    save_file.write(" ")


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    main_win = MainWindow()
    main_win.show()

    app.exec_()
