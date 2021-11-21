import json
import math
import sys
import os
import re
import uuid

import oead
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PyQt5.QtGui import QPen, QPixmap, QPainter, QPolygon, QTransform
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

from saveEditor import save

from gui import Ui_MainWindow
from dialogs import VanillaDialog, PreferencesDialog


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")) as file:
            config = json.load(file)
        self.config = config

        self.data = []
        self.index = [-1, -1]

        self.setupUi(self)
        self.init_events()

        self.disable_buttons()

    def paintEvent(self, event):
        if self.index[0] != -1:
            painter = QPainter(self)
            pixmap = QPixmap(os.path.join("assets", self.data[self.index[0]]["pattern"] + ".png"))
            if self.horizontalLayout_4.geometry().width() < self.horizontalLayout_4.geometry().height():
                size = self.horizontalLayout_4.geometry().width()
                difference = self.horizontalLayout_4.geometry().height() - self.horizontalLayout_4.geometry().width()
                left = round(self.horizontalLayout_4.geometry().left())
                top = round(self.horizontalLayout_4.geometry().top() + difference / 2)
            else:
                size = self.horizontalLayout_4.geometry().height()
                difference = self.horizontalLayout_4.geometry().width() - self.horizontalLayout_4.geometry().height()
                left = round(self.horizontalLayout_4.geometry().left() + difference / 2)
                top = round(self.horizontalLayout_4.geometry().top())
            rectange = QRect(QPoint(left, top), QSize(size, size))
            painter.drawPixmap(rectange, pixmap)

            if self.index[1] != -1:
                coordx = ((float(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Translate"][0]) % 1000) / 1000) * size
                coordz = ((float(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Translate"][2]) % 1000) / 1000) * size

                if coordx < 0:
                    coordx = size - coordx
                if coordz < 0:
                    coordz = size - coordz
                location_x = round(left + coordx)
                location_y = round(top + coordz)

                if self.lineEdit_9.isEnabled():
                    if isinstance(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Rotate"], oead.F32):
                        rotation = 180 - math.degrees(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Rotate"])
                    else:
                        rotation = 180 - math.degrees(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Rotate"][1])
                else:
                    rotation = 180

                painter.setPen(QPen(Qt.red, 1))
                painter.setBrush(Qt.red)
                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.setTransform(QTransform().translate(location_x, location_y).rotate(rotation))
                painter.drawPolygon(QPolygon([
                    QPoint(-6, 7),
                    QPoint(0, 4),
                    QPoint(6, 7),
                    QPoint(0, -7)
                ]))

    def disable_buttons(self, editobj=False, editlist=False, rotation=False):
        self.pushButton_5.setEnabled(editobj)
        self.pushButton_6.setEnabled(editobj)
        self.pushButton_7.setEnabled(editlist)
        self.pushButton_8.setEnabled(editobj)
        self.pushButton_9.setEnabled(editobj)
        self.pushButton_10.setEnabled(editlist)

        self.lineEdit.setEnabled(editobj)
        self.lineEdit_2.setEnabled(editobj)
        self.lineEdit_3.setEnabled(editobj)
        self.lineEdit_4.setEnabled(editobj)
        self.lineEdit_5.setEnabled(editobj)
        self.lineEdit_7.setEnabled(editobj)
        self.lineEdit_8.setEnabled(editobj)
        if not rotation:
            self.lineEdit_9.setEnabled(False)

        self.plainTextEdit.setEnabled(editobj)

    def confirm_box(self, msg="Are you sure? You will not be able to undo this action"):
        box = QMessageBox
        answer = box.question(self, 'Confirm', msg, box.Yes | box.No)
        return answer == box.Yes

    def update_object(self):
        self.lineEdit.setText(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["!Parameters"]["DropActor"])
        self.lineEdit_2.setText(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["UnitConfigName"])
        self.lineEdit_3.setText(str(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Translate"][0]))
        self.lineEdit_4.setText(str(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Translate"][1]))
        self.lineEdit_5.setText(str(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Translate"][2]))
        self.lineEdit_7.setText(str(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["HashId"]))
        self.lineEdit_8.setText(str(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["SRTHash"]))
        self.plainTextEdit.setPlainText(oead.byml.to_text(self.data[self.index[0]]["data"]["Objs"][self.index[1]]))
        try:
            if isinstance(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Rotate"], oead.F32):
                self.lineEdit_9.setText(str(round(math.degrees(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Rotate"]), 9)))
            else:
                self.lineEdit_9.setText(str(round(math.degrees(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Rotate"][1]), 9)))
            self.lineEdit_9.setEnabled(True)
        except KeyError:
            self.lineEdit_9.clear()
            self.lineEdit_9.setEnabled(False)

    def update_all(self):
        self.listWidget.clear()
        self.listWidget.addItems([x["name"] for x in self.data])
        self.update_map()

    def update_map(self):
        self.listWidget_2.clear()
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        self.lineEdit_5.clear()
        self.lineEdit_7.clear()
        self.lineEdit_8.clear()
        self.lineEdit_9.clear()
        self.plainTextEdit.clear()
        if self.index[0] != -1:
            for item in self.data[self.index[0]]["data"]["Objs"]:
                if len(re.findall("TBox", item["UnitConfigName"])) == 0:
                    self.listWidget_2.addItem(item["UnitConfigName"])
                    self.listWidget_2.item(self.listWidget_2.count() - 1).setHidden(True)
                else:
                    self.listWidget_2.addItem([
                        item["!Parameters"]["DropActor"],
                        str(item["UnitConfigName"]),
                        str(hex(int(item["HashId"]))),
                        str(item["HashId"]),
                    ][self.comboBox.currentIndex()])
                    try:
                        if not re.search(self.lineEdit_6.text(), self.listWidget_2.item(self.listWidget_2.count() - 1).text()):
                            self.listWidget_2.item(self.listWidget_2.count() - 1).setHidden(True)
                    except re.error:
                        pass
        self.update()

    def apply_filter(self):
        self.update_map()

    def select_object(self):
        self.index[1] = self.listWidget_2.currentRow()
        if self.index[1] != -1 and self.index[0] != -1:
            self.update_object()
            self.disable_buttons(editobj=True, editlist=True, rotation=True)
            self.update()
        elif self.index[0] != -1:
            self.disable_buttons(editlist=True)
        else:
            self.disable_buttons()

    def select_list(self):
        self.index[0] = self.listWidget.currentRow()
        if self.index[0] != -1:
            self.update_map()
            self.disable_buttons(editlist=True)
            self.update()
        else:
            self.disable_buttons()

    def open_custom_clicked(self):
        aoc = str(QFileDialog.getExistingDirectory(self, "Select `aoc` directory"))
        if aoc == "":
            print("None selected")
            return
        aoc = os.path.abspath(aoc)
        complete_path = os.path.join(aoc, "0010", "Map", "MainField")
        if not os.path.isdir(complete_path):
            print("Not valid directory")
            return

        folder_data = []
        subfolder = os.listdir(complete_path)
        for item in subfolder:
            folder_path = os.path.join(complete_path, item)
            pattern = re.findall("^[A-J]-[1-8]$", item)
            if os.path.isdir(folder_path) and len(pattern) == 1:
                subfile = os.listdir(folder_path)
                for file in subfile:
                    file_path = os.path.join(folder_path, file)
                    if os.path.isfile(file_path) and len(
                            re.findall("^" + pattern[0] + "_(Static|Dynamic).smubin$", file)) == 1:
                        with open(file_path, "rb") as f:
                            map_content = f.read()
                        data = oead.byml.from_binary(oead.yaz0.decompress(map_content))
                        folder_data.append({
                            "data": data,
                            "name": file.split(".")[0],
                            "pattern": pattern[0]
                        })
        if len(folder_data) == 0:
            print("No files")
            return

        self.data = folder_data
        self.update_all()

    def import_vanilla(self, filename):
        pattern = filename.split("_")[0]
        smubin_path = os.path.join(self.config["aoc_folder"], "content", "0010", "Map", "MainField", pattern, f"{filename}.smubin")
        if not os.path.isfile(smubin_path):
            print("The file does not exist !")
            return
        with open(smubin_path, "rb") as f:
            vanilla_data = f.read()
        self.data.append({
            "data": oead.byml.from_binary(oead.yaz0.decompress(vanilla_data)),
            "name": filename,
            "pattern": pattern
        })
        self.update_all()

    def select_vanilla(self, vanilla):
        self.import_vanilla(vanilla.listWidget.currentItem().text())
        vanilla.close()

    def open_vanilla_clicked(self):
        vanilla = VanillaDialog(self)
        for letter in [chr(i) for i in range(ord('A'), ord('J')+1)]:
            for i in range(1, 9):
                for y in ["Dynamic", "Static"]:
                    vanilla.listWidget.addItem(f"{letter}-{i}_{y}")
        vanilla.listWidget.clicked.connect(lambda: self.select_vanilla(vanilla))
        vanilla.exec()

    def save_map_clicked(self):
        aoc = str(QFileDialog.getExistingDirectory(self, "Select `aoc` directory"))
        if aoc == "":
            print("None selected")
            return
        aoc = os.path.abspath(aoc)
        complete_path = os.path.join(aoc, "0010", "Map", "MainField")
        if not os.path.isdir(complete_path):
            os.makedirs(complete_path)
        for item in self.data:
            full_path = os.path.join(complete_path, item["pattern"])
            data_converted = oead.yaz0.compress(oead.byml.to_binary(item["data"], big_endian=True))
            if not os.path.isdir(full_path):
                os.makedirs(full_path)
            with open(os.path.join(full_path, f"{item['name']}.smubin"), "bw") as f:
                f.write(data_converted)
        print("saved")

    def settings_clicked(self):
        preferences = PreferencesDialog(self)
        preferences.lineEdit.setText(self.config["aoc_folder"])
        preferences.lineEdit_2.setText(self.config["save_folder"])
        preferences.exec()

    def save_object_clicked(self):
        try:
            valx = oead.F32(float(self.lineEdit_3.text()))
            valy = oead.F32(float(self.lineEdit_4.text()))
            valz = oead.F32(float(self.lineEdit_5.text()))
        except ValueError:
            print("incorrect coordinates !")
            return
        try:
            hashid = oead.U32(int(self.lineEdit_7.text()))
            strhash = oead.S32(int(self.lineEdit_8.text()))
        except ValueError:
            print("incorrect Hash !")
            return

        if not self.lineEdit_2.text().startswith("TBox"):
            if not self.confirm_box("UnitConfigName no longer begins with \"TBox\". It will no longer be seen by the tool. Are you sure you want to continue?"):
                return

        if self.lineEdit_9.text() != "":
            try:
                rotation = oead.F32(math.radians(float(self.lineEdit_9.text())))
                if isinstance(self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Rotate"], oead.F32):
                    self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Rotate"] = rotation
                else:
                    self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Rotate"][1] = rotation
            except ValueError:
                print("incorrect rotation !")

        self.data[self.index[0]]["data"]["Objs"][self.index[1]]["!Parameters"]["DropActor"] = self.lineEdit.text()
        self.data[self.index[0]]["data"]["Objs"][self.index[1]]["UnitConfigName"] = self.lineEdit_2.text()
        self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Translate"][0] = valx
        self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Translate"][1] = valy
        self.data[self.index[0]]["data"]["Objs"][self.index[1]]["Translate"][2] = valz
        self.data[self.index[0]]["data"]["Objs"][self.index[1]]["HashId"] = hashid
        self.data[self.index[0]]["data"]["Objs"][self.index[1]]["SRTHash"] = strhash
        self.update_map()

    def save_yml_clicked(self):
        self.data[self.index[0]]["data"]["Objs"][self.index[1]] = oead.byml.from_text(self.plainTextEdit.toPlainText())
        self.update_map()

    def get_position_clicked(self):
        save_path = os.path.join(self.config["save_folder"], "user")
        users = os.listdir(save_path)
        last_save = ""
        for user in users:
            folder_path = os.path.join(save_path, user)
            if os.path.isdir(folder_path):
                for level in range(10):
                    level = str(level)
                    full_path = os.path.join(folder_path, level)
                    if os.path.isdir(full_path):
                        caption_path = os.path.join(full_path, "caption.jpg")
                        if os.path.isfile(caption_path):
                            edited = float(os.path.getmtime(caption_path))
                            if last_save == "" or edited > float(os.path.getmtime(last_save)):
                                last_save = caption_path
        save_file = os.path.join(os.path.dirname(last_save), "game_data.sav")
        print(save_file)
        if os.path.isfile(save_file):
            converted_sav = save.parseSaveFile(save_file, skip_bools=False)
            grid_x = min(10, max(1, math.trunc((converted_sav["PlayerSavePos"][0] + 4974.629) / 9949.258 * 10 + 1)))
            grid_z = min(8, max(1, math.trunc((converted_sav["PlayerSavePos"][2] + 3974.629) / 7949.258 * 8 + 1)))
            grid_value = f"{chr(64 + grid_x)}-{grid_z}"
            if grid_value == self.data[self.index[0]]["pattern"]:
                self.lineEdit_3.setText(str(converted_sav["PlayerSavePos"][0]))
                self.lineEdit_4.setText(str(converted_sav["PlayerSavePos"][1]))
                self.lineEdit_5.setText(str(converted_sav["PlayerSavePos"][2]))
            else:
                vanilla_save = grid_value + "_" + self.data[self.index[0]]["name"].split("_")[1]
                if self.confirm_box(f"You are not in the same zone as the save file. Import {vanilla_save}?"):
                    self.import_vanilla(vanilla_save)

    def create_object_clicked(self):
        random_hash = uuid.uuid4()
        new_chest = """
            '!Parameters': {{DropActor: Weapon_Sword_001, EnableRevival: false, IsInGround: false, SharpWeaponJudgeType: 0}}
            HashId: !u {}
            Rotate: 0.0
            SRTHash: {}
            Translate: [0.0, 0.0, 0.0]
            UnitConfigName: TBox_Field_Iron
        """.format("0x" + random_hash.hex[2:18], str(random_hash.int)[:10])
        self.data[self.index[0]]["data"]["Objs"].append(oead.byml.from_text(new_chest))
        self.update_map()

    def delete_object_clicked(self):
        if self.confirm_box():
            del self.data[self.index[0]]["data"]["Objs"][self.index[1]]
            self.update_map()

    def delete_map_clicked(self):
        if self.confirm_box():
            del self.data[self.index[0]]
            self.listWidget.setCurrentRow(-1)
            self.update_all()

    def init_events(self):
        self.pushButton.clicked.connect(self.open_custom_clicked)
        self.pushButton_2.clicked.connect(self.open_vanilla_clicked)
        self.pushButton_4.clicked.connect(self.save_map_clicked)
        self.pushButton_3.clicked.connect(self.settings_clicked)
        self.pushButton_5.clicked.connect(self.save_object_clicked)
        self.pushButton_6.clicked.connect(self.get_position_clicked)
        self.pushButton_7.clicked.connect(self.create_object_clicked)
        self.pushButton_8.clicked.connect(self.delete_object_clicked)
        self.pushButton_9.clicked.connect(self.save_yml_clicked)
        self.pushButton_10.clicked.connect(self.delete_map_clicked)
        self.listWidget.currentItemChanged.connect(self.select_list)
        self.listWidget_2.currentItemChanged.connect(self.select_object)
        self.comboBox.currentIndexChanged.connect(self.apply_filter)
        self.lineEdit_6.textChanged.connect(self.apply_filter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
