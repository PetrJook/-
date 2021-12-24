import psycopg2
import sys
from config import host, user, password, db_name

from PyQt5.QtWidgets import (QApplication, QWidget,
                             QTabWidget, QAbstractScrollArea,
                             QVBoxLayout, QHBoxLayout,
                             QTableWidget, QGroupBox,
                         QTableWidgetItem, QPushButton, QMessageBox, QDialog)



conn = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)

conn.set_session(autocommit=True)

cursor = conn.cursor()

base_date = '06-12-21'  # this has to be any past monday of the upper week
DAYS = ["понедельник", "вторник", "среда", "четверг", "пятница"]

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Schedule")

        self.vbox = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tabs.addTab(Tab(1, 'Schedule', 'timetable', 5,
                             ['timetable_id', 'day', 'fk_subject_id', 'room_numb', 'start_time']), 'Текущая неделя')
        self.tabs.addTab(Tab(2, 'Schedule', 'timetable', 5,
                             ['timetable_id', 'day', 'fk_subject_id', 'room_numb', 'start_time']), 'Следующая неделя')
        self.tabs.addTab(Tab(0, 'Subjects', 'subject', 3,
                             ['subject_id', 'name', 'fk_teacher_id']), 'Subject')
        self.tabs.addTab(Tab(0, 'Teachers', 'teacher', 2,
                             ['teacher_id', 'full_name']), 'Teacher')
        self.vbox.addWidget(self.tabs)

        self.setLayout(self.vbox)


