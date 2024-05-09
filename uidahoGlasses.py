#   Jeremy Wisecarver
#   May 8 2024
#   Half-Time tool-kit pattern creator
#   Uses Python3 with PyQt5
#   A GUI to help create the patterns for the idaho band glasses

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import os

#The data that makes up the individual square cells
class CellWidget(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #808080;")  # Set initial color
        self.setStyleSheet("background-color: white;")  # Set the background color to white
        self.resize(35, 35)
        self.value = -1
        self.color = "white"
        self.x_coord = 0
        self.y_coord = 0
        self.r = 255
        self.b = 255
        self.g = 255
        self.update_display()
        self.setAlignment(QtCore.Qt.AlignCenter)

        self.selected = False
        self.count = 0
        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("color: white;") 

    #When the mouse is clicked on the cell widget
    def mousePressEvent(self, event):
        #When a cell is clicked a change has been detected. Used for save checking
        self.parent().parent().parent().parent().parent().changes_made = True
        msg = QMessageBox()
        selected_color_red = self.parent().parent().parent().parent().parent().red_input.text()
        selected_color_green = self.parent().parent().parent().parent().parent().green_input.text()
        selected_color_blue = self.parent().parent().parent().parent().parent().blue_input.text()
        eraser_status = self.parent().parent().parent().parent().parent().eraserToggle
        print(eraser_status)
        # If the eraser is enabled return clicked on square to default
        if eraser_status == True:
            self.color = "white"
            self.value = -1
            self.setStyleSheet("background-color: " + "white" + ";")
            self.update_display()
            self.changes_made = True
            return
        #Check to see what color the cell is being set to
        if selected_color_red.isdigit() and selected_color_green.isdigit() and selected_color_blue.isdigit():
            if (0 > int(selected_color_red) > 255) or ( 0 > int(selected_color_green) > 255) or (0 > int(selected_color_blue) > 255):
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('All color values must be in a range of 0-255.')
                msg.setWindowTitle("Error")
                msg.exec_()
                return
            self.r = selected_color_red
            self.g = selected_color_green
            self.b = selected_color_blue
        else:
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('All color values must be in a range of 0-255.')
            msg.setWindowTitle("Error")
            msg.exec_()
            return
        #Check to see what address number is being used for the cell
        selected_value = self.parent().parent().parent().parent().parent().integer_input.text()  # Get the selected value from the input box
        if selected_value:
            if selected_value.isdigit():
                self.setStyleSheet("background-color:rgb(" + selected_color_red + "," + selected_color_green + "," + selected_color_blue + ")" + ";")  # Set the selected color
                self.value = int(selected_value)  # Update the value
                self.changes_made = True
            else:
                msg.setText("Error")
                msg.setInformativeText('Address must be a digit.')
                msg.setWindowTitle("Error")
                msg.exec_()
                self.r = 255
                self.g = 255
                self.b = 255
                return
            #if the toggle is on that increments the address then increment automatically.
            if self.parent().parent().parent().parent().parent().increment.isChecked() == True:
                self.parent().parent().parent().parent().parent().integer_input.setText(str(self.value+1))
            self.update_display()
        elif selected_value == "":
            #set the address to a value of -2 to denote it is not set
            self.value = -1
            msg.setText("Error")
            msg.setInformativeText('Address must be a digit.')
            msg.setWindowTitle("Error")
            msg.exec_()
            self.update_display()
    def update_display(self):
        # Display the value as a string
        if int(self.value) > -1:
            self.setText(str(self.value)) 
            # Show no address in the cell.
        else:
            self.setText("")

#This class is used to deal with the grid widget in the GUI
class SquareGridWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)
        size = min(self.width(), self.height())
        self.resize(size, size)
        self.setStyleSheet("background-color: black;")  # Set the background color of the main window
        self.square_number = 0
        self.changes_made = parent.parent().parent().changes_made

    #Add all of the cells into the grid
    def populate_grid(self, row_count, column_count, cell_size=80, spacing=1):
        for i in range(row_count):
            for j in range(column_count):
                cell_widget = CellWidget(self)
                cell_widget.x_coord = j
                cell_widget.y_coord = i
                self.grid_layout.addWidget(cell_widget, i, j)
                cell_widget.changes_made = self.changes_made
        self.grid_layout.setSpacing(1)  # set minimum spacing in pixels
        self.grid_layout.setContentsMargins(1, 1, 1, 1)  # set margins in pixels
        #This fixedsize may not be useful later thanks to the scroll area, I may just force the grid to always have an equal number of rows and columns
        self.setFixedSize(cell_size * column_count + spacing * (column_count - 1), cell_size * row_count + spacing * (row_count - 1))

    #added this to increment square_number/counter
    def get_next_square_number(self):
        self.square_number += 1
        return self.square_number
        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.changes_made = False
        self.toggle_increment = False
        self.lastFrame = 0
        self.fileName = "UNK"
        self.fileStr = ""

        self.createMenuBar()

        self.central_widget = QtWidgets.QWidget(self)  # Create a new central widget
        self.setCentralWidget(self.central_widget)

    
        #Make the central layout. This is how the main elements of the gui will be organized. New elements spawn to the right
        self.central_layout = QtWidgets.QHBoxLayout(self.central_widget)
        
        #Make an area with scroll bars where the grid is capable of being placed.
        self.scroll_area = QtWidgets.QScrollArea(self.central_widget)
        self.square_grid_widget = SquareGridWidget(self.scroll_area)
        self.changes_made = self.square_grid_widget.changes_made
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
        # Create a dropdown menu for pattern frame
        self.frame_selection = QtWidgets.QComboBox(self.side_widget)
        self.frame_selection.activated.connect(self.on_frame_clicked)
        self.frame_selection.addItem('Pattern 1')
        self.side_layout.addWidget(self.frame_selection)
        #Create two buttons to easily switch what pattern is being viewed
        self.arrow_widget = QtWidgets.QWidget(self.side_widget)
        self.arrow_layout = QtWidgets.QHBoxLayout(self.arrow_widget)
        self.side_layout.addWidget(self.arrow_widget, 0)
        self.left_button = QPushButton('<<', self.arrow_widget)
        self.right_button = QPushButton('>>', self.arrow_widget)
        self.arrow_layout.addWidget(self.left_button)
        self.arrow_layout.addWidget(self.right_button)
        self.left_button.clicked.connect(lambda: self.left_button_clicked(self.changes_made))
        self.right_button.clicked.connect(lambda: self.right_button_clicked(self.changes_made))
        # Create a button to add a pattern frame
        self.pattern_button = QPushButton('add pattern', self.side_widget)
        self.side_layout.addWidget(self.pattern_button, 1)
        self.pattern_button.clicked.connect(lambda: self.on_pattern_clicked())
        # Create a button to delete a pattern frame
        #self.delete_pattern_button = QPushButton('remove pattern', self.side_widget)
        #self.side_layout.addWidget(self.delete_pattern_button, 1)
        #self.delete_pattern_button.clicked.connect(lambda: self.on_delete_pattern_clicked(self.frame_selection.currentIndex()))
        # Create a button to save a pattern to the current frame
        self.save_pattern_button = QPushButton('save pattern', self.side_widget)
        self.side_layout.addWidget(self.save_pattern_button, 1)
        # Make the save button so that you can overwrite saves
        self.save_pattern_button.clicked.connect(lambda: self.on_pattern_saved(self.frame_selection.currentIndex(), self.changes_made))
        # Create an input box for integer input
        self.integer_input = QtWidgets.QLineEdit(self.side_widget)
        #add it to the side layout
        self.integer_label = QtWidgets.QLabel("Address:")
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.integer_label.setSizePolicy(size_policy)
        self.side_layout.addWidget(self.integer_label, 1)
        self.side_layout.addWidget(self.integer_input, 1)
        # Checkbox with a text label
        self.increment = QCheckBox(text="Auto Increment")
        # Add to the side area
        self.side_layout.addWidget(self.increment)

        self.time_input = QtWidgets.QLineEdit(self.side_widget)
        #add it to the side layout
        self.time_label = QtWidgets.QLabel("Time(milliseconds):")
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.time_label.setSizePolicy(size_policy)
        self.side_layout.addWidget(self.time_label, 1)
        self.side_layout.addWidget(self.time_input, 1)


        self.red_input = QtWidgets.QLineEdit(self.side_widget)
        self.green_input = QtWidgets.QLineEdit(self.side_widget)
        self.blue_input = QtWidgets.QLineEdit(self.side_widget)
        self.red_label = QtWidgets.QLabel("Red:")
        self.green_label = QtWidgets.QLabel("Green:")
        self.blue_label = QtWidgets.QLabel("Blue:")

        self.color_widget = QtWidgets.QWidget(self.side_widget)
        self.color_layout = QtWidgets.QHBoxLayout(self.color_widget)
        self.side_layout.addWidget(self.color_widget)
        self.color_layout.addWidget(self.red_label)
        self.color_layout.addWidget(self.red_input)
        self.color_layout.addStretch()
        self.color_layout.addWidget(self.green_label)
        self.color_layout.addWidget(self.green_input)
        self.color_layout.addStretch()
        self.color_layout.addWidget(self.blue_label)
        self.color_layout.addWidget(self.blue_input)
        self.red_input.setText("0")
        self.green_input.setText("0")
        self.blue_input.setText("0")
        self.red_input.setFixedWidth(40)
        self.green_input.setFixedWidth(40)
        self.blue_input.setFixedWidth(40)

        # Create a button to toggle eraser for grid spaces
        self.eraserToggle = False
        self.eraser_button = QPushButton('eraser', self.side_widget)
        self.eraser_button.setCheckable(True)
        self.side_layout.addWidget(self.eraser_button)
        self.eraser_button.clicked.connect(lambda: self.on_eraser_clicked(self.eraserToggle))
        

        # Create a button to reset everything on the grid
        self.button = QPushButton('reset', self.side_widget)
        self.side_layout.addWidget(self.button)
        self.button.clicked.connect(self.on_reset_clicked)

        #populate the square_grid we added earlier. This can be changed later based on how comfy the square sizes are.
        self.square_grid_widget.populate_grid(30, 30)
        self.side_layout.addStretch()


    def createMenuBar(self):
        menuBar = QMenuBar(self)
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        self.setMenuBar(menuBar)
        self.save_action = QtWidgets.QAction("Save", self)
        self.save_action.triggered.connect(lambda: self.on_save_clicked(self.fileName))  # Connect the action's triggered signal to your save function
        if self.fileName == "UNK":
            self.save_action.setEnabled(False)
        self.open_action = QtWidgets.QAction("Open", self)
        self.open_action.triggered.connect(lambda: self.on_open_clicked())
        self.save_as_action = QtWidgets.QAction("Save as...", self)
        self.save_as_action.triggered.connect(self.save_file_as)  # Connect the action's triggered signal to your save function
        self.convert_save_to_ht13_action = QtWidgets.QAction("Convert to ht13", self)
        self.convert_save_to_ht13_action.triggered.connect(lambda: self.on_convert_clicked())
        fileMenu.addAction(self.open_action)
        fileMenu.addAction(self.save_action)
        fileMenu.addAction(self.save_as_action)
        fileMenu.addAction(self.convert_save_to_ht13_action)

    def on_open_clicked(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*)", options=options)
        print(file_name)
        if file_name:
            with open(file_name, 'r') as file:
                self.fileStr = file.read()
                self.frame_selection.clear()
                temp_file = open('TEMP', 'w')

                for i in range(0, len(self.fileStr)): 
                    temp_file.write(self.fileStr[i])
                #add the correct number of patterns depending on '#' found
                self.frame_selection.addItem('Pattern 1')
                for i in range(0, len(self.fileStr)):
                    if self.fileStr[i] == '#':
                        self.frame_selection.addItem('Pattern ' + str(self.frame_selection.count() + 1))
                self.fileName = file_name
                self.save_action.setEnabled(True)
                self.repopulate_grid(file_name, 0)

    def repopulate_grid(self, file_name, index):
        print("re-Populating using " + file_name + "..\n")
        self.on_reset_clicked()
        cell_widget = self.square_grid_widget.grid_layout.itemAt(1).widget()
        #find the time value
        #for i in range(0,)
        frame_data = self.fileStr.split("#")
        if not frame_data[index].split("||"):
           print("split is invalid")
        grid_data = frame_data[index].split("||")
        for grid_information in grid_data:
            if grid_information == "":
                print("Nothing in file, failed to open.")
                return
            cell_data = grid_information.split("|")
            print(cell_data)
            for i, cell_information in enumerate(cell_data):
                try: cell_information
                except NameError:
                    return
                if cell_information[0] == "#":
                    return
                if cell_information[0] == "":
                    return
                if cell_information[0] == "(":
                    time_value = ""
                    for i in range(1, len(cell_information)):
                        if cell_information[i] != ")":
                            time_value += cell_information[i]
                    print(time_value)
                    self.time_input.setText(time_value)
                    return
                if str(cell_information[0]) == " END":
                    return
                #Using the enumeration we process each piece of
                # data for the cell one at a time:
                #Load the coordinates of the cell here
                if i == 0:
                    #the first bit of information is the coordinates so they are split by comma and then put onto variables
                    coordinates = cell_information.split(",")
                    if coordinates[0] == "END":
                        return
                    if coordinates[0] == "":
                        return
                    if coordinates[0] == "#":
                        return
                    if coordinates[0][0] == "(":
                        return
                    x = int(coordinates[0])
                    y = int(coordinates[1])
                    index = (y*30) + x
                    cell_widget = self.square_grid_widget.grid_layout.itemAt(index).widget()
                #Load the address of the cell here
                elif i == 1:
                    #print(cell_information)
                    cell_widget.value = int(cell_information)
                    #print(cell_information)
                    cell_widget.update_display()
                #Load the color of the cell here
                elif i == 2:
                    print("CELL INFO HERE: ", cell_information)
                    colors = cell_information.split("[")
                    #cell_widget.color = cell_information
                    cell_widget.r = colors[0]
                    cell_widget.g = colors[1]
                    cell_widget.b = colors[2]
                    cell_widget.setStyleSheet("background-color:rgb(" + cell_widget.r + "," + cell_widget.g + "," + cell_widget.b + ");")

    #Standard save file as functionality
    def save_file_as(self):
        print("SAVED AS!")
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()", "", "All Files (*)", options=options)
        if file_name and file_name != "UNK":
            self.fileName = file_name
            self.save_action.setEnabled(True)
            self.on_save_clicked(file_name)
        return file_name
    def save_file(self):
        print("SAVED!")
        
    def on_reset_clicked(self):
        for i in range(self.square_grid_widget.grid_layout.count()):
            cell_widget = self.square_grid_widget.grid_layout.itemAt(i).widget()
            if isinstance(cell_widget, CellWidget):  # Check if the widget is a CellWidget
                cell_widget.setStyleSheet("background-color: white;")  # Change the cell's color to white
                cell_widget.value = -1
                cell_widget.update_display()

    def on_save_clicked(self, fileName):
        with open('TEMP','r') as read_file, open(fileName,'w') as write_file: 
      
            # read content from first file 
            for line in read_file: 
               
                # write content to second file 
                write_file.write(line)

            read_file.close()
            write_file.close()


    # Eraser button is used as a toggle to erase cell spaces
    def on_eraser_clicked(self, eraserToggle):
        if(self.eraser_button.isChecked == True):
            self.eraser_button.isChecked = False
            self.eraserToggle = False
            print("Not Checked") 
            self.eraser_button.setStyleSheet("")    # Entering nothing gives the default colors
        else:
            self.eraserToggle = True
            self.eraser_button.isChecked = True
            print("Checked")
            self.eraser_button.setStyleSheet("background-color : red")  # Turns the button red when it is in use

    #This should load the frame number clicked from TEMP
    def on_frame_clicked(self, index):
        print("Frame index is " + str(index))
        #Check if pattern being clicked exists
        self.frame_selection.count()
        if index < 0:
            print("index too low and does not exist")
            return
        if index >= self.frame_selection.count():
            print("index too high and does not exist")
            return
        print("Last frame is " + str(self.lastFrame))
        print(self.frame_selection.count())
        #index starts at 0, this will adjust for that
        #step 1, seek the part of temp that has the number index
        save_choice = QMessageBox()
        if self.changes_made == True:
            save_choice = QMessageBox()
            ret = save_choice.question(self,'', "Unsaved work detected. Do you wish to save?", save_choice.Yes | save_choice.No)
            if(ret == save_choice.Yes):
                self.on_pattern_saved(self.lastFrame, self.changes_made)
                self.changes_made = False
        with open("TEMP", 'r') as file:
                self.fileStr = file.read()
                #self.save_action.setEnabled(True)
                self.repopulate_grid("TEMP", index)
                self.lastFrame = index

    #Used to get a string that does not include a pattern
    def remove_pattern(self, index):
        temp_list_left = "" 
        temp_list_right = "" 
        final_list = ""
        #Open the temp file and put the current contents into a file string variable
        with open("TEMP", 'r') as file:
                self.fileStr = file.read()
                print(self.fileStr + " " + str(index))
                #Find the information that is going to be removed and save everything else to two variables temp_list_left, and temp_list_right
                number_found = 0
                removal_position = 0
                #These ifs and for are to check what range should be removed from the file
                #Could be done better, a lot of extra logic for edge cases
                if index != 0:
                    for i in range(0, len(self.fileStr)):
                        if self.fileStr[i] == '#':
                            number_found = number_found + 1
                            if index == number_found:
                                removal_position = i
                if index != 0:
                    for i in range(0, removal_position):
                        temp_list_left += self.fileStr[i]
                found_end = False
                for i in range(removal_position, len(self.fileStr)):
                    if self.fileStr[i] == '#' and i != removal_position:
                        found_end = True
                    if found_end == True and i < len(self.fileStr):
                        temp_list_right += self.fileStr[i]
                if len(self.fileStr) > 0:
                    if self.fileStr[0] == '#' and removal_position == 0:
                        temp_list_right += '#'
                final_list = final_list + temp_list_left + temp_list_right
                #Printout for debugging in the console, showing what was removed from the string
                print("BEFORE\n" + self.fileStr + "\nBEFORE")
                print("AFTER\n" + final_list + "\nAFTER")
        #Return the variables that will allow you to add or replace or do something else
        return temp_list_left, temp_list_right, final_list


    #Function to save changes to a pattern
    def on_pattern_saved(self, index, changes_made):
        print("PATTERN SAVE CLICKED")
        self.changes_made = False
        #Check to make sure a time is set before saving the pattern
        input = self.time_input.text()
        if input == "":
            msg = QMessageBox()
            msg.setWindowTitle("ERROR")
            msg.setText("Pattern cannot be saved without a valid time input.")
            msg.exec_()
            return
        #Check to make sure that the time set is a digit
        elif not input.isdigit():
            msg = QMessageBox()
            msg.setWindowTitle("ERROR")
            msg.setText("Pattern cannot be saved with a time input that is not a number.")
            msg.exec_()
            return
        temp_list_left = ""
        temp_list_right = ""
        final_list = ""
        temp_list_left, temp_list_right, final_list = self.remove_pattern(index)
        print("AFTER\n" + final_list + "\nAFTER")
        #step 3: get the new information that is going to be saved to the list unless the pattern is just being removed
        values = []
        cell_widgets = []
        copies_exist = False

        #For all cells in the grid, add all cells to a list
        for i in range(0, self.square_grid_widget.grid_layout.count()):
            cell_widget = self.square_grid_widget.grid_layout.itemAt(i).widget()
            if isinstance(cell_widget, CellWidget):  # Check if the widget is a CellWidget
                values.append(cell_widget.value)
                cell_widgets.append(cell_widget)
        #Check for duplicate addresses used in the for loop
        for i, value in enumerate(values):
            if values.count(value) > 1:
                #When duplicate addresses are found, give the cells a border so the user can see where the copies are
                if int(cell_widgets[i].value) > -1:
                    cell_widgets[i].setStyleSheet("border: 3px solid black; background-color:rgb(" + str(cell_widgets[i].r) + "," + str(cell_widgets[i].g) + "," + str(cell_widgets[i].b) + ");")
                    copies_exist = True
        #If there are copies display the error to the user
        if copies_exist == True:
            msg = QMessageBox()
            msg.setWindowTitle("ERROR")
            msg.setText("Error: Two or more addresses in the grid are the same. The borders of the cells in the grids in question have been highlighted.")
            msg.exec_()
            #Don't save anything to the file if there are any copies
            copies_exist = False
            return
        total = self.frame_selection.count()
        temp_insert = ""
        if index != 0:
            temp_insert = "#"
        #For all cells in the grid, if the cell has value, store the data in a string
        for i in range(self.square_grid_widget.grid_layout.count()):
            cell_widget = self.square_grid_widget.grid_layout.itemAt(i).widget()
            #Check if the widget is a CellWidget
            if isinstance(cell_widget, CellWidget):
                if int(cell_widget.value) != -1: 
                    cell_widget.setStyleSheet("border: 1px white; background-color:rgb(" + cell_widget.r + "," + cell_widget.g + "," + cell_widget.b + ");")
                    temp_insert = temp_insert + str(cell_widget.x_coord) + "," + str(cell_widget.y_coord) + "|" + str(cell_widget.value) + "|" + cell_widget.r + "[" + cell_widget.g + "[" +  cell_widget.b + "||"
        temp_insert = temp_insert + "(" + self.time_input.text() + ")"
        print(temp_insert)
        #Make a new variable and save it to the new string like this new_temp_file = temp_list_left + new_string + temp_list_right
        new_temp_file = temp_list_left + temp_insert + temp_list_right
        #Save this new string to TEMP
        save_file = open("TEMP", "w")
        save_file.write(new_temp_file)
    
    #Look at a lower pattern number pattern
    def left_button_clicked(self, changes_made):
        save_choice = QMessageBox()
        #If changes have been made recently, prompt the user to save their pattern
        if changes_made == True:
            save_choice = QMessageBox()
            ret = save_choice.question(self,'', "Unsaved work detected. Do you wish to save?", save_choice.Yes | save_choice.No)
            if(ret == save_choice.Yes):
                self.on_pattern_saved(self.frame_selection.currentIndex(), changes_made)
                changes_made = False
                self.lastFrame = self.frame_selection.currentIndex()
                return
            else:
                self.changes_made = False
        #Check to see if its actually possible to go to a lower pattern
        if(self.frame_selection.currentIndex()-1 > -1):
            self.on_frame_clicked(self.frame_selection.currentIndex()-1)
            print("valid and can be swapped")
            self.frame_selection.setCurrentIndex(self.frame_selection.currentIndex()-1)
            self.lastFrame = self.frame_selection.currentIndex()
        print("LEFT")

    #Display the next numbered pattern if it exists
    def right_button_clicked(self, changes_made):
        save_choice = QMessageBox()
        if changes_made == True:
            save_choice = QMessageBox()
            ret = save_choice.question(self,'', "Unsaved work detected. Do you wish to save?", save_choice.Yes | save_choice.No)
            if(ret == save_choice.Yes):
                self.on_pattern_saved(self.frame_selection.currentIndex(), changes_made)
                changes_made = False
                return
            else:
                self.changes_made = False
        #Check to see if its actually possible to go to a higher pattern
        if(self.frame_selection.currentIndex()+1 < self.frame_selection.count()):
            self.on_frame_clicked(self.frame_selection.currentIndex()+1)
            print("valid and can be swapped")
            self.frame_selection.setCurrentIndex(self.frame_selection.currentIndex()+1)
            self.lastFrame = self.frame_selection.currentIndex()
        print("RIGHT")

    # Hold all patterns in a temporary file for proper saving and navigation between patterns
    def on_pattern_clicked(self):
        if self.frame_selection.count() == 0:
            save_file = open("TEMP", "w")
        else:
            save_file = open("TEMP", "a+")
        self.frame_selection.addItem('Pattern ' + str(self.frame_selection.count() + 1))
        save_file.write("#")

    def on_delete_pattern_clicked(self, index):
        pattern_to_delete = self.frame_selection.currentIndex()
        #reuse save pattern function 
        self.on_pattern_saved(self.frame_selection.currentIndex(), self.changes_made)
        print("Deleting: " + str(pattern_to_delete) + "\n")
        #Get the strings with the pattern in question removed
        temp_list_left, temp_list_right, final_list = self.remove_pattern(index)
        print(final_list)
        #rewrite the temp file to not have the pattern that has been removed
        save_file = open("TEMP", "w")
        #if the removed pattern is the first one a case must be made to remove the first '#' in final_list
        if pattern_to_delete == 0:
            save_file.write(final_list[1:])
        else:
            save_file.write(final_list)
        #fix the frame_selection_indicies
        self.remove_pattern_index(pattern_to_delete)
        #clear the deleted display from the gui

    def remove_pattern_index(self, index):
        total = self.frame_selection.count()
        self.frame_selection.clear()
        for i in range(total - 1):
            self.frame_selection.addItem("Pattern " + str(i+1))
        self.on_reset_clicked()
        if (total > 1) and (index != 0):
            self.repopulate_grid("TEMP", index-1)
            self.frame_selection.setCurrentIndex(index-1)
            self.lastFrame = self.frame_selection.currentIndex()
        elif (total > 1) and (index == 0):
            self.repopulate_grid("TEMP", 1)
            self.frame_selection.setCurrentIndex(index)
            self.lastFrame = self.frame_selection.currentIndex()
        else:
            self.on_reset_clicked()
            self.frame_selection.addItem("Pattern 1")
            self.frame_selection.setCurrentIndex(index)
            self.lastFrame = self.frame_selection.currentIndex()



    #Take the contents of a saved file and change it to an ht13 file to be read by the ht13 toolkit
    def on_convert_clicked(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*)", options=options)
        initial_file = open(file_name, "r")
        converted_file = open(file_name + ".ht13", "w")
        # Step 1 pull all information needed from the initial file (exclude coordinates)
        initial_text = initial_file.read()
        # Using a boolean to toggle what text is being added or not
        skip_text = True
        post_text = ""
        i = 0
        while i < len(initial_text):
            if skip_text == False:
                post_text += initial_text[i]
            if initial_text[i] == "|":
                if initial_text[i+1] != "|":
                    skip_text = False
            if initial_text[i] == "|" and initial_text[i+1] == "|" and initial_text[i+2] != "(":
                skip_text = True
                i = i+1
            if initial_text[i] == "#":
                skip_text = True
            if initial_text[i] == "#" and initial_text[i+1] == "(":
                skip_text = False
            i = i + 1
        repeat = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Repeating? Y/N')
        bind = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Enter keybind:') 
        print(bind)
        post_text += repeat[0]
        post_text += bind[0]
        print(post_text)
        converted_file.write(post_text)
    

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    main_win = MainWindow()
    main_win.show()
    open("TEMP", 'w').close()


    app.exec_()
