import pickle
from PyQt5 import QtGui, QtWidgets, uic
from enum import IntEnum
from PyQt5.QtCore import Qt, QObject, pyqtSlot, QEvent
from PyQt5.QtGui import QPixmap, QCloseEvent, QKeyEvent, QIntValidator
from PyQt5.QtWidgets import QFileDialog


class Gender(IntEnum):
    MAN = 0
    WOMAN = 1


class Race(IntEnum):
    ELF = 0
    FAIRY = 1
    ORK = 2
    HUMAN = 3


class Class(IntEnum):
    ЦЕЛИТЕЛЬ = 0
    ГУБИТЕЛЬ = 1
    ЗАЩИТНИК = 2
    БАНДИТ = 3
    ВОРЮГА = 4
    БАРБИ = 5


class Unit():
    def __init__(self, name, race, gender, str, dex, int, lck, uclass):
        self.name = name
        self.race = race
        self.gender = gender
        self.uclass = uclass
        self.str = str
        self.dex = dex
        self.int = int
        self.lck = lck
        self.hp = 0
        self.mp = 0
        self.attack = 0
        self.defence = 0
        self.avatarImagePath = ''

        self.calculateOutputParameters()

    def calculateOutputParameters(self):
        self.hp = 5 * self.str + 4 * self.dex - .2 * self.int + 3 * self.lck
        self.mp = 6 * self.int + self.dex + self.lck
        self.attack = 5 * self.str + 3 * self.dex + 2 * self.lck
        self.defence = 5 * self.dex + 3 * self.lck + self.str

        if self.uclass == Class.ЦЕЛИТЕЛЬ:
            self.mp = self.mp * 1.3
            self.attack = self.attack * .5
        elif self.uclass == Class.ГУБИТЕЛЬ:
            self.attack = self.attack * 2
            self.defence = self.defence * .7
        elif self.uclass == Class.ЗАЩИТНИК:
            self.mp = 0
            self.defence = self.defence * 2.2
            self.attack = self.attack * .85
        elif self.uclass == Class.БАНДИТ:
            self.hp = self.hp * .8
            self.attack = self.attack * 1.2
            self.defence = self.defence * .3
        elif self.uclass == Class.ВОРЮГА:
            pass
        elif self.uclass == Class.БАРБИ:
            self.hp = self.hp * .1
            self.mp = self.mp * .1
            self.attack = self.attack * .1
            self.defence = self.defence * .1

        if self.gender == Gender.MAN:
            if self.race == Race.HUMAN:
                self.imagePath = './images/male_hum.jpg'
            elif self.race == Race.ELF:
                self.imagePath = './images/elf_man.jpg'
            elif self.race == Race.FAIRY:
                self.imagePath = './images/fairy_man.jpg'
            elif self.race == Race.ORK:
                self.imagePath = './images/male_ork.jpg'
        elif self.gender == Gender.WOMAN:
            if self.race == Race.HUMAN:
                self.imagePath = './images/fem_hum.png'
            elif self.race == Race.ELF:
                self.imagePath = './images/elf_woman.jpg'
            elif self.race == Race.FAIRY:
                self.imagePath = './images/fairy_woman.jpg'
            elif self.race == Race.ORK:
                self.imagePath = './images/fem_ork.jpg'

    def to_dict(self):
        return {
            'name': self.name,
            'race': self.race,
            'gender': self.gender,
            'uclass': self.uclass,
            'str': self.str,
            'dex': self.dex,
            'int': self.int,
            'lck': self.lck
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['name'],
            data['race'],
            data['gender'],
            data['str'],
            data['dex'],
            data['int'],
            data['lck'],
            data['uclass']
        )


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        uic.loadUi('./forms/form.ui', self)

        self.__currentRace = Race.HUMAN
        self.__currentGender = Gender.MAN
        self.__currentClass = Class.ЦЕЛИТЕЛЬ
        self.comboBox_Race.setCurrentIndex(3)
        self.__savePath = ''
        self.__savePathBIN = ''

        self.showPerson()

        self.pushButton_SaveAsToTXT.setEnabled(False)
        self.pushButton_SaveAsToBIN.setEnabled(False)
        self.pushButton_SaveToTXT.setEnabled(False)
        self.pushButton_SaveToBIN.setEnabled(False)

        self.u = None

        validator = QtGui.QIntValidator(self)
        validator.setBottom(0)
        validator.setTop(1)
        self.lineEdit_Strength.setValidator(validator)
        self.lineEdit_Agility.setValidator(validator)
        self.lineEdit_Intelligence.setValidator(validator)
        self.lineEdit_Luck.setValidator(validator)
        self.pushButton_M.setEnabled(False)

        self.lineEdit_Strength.setText('0')
        self.lineEdit_Agility.setText('0')
        self.lineEdit_Intelligence.setText('0')
        self.lineEdit_Luck.setText('0')

        self.lineEdit_Strength.textChanged.connect(self.updatePoints)
        self.lineEdit_Agility.textChanged.connect(self.updatePoints)
        self.lineEdit_Intelligence.textChanged.connect(self.updatePoints)
        self.lineEdit_Luck.textChanged.connect(self.updatePoints)

        self.pushButton_M.clicked.connect(self.mGenderChanged)
        self.pushButton_F.clicked.connect(self.fGenderChanged)

        self.comboBox_Race.currentIndexChanged.connect(self.raceChanged)
        self.comboBox_ClassValue.currentIndexChanged.connect(self.classChanged)
        self.pushButton_Create.clicked.connect(self.createUnit)
        self.pushButton_Clear.clicked.connect(self.clearUnit)

        # self.pushButton_SaveToTXT.clicked.connect(self.saveToTXT)
        # self.pushButton_LoadFromTXT.clicked.connect(self.loadFromTXT)
        self.pushButton_SaveAsToTXT.clicked.connect(self.onSaveAsToTXT)
        self.pushButton_LoadFromTXT.clicked.connect(self.onLoadFromTXT)
        self.pushButton_SaveAsToBIN.clicked.connect(self.onSaveAsToBIN)
        self.pushButton_LoadFromBIN.clicked.connect(self.onLoadFromBIN)
        self.pushButton_SaveToTXT.clicked.connect(self.saveToTXT)
        self.pushButton_SaveToBIN.clicked.connect(self.saveToBIN)

        self.updatePoints()

    def setEnability(self, state):
        self.lineEdit_Name.setEnabled(state)
        self.lineEdit_Strength.setEnabled(state)
        self.lineEdit_Agility.setEnabled(state)
        self.lineEdit_Intelligence.setEnabled(state)
        self.lineEdit_Luck.setEnabled(state)
        self.comboBox_Race.setEnabled(state)
        self.comboBox_ClassValue.setEnabled(state)

        self.pushButton_Create.setEnabled(state)
        self.pushButton_M.setEnabled(state)
        self.pushButton_F.setEnabled(state)

        self.pushButton_SaveAsToTXT.setEnabled(state)
        self.pushButton_LoadFromTXT.setEnabled(state)
        self.pushButton_SaveAsToBIN.setEnabled(state)
        self.pushButton_LoadFromBIN.setEnabled(state)
        self.pushButton_SaveToTXT.setEnabled(state)
        self.pushButton_SaveToBIN.setEnabled(state)

    @pyqtSlot()
    def onSaveAsToTXT(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setDefaultSuffix('txt')
        file_path, _ = file_dialog.getSaveFileName(self, "Сохранить персонажа", "",
                                                   "Текстовые файлы (*.txt);;Все файлы (*)")

        if file_path:
            self.__savePath = file_path
            self.saveToTXT()

    @pyqtSlot()
    def onLoadFromTXT(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_path, _ = file_dialog.getOpenFileName(self, "Загрузить персонажа", "",
                                                   "Текстовые файлы (*.txt);;Все файлы (*)")

        if file_path:
            self.__savePath = file_path
            self.loadFromTXT()

    def saveToTXT(self):
        if self.__savePath == '':
            self.onSaveAsToTXT()
        else:
            if self.u is not None:
                try:
                    with open(self.__savePath, 'w', encoding='utf-8') as file:
                        data = self.u.to_dict()
                        for key, value in data.items():
                            file.write(f"{key}: {value}\n")

                    QtWidgets.QMessageBox.information(self, "Успешно!", f"Персонаж сохранен в файл: {self.__savePath}",
                                                  QtWidgets.QMessageBox.Ok)

                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Ошибка!", f"Возникла ошибка при сохранении: {str(e)}",
                                               QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.critical(self, "Ошибка!", "Персонажа не существует!", QtWidgets.QMessageBox.Ok)

    @pyqtSlot()
    def onLoadFromTXT(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_path, _ = file_dialog.getOpenFileName(self, "Загрузить персонажа", "",
                                                   "Текстовые файлы (*.txt);;Все файлы (*)")

        if file_path:
            self.__savePath = file_path
            self.loadFromTXT()

    def loadFromTXT(self):
        try:
            with open(self.__savePath, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            data = {}
            for line in lines:
                key, value = map(str.strip, line.split(':'))
                data[key] = value

            u = Unit(
                data['name'],
                Race(int(data['race'])),
                Gender(int(data['gender'])),
                int(data['str']),
                int(data['dex']),
                int(data['int']),
                int(data['lck']),
                Class(int(data['uclass']))
            )

            self.u = u
            self.lineEdit_Name.setText(u.name)
            self.lineEdit_Strength.setText(str(u.str))
            self.lineEdit_Agility.setText(str(u.dex))
            self.lineEdit_Intelligence.setText(str(u.int))
            self.lineEdit_Luck.setText(str(u.lck))
            self.label_HealthValue.setText(str(round(u.hp)))
            self.label_ManaValue.setText(str(round(u.mp)))
            self.label_AttackValue.setText(str(round(u.attack)))
            self.label_DefenceValue.setText(str(round(u.defence)))
            self.updatePoints()

            self.__currentRace = u.race
            self.__currentGender = u.gender
            self.__currentClass = u.uclass

            self.showPerson()

            QtWidgets.QMessageBox.information(self, "Успешно!", f"Персонаж загружен из файла: {self.__savePath}",
                                              QtWidgets.QMessageBox.Ok)

            self.setEnability(False)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка!", f"Возникла ошибка при загрузке: {str(e)}",
                                           QtWidgets.QMessageBox.Ok)

    @pyqtSlot()
    def onSaveAsToBIN(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_path, _ = file_dialog.getSaveFileName(self, "Сохранить персонажа", "", "BIN-файлы (*.bin);;Все файлы (*)")

        if file_path:
            self.__savePathBIN = file_path
            self.saveToBIN()

    @pyqtSlot()
    def onLoadFromBIN(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_path, _ = file_dialog.getOpenFileName(self, "Загрузить персонажа", "", "BIN-файлы (*.bin);;Все файлы (*)")

        if file_path:
            self.__savePathBIN = file_path
            self.loadFromBIN()

    def saveToBIN(self):
        if self.__savePathBIN == '':
            self.onSaveAsToBIN()
        else:
            if self.u is not None:
                try:
                    with open(self.__savePathBIN, 'wb') as file:
                        pickle.dump(self.u.to_dict(), file)

                    QtWidgets.QMessageBox.information(self, "Успешно!", f"Персонаж сохранен в файл: {self.__savePathBIN}",
                                                      QtWidgets.QMessageBox.Ok)

                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Ошибка!", f"Возникла ошибка при сохранении: {str(e)}",
                                                   QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.critical(self, "Ошибка!", "Персонажа не существует!", QtWidgets.QMessageBox.Ok)

    @pyqtSlot()
    def loadFromBIN(self):
        try:
            with open(self.__savePathBIN, 'rb') as file:
                data = pickle.load(file)
            u = Unit(
                data['name'],
                Race(int(data['race'])),
                Gender(int(data['gender'])),
                int(data['str']),
                int(data['dex']),
                int(data['int']),
                int(data['lck']),
                Class(int(data['uclass'])),
            )

            self.u = u
            self.lineEdit_Name.setText(u.name)
            self.lineEdit_Strength.setText(str(u.str))
            self.lineEdit_Agility.setText(str(u.dex))
            self.lineEdit_Intelligence.setText(str(u.int))
            self.lineEdit_Luck.setText(str(u.lck))
            self.label_HealthValue.setText(str(round(u.hp)))
            self.label_ManaValue.setText(str(round(u.mp)))
            self.label_AttackValue.setText(str(round(u.attack)))
            self.label_DefenceValue.setText(str(round(u.defence)))
            self.updatePoints()
            #
            self.__currentRace = u.race
            self.__currentGender = u.gender
            self.__currentClass = u.uclass
            #
            self.showPerson()

            QtWidgets.QMessageBox.information(self, "Успешно!", f"Персонаж загружен из файла: {self.__savePathBIN}",
                                              QtWidgets.QMessageBox.Ok)

            self.setEnability(False)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка!", f"Возникла ошибка при загрузке: {str(e)}",
                                           QtWidgets.QMessageBox.Ok)
            print(e)

    @pyqtSlot()
    def clearUnit(self):
        self.comboBox_Race.setCurrentIndex(0)

        self.lineEdit_Name.clear()
        self.lineEdit_Strength.setText('0')
        self.lineEdit_Agility.setText('0')
        self.lineEdit_Intelligence.setText('0')
        self.lineEdit_Luck.setText('0')
        self.label_HealthValue.setText('0')
        self.label_ManaValue.setText('0')
        self.label_DefenceValue.setText('0')
        self.label_AttackValue.setText('0')
        self.__currentRace = Race.HUMAN
        self.__currentGender = Gender.MAN
        self.__currentClass = Class.ЦЕЛИТЕЛЬ
        self.showPerson()

        self.setEnability(True)
        self.pushButton_SaveAsToTXT.setEnabled(False)
        self.pushButton_SaveAsToBIN.setEnabled(False)
        self.pushButton_SaveToTXT.setEnabled(False)
        self.pushButton_SaveToBIN.setEnabled(False)
        self.pushButton_M.setEnabled(False)
        self.pushButton_Create.setEnabled(False)
        self.u = None

    @pyqtSlot()
    def updatePoints(self):
        if self.lineEdit_Strength.text() == '':
            strength = 1
        else:
            strength = int(self.lineEdit_Strength.text())
        if self.lineEdit_Agility.text() == '':
            agility = 1
        else:
            agility = int(self.lineEdit_Agility.text())
        if self.lineEdit_Intelligence.text() == '':
            intelligence = 1
        else:
            intelligence = int(self.lineEdit_Intelligence.text())
        if self.lineEdit_Luck.text() == '':
            luck = 1
        else:
            luck = int(self.lineEdit_Luck.text())

        remaining_points = 20 - strength - agility - intelligence - luck
        self.label_Points.setText(f'Осталось очков: {str(remaining_points)}')

        if remaining_points >= 0:
            self.pushButton_Create.setEnabled(True)
            self.label_Points.setStyleSheet('color: green')
        else:
            self.pushButton_Create.setEnabled(False)
            self.label_Points.setStyleSheet('color: red')

    @pyqtSlot()
    def createUnit(self):
        if self.lineEdit_Name.text() == '' or self.lineEdit_Strength.text() == '' or self.lineEdit_Agility.text() == '' or self.lineEdit_Intelligence.text() == '' or self.lineEdit_Luck.text() == '':
            QtWidgets.QMessageBox.critical(self, "Ошибка!", "Введите данные!", QtWidgets.QMessageBox.Ok)
        else:
            name = self.lineEdit_Name.text()
            stre = int(self.lineEdit_Strength.text())
            dex = int(self.lineEdit_Agility.text())
            itl = int(self.lineEdit_Intelligence.text())
            lck = int(self.lineEdit_Luck.text())

            # u = Unit(name, self.__currentRace, self.__currentGender, stre, dex, itl, lck, self.__currentClass)
            self.u = Unit(name, self.__currentRace, self.__currentGender, stre, dex, itl, lck, self.__currentClass)

            # результат

            self.label_HealthValue.setText(str(round(self.u.hp)))
            self.label_ManaValue.setText(str(round(self.u.mp)))
            self.label_DefenceValue.setText(str(round(self.u.defence)))
            self.label_AttackValue.setText(str(round(self.u.attack)))

            self.setEnability(False)
            self.pushButton_SaveAsToTXT.setEnabled(True)
            self.pushButton_SaveAsToBIN.setEnabled(True)
            self.pushButton_SaveToTXT.setEnabled(True)
            self.pushButton_SaveToBIN.setEnabled(True)

    def closeEvent(self, e: QCloseEvent):
        if self.u is not None:
            answer = QtWidgets.QMessageBox.question(self, "Сохранить героя?",
                                                    "Хотите ли вы сохранить героя перед закрытием программы?",
                                                    QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel,
                                                    QtWidgets.QMessageBox.Cancel)
            if answer == QtWidgets.QMessageBox.Save:
                self.saveToTXT()
                self.saveToBIN()
                e.accept()
                QtWidgets.QWidget.closeEvent(self, e)
            elif answer == QtWidgets.QMessageBox.Discard:
                e.accept()
                QtWidgets.QWidget.closeEvent(self, e)
            else:
                e.ignore()
        else:
            answer = QtWidgets.QMessageBox.question(self, "Выход из программы",
                                                    "Вы уверены, что хотите прекратить создание персонажа?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                    QtWidgets.QMessageBox.No)
            if answer == QtWidgets.QMessageBox.Yes:
                e.accept()
                QtWidgets.QWidget.closeEvent(self, e)
            else:
                e.ignore()

    # Слот изменения расы
    @pyqtSlot()
    def raceChanged(self):
        self.__currentRace = Race(self.comboBox_Race.currentIndex())
        self.showPerson()

        pass

    @pyqtSlot()
    def classChanged(self):
        if self.comboBox_ClassValue.currentIndex() == 0:
            self.__currentClass = Class.ЦЕЛИТЕЛЬ
        elif self.comboBox_ClassValue.currentIndex() == 1:
            self.__currentClass = Class.ГУБИТЕЛЬ
        elif self.comboBox_ClassValue.currentIndex() == 2:
            self.__currentClass = Class.ЗАЩИТНИК
        elif self.comboBox_ClassValue.currentIndex() == 3:
            self.__currentClass = Class.БАНДИТ
        elif self.comboBox_ClassValue.currentIndex() == 4:
            self.__currentClass = Class.ВОРЮГА
        elif self.comboBox_ClassValue.currentIndex() == 5:
            self.__currentClass = Class.БАРБИ

    @pyqtSlot()
    def mGenderChanged(self):
        self.__currentGender = Gender.MAN
        self.pushButton_M.setEnabled(False)
        self.pushButton_F.setEnabled(True)
        self.showPerson()

    @pyqtSlot()
    def fGenderChanged(self):
        self.__currentGender = Gender.WOMAN
        self.pushButton_M.setEnabled(True)
        self.pushButton_F.setEnabled(False)
        self.showPerson()

    # Функция отображения персонажа
    def showPerson(self):
        pix = QPixmap()
        if self.__currentGender == Gender.MAN:
            if self.__currentRace == Race.HUMAN:  # 3
                pix.load('./images/male_hum.jpg')
                self.comboBox_Race.setCurrentIndex(3)
            elif self.__currentRace == Race.ELF:  # 0
                pix.load('./images/elf_man.jpg')
                self.comboBox_Race.setCurrentIndex(0)
            elif self.__currentRace == Race.FAIRY:  # 1
                pix.load('./images/fairy_man.jpg')
                self.comboBox_Race.setCurrentIndex(1)
            elif self.__currentRace == Race.ORK:  # 2
                pix.load('./images/male_ork.jpg')
                self.comboBox_Race.setCurrentIndex(2)
        elif self.__currentGender == Gender.WOMAN:
            if self.__currentRace == Race.HUMAN:
                pix.load('./images/fem_hum.png')
                self.comboBox_Race.setCurrentIndex(3)
            elif self.__currentRace == Race.ELF:
                pix.load('./images/elf_woman.jpg')
                self.comboBox_Race.setCurrentIndex(0)
            elif self.__currentRace == Race.FAIRY:
                pix.load('./images/fairy_woman.jpg')
                self.comboBox_Race.setCurrentIndex(1)
            elif self.__currentRace == Race.ORK:
                pix.load('./images/fem_ork.jpg')
                self.comboBox_Race.setCurrentIndex(2)
        self.label_Image.setPixmap(pix)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
