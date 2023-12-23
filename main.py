import sqlite3
import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QInputDialog, QLineEdit, QWidget
import sys

class BasementUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('пропуска')
        self.setGeometry(800, 300, 300, 300)
        self.name_label = QLabel('Фамилия:')
        self.name_input = QLineEdit()
        self.surname_label = QLabel('Имя:')
        self.surname_input = QLineEdit()
        self.patronymic_label = QLabel('Отчество:')
        self.patronymic_input = QLineEdit()
        self.birthdate_label = QLabel('Дата рождения:')
        self.birthdate_input = QLineEdit()
        self.passnumber_label = QLabel('Номер пропуска:')
        self.passnumber_input = QLineEdit()
        self.check_button = QPushButton('Вход на работу')
        self.check_button.clicked.connect(self.check)
        self.check_button1 = QPushButton('Выход с работы')
        self.check_button1.clicked.connect(self.work)
        self.check_button2 = QPushButton('Выдать таллон')
        self.check_button2.clicked.connect(self.create_temporary_pass)
        self.cancel_pass_button = QPushButton('Отменить пропуск')
        self.cancel_pass_button.clicked.connect(self.cancel_temporary_pass)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.surname_label)
        self.layout.addWidget(self.surname_input)
        self.layout.addWidget(self.patronymic_label)
        self.layout.addWidget(self.patronymic_input)
        self.layout.addWidget(self.birthdate_label)
        self.layout.addWidget(self.birthdate_input)
        self.layout.addWidget(self.passnumber_label)
        self.layout.addWidget(self.passnumber_input)
        self.check_result = QLabel('')
        self.layout.addWidget(self.check_result)
        self.layout.addWidget(self.check_button)
        self.layout.addWidget(self.check_button1)
        self.layout.addWidget(self.check_button2)
        self.layout.addWidget(self.cancel_pass_button)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # Создайте таблицу
        db_connection = sqlite3.connect('baZa.db')
        cursor = db_connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS temporary_passes ("
                       "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "surname TEXT NOT NULL,"
                       "name TEXT NOT NULL,"
                       "patronymic TEXT NOT NULL,"
                       "birthdate TEXT NOT NULL,"
                       "entry_time DATETIME NOT NULL,"
                       "valid_hours INTEGER NOT NULL,"
                       "expiration_time DATETIME NOT NULL)")
        db_connection.close()

    def check(self):
        surname = self.surname_input.text()
        name = self.name_input.text()
        patronymic = self.patronymic_input.text()
        birthdate = self.birthdate_input.text()
        passn = self.passnumber_input.text()
        if surname and name and patronymic and birthdate and passn:
            db_connection = sqlite3.connect('baZa.db')
            cursor = db_connection.cursor()
            cursor.execute(
                "SELECT * FROM baza WHERE surname = ? AND name = ? AND patronymic = ? AND birthdate = ? AND pass_number = ?",
                (surname, name, patronymic, birthdate,passn))
            baza = cursor.fetchone()
            if baza:
                self.check_result.setText('Сотрудник приступил к работе.')
                sec = datetime.datetime.now()
                cursor.execute(
                    "UPDATE baza SET in_work = ? WHERE surname = ? AND name = ? AND patronymic = ? AND birthdate = ? AND pass_number = ?",
                    (sec, surname, name, patronymic, birthdate, passn))
                db_connection.commit()
            else:
                self.check_result.setText('Сотрудник не смог пройти на работу')
            db_connection.close()
        else:
            self.check_result.setText('Заполните все поля')

    def work(self):
        surname = self.surname_input.text()
        name = self.name_input.text()
        patronymic = self.patronymic_input.text()
        birthdate = self.birthdate_input.text()
        passn = self.passnumber_input.text()
        if surname and name and patronymic and birthdate and passn:
            db_connection = sqlite3.connect('baZa.db')
            cursor = db_connection.cursor()
            cursor.execute(
                "SELECT * FROM baza WHERE surname = ? AND name = ? AND patronymic = ? AND birthdate = ? AND pass_number = ?",
                (surname, name, patronymic, birthdate,passn))
            baza = cursor.fetchone()
            if baza:
                self.check_result.setText('Сотрудник ушел с работы.')
                sec = datetime.datetime.now()
                cursor.execute(
                    "UPDATE baza SET out = ? WHERE surname = ? AND name = ? AND patronymic = ? AND birthdate = ? AND pass_number = ?",
                    (sec, surname, name, patronymic, birthdate, passn))
                db_connection.commit()
            else:
                self.check_result.setText('Сотрудник не смог выйти с работы')
            db_connection.close()
        else:
            self.check_result.setText('Заполните все поля')

    def create_temporary_pass(self):
        surname = self.surname_input.text()
        name = self.name_input.text()
        patronymic = self.patronymic_input.text()
        birthdate = self.birthdate_input.text()
        if surname and name and patronymic and birthdate:
            db_connection = sqlite3.connect('baZa.db')
            cursor = db_connection.cursor()
            entry_time = datetime.datetime.now()
            valid_hours, ok = QInputDialog.getInt(self, 'Выдача временного пропуска',
                                                  'Введите количество минут для пропуска:')
            if ok:
                expiration_time = entry_time + datetime.timedelta(minutes=valid_hours)
                cursor.execute("INSERT INTO temporary_passes (surname, name, patronymic, birthdate, entry_time, valid_hours, expiration_time)"
                               "VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (surname, name, patronymic, birthdate, entry_time, valid_hours, expiration_time))
                db_connection.commit()
                self.check_result.setText('Посетителю выдан временной пропуск до ' + str(expiration_time))
            else:
                self.check_result.setText('Отменено')
        else:
            self.check_result.setText('Введите фамилию, имя, отчество и дату рождения посетителя')

    def cancel_temporary_pass(self):
        passn = self.passnumber_input.text()
        if passn:
            db_connection = sqlite3.connect('baZa.db')
            cursor = db_connection.cursor()
            cursor.execute(
                "DELETE FROM temporary_passes WHERE id = ?",
                (passn,))
            db_connection.commit()
            self.check_result.setText('Временный пропуск отменен')
            db_connection.close()
        else:
            self.check_result.setText('Временный пропуск отменен')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    basement_ui = BasementUI()
    basement_ui.show()
    sys.exit(app.exec())