class Tab(QWidget):
    def __init__(self, timetable, name, table_name, column_count, labels):
        super().__init__()
        self.timetable = timetable
        self.name = name
        self.table_name = table_name
        self.column_count = column_count
        self.labels = labels
        self.labels.extend(['', ''])
        self.table_gbox = QGroupBox("")
        self.svbox = QVBoxLayout()
        self.shbox1 = QHBoxLayout()
        self.shbox2 = QHBoxLayout()
        self.shbox3 = QHBoxLayout()
        self.svbox.addLayout(self.shbox1)
        self.svbox.addLayout(self.shbox2)
        self.svbox.addLayout(self.shbox3)


        if self.timetable in [1, 2]:
            self._create_timetable()
        else:
            self.shbox1.addWidget(self.table_gbox)
            self._create_table()

        self.update_schedule_button = QPushButton("Update")
        self.update_schedule_button.clicked.connect(lambda: self._update_table())
        self.insert_value_button = QPushButton("Insert")
        self.insert_value_button.clicked.connect(lambda: self._insert_value())
        self.shbox2.addWidget(self.insert_value_button)
        self.shbox3.addWidget(self.update_schedule_button)

        self.setLayout(self.svbox)


    def _create_table(self):
        self.table = QTableWidget()
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.table.setColumnCount(self.column_count + 2)    # кол-во столбцов на 2 больше, чем полей в таблице, место для кнопок
        self.table.setHorizontalHeaderLabels(self.labels)

        self._update_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.table)
        self.table_gbox.setLayout(self.mvbox)


    def _create_timetable(self):
        self.tables = [Table(i, self.timetable) for i in range(1, 5 + 1)]

        for i, table in enumerate(self.tables):
            self._add_layout(i, table)

    def _add_layout(self, i, table):
        vbox = QVBoxLayout()
        vbox.addWidget(table)
        gbox = QGroupBox(DAYS[i].upper())
        gbox.setLayout(vbox)
        shbox = QHBoxLayout()
        shbox.addWidget(gbox)
        self.svbox.addLayout(shbox)

    def _update_table(self):
        if self.timetable in [1,2]:
            for table in self.tables:
                table.update_table()
        else:
            cursor.execute(f"SELECT * FROM {self.table_name}")
            records = cursor.fetchall()
            self.table.setRowCount(len(records))

            for i, r in enumerate(records):
                self._add_value(i, r)

            self.table.resizeRowsToContents()


    def _insert_value(self):
        labels = self.labels[1:-2]
        text_labels = ', '.join(labels).rstrip(',')

        try:
            cursor.execute("""
            SELECT MAX(timetable_id) FROM timetable
            """)
            new_id = list(cursor.fetchall()[0])
            new_id[0] = str(new_id[0] + 1)
            print(new_id)
            row = input(f'Введите следующие данные через запятую:\n {text_labels}, верхняя/нижняя неделя\n').split(',')
            new_row = new_id + [value.replace(' ', '') for value in row]
            print(new_row)
            if new_row[-1].lower() == 'верхняя':
                try:
                    day = DAYS.index(new_row[1].lower()) + 1
                    new_row[1] = str(day)
                except:
                    QMessageBox.about(self, "Error", f"field 'day' filled improperly")
                    return
            elif new_row[-1].lower() == 'нижняя':
                try:
                    day = DAYS.index(new_row[1].lower()) + 1
                    new_row[1] = str(day + 7)
                except:
                    QMessageBox.about(self, "Error", f"field 'day' filled improperly")
                    return
            else:
                QMessageBox.about(self, "Error", f"field 'верхняя/нижняя неделя' filled improperly")
                return
            new_row[3] = '\'' + new_row[3] + '\''
            new_row[4] = '\'' + new_row[4] + '\''
            # поля room_numb и start_time должны выглядеть как строки
            new_values = ''
            for i in range(len(labels) + 1):
                new_values += new_row[i] + ','
            new_values = new_values.rstrip(',')
            print(f'INSERT INTO {self.table_name} VALUES ({new_values})')
            cursor.execute(f"""
                   INSERT INTO {self.table_name} VALUES ({new_values})
                   """)
        except:
            QMessageBox.about(self, "Error", f"Enter all fields, strings have to be inside single quotes")

    def _add_value(self, i, r):
        for j, field in enumerate(r):
            self.table.setItem(i, j, QTableWidgetItem(str(field)))
        changeButton = QPushButton("Изменить")
        deleteButton = QPushButton("Удалить")
        self.table.setCellWidget(i, j + 1, changeButton)
        self.table.setCellWidget(i, j + 2, deleteButton)

        changeButton.clicked.connect(lambda: self._change_row(r[0]))
        deleteButton.clicked.connect(lambda: self._delete_row(r[0], i))

    def _change_row(self, id):
        """
        В поле day таблицы timetable хранятся числа от 1 до 12.
        Каждое число обозначает номер дня недели в двухнедельном цикле.
        1 - Понедельник верхней недели
        2 - Вторник верхней недели
        8 - Понедельник нижней недели
        9 - Вторник нижней недели

        """
        labels = self.labels[1:-2]    # убираем пустые поля и поле id
        text_labels = ', '.join(labels).rstrip(',')
        try:
            row = input(f'Введите следующие данные через запятую:\n {text_labels}, верхняя/нижняя неделя\n').split(',')
            new_row = [value.replace(' ', '') for value in row]
            if new_row[-1].lower() == 'верхняя':
                try:
                    day = DAYS.index(new_row[0].lower()) + 1
                    new_row[0] = str(day)
                except:
                    QMessageBox.about(self, "Error", f"field 'day' filled improperly")
                    return
            elif new_row[-1].lower() == 'нижняя':
                try:
                    day = DAYS.index(new_row[0].lower()) + 1
                    new_row[0] = str(day + 7)
                except:
                    QMessageBox.about(self, "Error", f"field 'day' filled improperly")
                    return
            else:
                QMessageBox.about(self, "Error", f"field 'верхняя/нижняя неделя' filled improperly")
                return
            new_row[2] = '\'' + new_row[2] + '\''
            new_row[3] = '\'' + new_row[3] + '\''
            # поля room_numb и start_time должны выглядеть как строки
            new_values = ''
            for i, label in enumerate(labels):
                new_values += label + '=' + new_row[i] + ','
            new_values = new_values.rstrip(',')
            print(f'UPDATE {self.table_name} SET {new_values} WHERE {self.table_name}_id = {id}')
            cursor.execute(f"""
            UPDATE {self.table_name} SET {new_values} WHERE {self.table_name}_id = {id}
            """)
        except:
            QMessageBox.about(self, "Error", f"Enter all fields, strings have to be inside single quotes")


    def _delete_row(self, id, row):
        print(f"DELETE FROM {self.table_name} WHERE {self.table_name}_id = {str(id)}")
        try:
            cursor.execute(f"""
            DELETE FROM {self.table_name} WHERE {self.table_name}_id = {str(id)}
            """)
        except:
            QMessageBox.about(self, "Error", "Wrong ID!")
        self.table.removeRow(row + 1)
    def _add_line(self, id):
        new_line = input(f'Введите следующие значения через запятую:\n{self.labels[:-2]}\n')
        print(f'INSERT INTO {self.table_name} VALUES ({new_line}) ')

        try:
            cursor.execute(f"""
            INSERT INTO {self.table_name} VALUES ({new_line})
            """)
        except:
            QMessageBox.about(self, "Error", f"Enter all fields, {self.table_name}_id is a PRIMARY KEY, strings have to be inside single quotes")

        self.table.removeCellWidget(id, 0)


