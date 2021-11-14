import json
import os

from PyQt5.QtWidgets import QDialog, QFileDialog

from gui_preferences import Ui_Dialog
from gui_vanilla_map import Ui_Dialog_2


class VanillaDialog(QDialog, Ui_Dialog_2):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)


class PreferencesDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
        self.init_events()

    def browse(self, text):
        folder = str(QFileDialog.getExistingDirectory(self, "Select a directory"))
        if folder == "":
            print("None selected")
            return
        folder = os.path.abspath(folder)
        text.setText(folder)

    def browse_map(self):
        self.browse(self.lineEdit)

    def browse_save(self):
        self.browse(self.lineEdit_2)

    def save(self):
        config = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        data = {
            "aoc_folder": self.lineEdit.text(),
            "save_folder": self.lineEdit_2.text()
        }
        with open(config, 'w') as file:
            json.dump(data, file)
        self.close()

    def init_events(self):
        self.pushButton.clicked.connect(self.browse_map)
        self.pushButton_2.clicked.connect(self.browse_save)
        self.pushButton_3.clicked.connect(self.save)
        self.pushButton_4.clicked.connect(self.close)