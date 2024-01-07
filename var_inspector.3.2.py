import re
import zipfile
import os
import tempfile
import json
import sys
from PyQt5.QtGui import QColor, QPalette, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QTextEdit, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem, QLineEdit, QSplitter, QHeaderView, QMenu, QLabel
from PyQt5.QtCore import Qt

def create_window():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(0, 0, 0))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(palette)

    main_window = VarFileProcessor()
    main_window.show()

    sys.exit(app.exec_())

class VarFileProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('VAR Inspector')
        self.setGeometry(100, 100, 800, 600)
        self.initUI()
        font = QFont('Roboto', 13)
        log_font = QFont('Roboto', 10)
        self.file_list.setFont(font)
        self.log_area.setFont(log_font)
        self.search_bar.setFont(font)
        self.package_table.setFont(font)        

    def initUI(self):
        central_widget = QWidget(self)
        self.main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        primary_splitter = QSplitter(Qt.Vertical, central_widget)

        top_pane_widget = QWidget()
        top_pane_layout = QHBoxLayout(top_pane_widget)

        button_layout = QVBoxLayout()
        button_font = QFont('Roboto', 10)        

        self.add_button = QPushButton("Add File", central_widget)
        self.add_button.setFont(button_font)
        self.add_button.clicked.connect(self.add_files)
        self.add_button.setObjectName("addButton")
        self.add_button.setStyleSheet("""
            #addButton {
                background-color: #323232;
                color: white;
                border: 1px solid #666666;
                border-radius: 3px;
                padding-top: 3px;
                padding-bottom: 3px;
                padding-left: 15px;
                padding-right: 15px;
            }
            #addButton:hover {
                background-color: #9d37a5;
                border: 1px solid #ef37ef;
            }
        """)        
        button_layout.addWidget(self.add_button)

        self.submit_button = QPushButton("Submit", central_widget)
        self.submit_button.setFont(button_font)
        self.submit_button.clicked.connect(self.submit_files)
        self.submit_button.setObjectName("submitButton")
        self.submit_button.setStyleSheet("""
            #submitButton {
                background-color: #323232;
                color: white;
                border: 1px solid #666666;
                border-radius: 3px;
                padding-top: 3px;
                padding-bottom: 3px;
                padding-left: 15px;
                padding-right: 15px;
            }
            #submitButton:hover {
                background-color: #403de2;
                border: 1px solid #3a7cf4;
            }
        """)         
        button_layout.addWidget(self.submit_button)

        self.reset_button = QPushButton("Reset", central_widget)
        self.reset_button.setFont(button_font)
        self.reset_button.clicked.connect(self.reset_ui)
        self.reset_button.setObjectName("resetButton")
        self.reset_button.setStyleSheet("""
            #resetButton {
                background-color: #000000;
                color: white;
                border: 1px solid #323232;
                border-radius: 3px;
                padding-top: 3px;
                padding-bottom: 3px;
                padding-left: 15px;
                padding-right: 15px;
            }
            #resetButton:hover {
                background-color: #222222;
                border: 1px solid #ffffff;
            }
        """)         
        button_layout.addWidget(self.reset_button)

        top_pane_layout.addLayout(button_layout)

        self.file_list = QListWidget(central_widget)
        top_pane_layout.addWidget(self.file_list)

        primary_splitter.addWidget(top_pane_widget)

        self.splitter = QSplitter(Qt.Vertical, central_widget)

        self.log_area = QTextEdit(central_widget)
        self.log_area.setReadOnly(True)
        self.splitter.addWidget(self.log_area)

        package_details_widget = QWidget()
        package_details_layout = QVBoxLayout(package_details_widget)

        self.search_bar = QLineEdit(package_details_widget)
        self.search_bar.setPlaceholderText("Search packages...")
        package_details_layout.addWidget(self.search_bar)

        self.package_table = QTableWidget(central_widget)
        self.package_table.setColumnCount(3)
        self.package_table.setHorizontalHeaderLabels(["Package Name", "Filename", "Location"])
        self.package_table.setSortingEnabled(True)
        
        self.package_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.package_table.customContextMenuRequested.connect(self.table_context_menu)

        header = self.package_table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        package_details_layout.addWidget(self.package_table)

        self.splitter.addWidget(package_details_widget)

        primary_splitter.addWidget(self.splitter)

        self.main_layout.addWidget(primary_splitter)

        primary_splitter.setSizes([100, 900])
        self.splitter.setSizes([100, 900])
        
        self.version_label = QLabel("v1.3.2 © 2024 AshAuryn", central_widget)
        self.version_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.main_layout.addWidget(self.version_label)        

        self.connect_search()
   
    def table_context_menu(self, position):
        menu = QMenu()
        copy_action = menu.addAction("Copy")
        action = menu.exec_(self.package_table.viewport().mapToGlobal(position))
        
        if action == copy_action:
            self.copy_selection_to_clipboard()
            
    def clear_table(self):
        self.package_table.setRowCount(0)            
            
    def connect_search(self):
        self.search_bar.textChanged.connect(self.filter_table)

    def filter_table(self):
        search_text = self.search_bar.text().lower()
        for row in range(self.package_table.rowCount()):
            item = self.package_table.item(row, 0)
            self.package_table.setRowHidden(row, search_text not in item.text().lower())
        
    def copy_selection_to_clipboard(self):
        selection = self.package_table.selectedIndexes()
        if selection:
            data_to_copy = "\n".join([self.package_table.model().data(index) for index in selection])
            QApplication.clipboard().setText(data_to_copy)           

    def reset_ui(self):
        self.log_area.clear()

        self.file_list.clear()
        self.clear_table()

    def add_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select VAR files", "", "VAR files (*.var)")
        for file_path in file_paths:
            self.file_list.addItem(file_path)

    def submit_files(self):
        selected_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        if not selected_files:
            QMessageBox.information(self, "No Files", "No files selected for processing.")
            return

        package_names_info = set()
        key_names_set = set()
        self.process_var_files(selected_files, package_names_info, key_names_set)
        package_names_list = list(package_names_info)
        self.log_area.append(f"Processed packages: {package_names_list}\n")

    def process_json_file(self, file_path, package_names_info, key_names_set, filename):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            regex_pattern = re.compile(r'([a-zA-Z0-9_ ]+)\.([a-zA-Z0-9_ ]+)\.(latest|\d+)')
            filename = os.path.basename(file_path)
            self.extract_package_names(data, regex_pattern, package_names_info, key_names_set, key_path=[], filename=filename)
        except Exception as e:
            self.log_area.append(f"Error processing JSON file {file_path}: {e}\n")

    def extract_zip_to_temp(self, zip_path):
        try:
            temp_dir = tempfile.TemporaryDirectory()
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir.name)
            return temp_dir
        except zipfile.BadZipFile:
            self.log_area.append(f"Error: Bad var file {zip_path}\n")
            return None
        except Exception as e:
            self.log_area.append(f"Error extracting var file {zip_path}: {e}\n")
            return None

    def process_files_in_directory(self, directory, package_names_info, key_names_set):
        self.log_area.append(f"Processing files in directory: {directory}\n")
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.json', '.vap')) and file != 'meta.json':
                    file_path = os.path.join(root, file)
                    filename = os.path.basename(file_path)
                    self.process_json_file(file_path, package_names_info, key_names_set, filename)


    def process_var_files(self, file_paths, package_names_info, key_names_set):
        for file_path in file_paths:
            self.log_area.append(f"Processing .var file: {file_path}\n")
            if file_path.endswith('.var'):
                temp_dir = self.extract_zip_to_temp(file_path)
                if temp_dir:
                    self.process_files_in_directory(temp_dir.name, package_names_info, key_names_set)
                    temp_dir.cleanup()
                 
    def extract_package_names(self, data, regex_pattern, package_names_info, key_names_set, key_path, filename):
        color_package_name = "green"
        color_filename = "pink"
        color_key_path = "purple"
        if isinstance(data, dict):
            for key, value in data.items():
                new_key_path = key_path + [key]
                if isinstance(value, (dict, list)):
                    self.extract_package_names(value, regex_pattern, package_names_info, key_names_set, new_key_path, filename)
                elif isinstance(value, str) and "This scene requires the use of VaM client version" not in value:
                    match = regex_pattern.match(value)
                    if match:
                        package_name = f"{match.group(1)}.{match.group(2)}"
                        if package_name not in package_names_info:
                            if key not in key_names_set:
                                key_names_set.add(key)
                            key_path_str = " -> ".join(new_key_path)
                            log_message = (f"Found package name: <span style='color:{color_package_name}'>{package_name}</span> "
                                        f"in <span style='color:{color_filename}'>{filename}</span> "
                                        f"at location <span style='color:{color_key_path}'>{key_path_str}</span>\n")
                            self.log_area.append(log_message)
                            package_names_info.add(package_name)
                            self.add_package_to_table(package_name, filename, key_path_str)
        elif isinstance(data, list):
            for item in data:
                self.extract_package_names(item, regex_pattern, package_names_info, key_names_set, key_path, filename)
                
    def add_package_to_table(self, package_name, filename, location):
        row_position = self.package_table.rowCount()
        self.package_table.insertRow(row_position)

        self.package_table.setItem(row_position, 0, QTableWidgetItem(package_name))
        self.package_table.setItem(row_position, 1, QTableWidgetItem(filename))
        self.package_table.setItem(row_position, 2, QTableWidgetItem(location))

if __name__ == '__main__':
    create_window()