class Table(QTableWidget):
    def __init__(self, day, week):
        QTableWidget.__init__(self)
        self.table_name = 'timetable'
        self.week = week
        self.day = day
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.setColumnCount(5)  # кол-во столбцов на 2 больше, чем полей в таблице, место для кнопок
        self.setHorizontalHeaderLabels([ 'name', 'room_numb', 'start_time', '', ''])

        self.update_table()


    def update_table(self):
        if self.week == 1:
            c = '<'
        elif self.week == 2:
            c = '>'
        cursor.execute(f'''
                SELECT timetable_id, day, name, room_numb, start_time 
                FROM {self.table_name}
                INNER JOIN subject on subject.subject_id = {self.table_name}.fk_subject_id
                WHERE 
                    CASE WHEN (current_date - date '{base_date}') % 14 {c} 7
                        THEN day < 7
                        ELSE day > 7
                    END
                ORDER BY day ASC, start_time ASC 
                ''')
        data = cursor.fetchall()
        records = [r for r in data if r[1] % 7 == self.day]
        self.setRowCount(len(records))

        for i, r in enumerate(records):
            self._add_value(i, r)

        self.resizeRowsToContents()

    def _add_value(self, i, r):
        id = r[0]
        r = r[2:]
        for j, field in enumerate(r):
            self.setItem(i, j, QTableWidgetItem(str(field)))
        changeButton = QPushButton("Изменить")
        deleteButton = QPushButton("Удалить")
        self.setCellWidget(i, j + 1, changeButton)
        self.setCellWidget(i, j + 2, deleteButton)

        changeButton.clicked.connect(lambda: self._change_row(id))
        deleteButton.clicked.connect(lambda: self._delete_row(id, i))

    def _change_row(self, id):
        """
        В поле day таблицы timetable хранятся числа от 1 до 12.
        Каждое число обозначает номер дня недели в двухнедельном цикле.
        1 - Понедельник верхней недели
        2 - Вторник верхней недели
        8 - Понедельник нижней недели
        9 - Вторник нижней недели

        """
        labels = ['day', 'fk_subject_id', 'room_numb', 'start_time']    # убираем пустые поля и поле id
        text_labels = ', '.join(labels).rstrip(',')
        try:
            row = input(f'Введите следующие данные через запятую:\n {text_labels}, верхняя/нижняя неделя\n').split(',')
            new_row = [value.replace(' ', '') for value in row]
            if new_row[-1].lower() == 'верхняя':
                try:
                    day = DAYS.index(new_row[0].lower()) + 1
                    new_row[0] = str(day)
                except:
                    QMessageBox.about(self, "Error", f"field 'day' filled improperly")
                    return
            elif new_row[-1].lower() == 'нижняя':
                try:
                    day = DAYS.index(new_row[0].lower()) + 1
                    new_row[0] = str(day + 7)
                except:
                    QMessageBox.about(self, "Error", f"field 'day' filled improperly")
                    return
            else:
                QMessageBox.about(self, "Error", f"field 'верхняя/нижняя неделя' filled improperly")
                return
            new_row[2] = '\'' + new_row[2] + '\''
            new_row[3] = '\'' + new_row[3] + '\''
            # поля room_numb и start_time должны выглядеть как строки
            new_values = ''
            for i, label in enumerate(labels):
                new_values += label + '=' + new_row[i] + ','
            new_values = new_values.rstrip(',')
            print(f'UPDATE {self.table_name} SET {new_values} WHERE {self.table_name}_id = {id}')
            cursor.execute(f"""
            UPDATE {self.table_name} SET {new_values} WHERE {self.table_name}_id = {id}
            """)
        except:
            QMessageBox.about(self, "Error", f"Enter all fields, strings have to be inside single quotes")


    def _delete_row(self, id, row):
        print(f"DELETE FROM timetable WHERE timetable_id = {str(id)}")
        try:
            cursor.execute(f"""
            DELETE FROM timetable WHERE timetable_id = {str(id)}
            """)
        except:
            QMessageBox.about(self, "Error", "Wrong ID!")
        self.removeRow(row + 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
