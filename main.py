import sys
import pymysql
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QLineEdit,
    QDateTimeEdit, QSpinBox, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtGui import QPixmap

class RestaurantApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Рестораны и Бронирование')
        self.resize(1300, 900)
        self.setStyleSheet("""
            QWidget {
                background-color: #262626;
                color: #EDEDED;
                font-family: 'Segoe UI Black', sans-serif;
                font-size: 14px;
            }

            QLabel {
                font-weight: 600;
                margin-top: 10px;
                margin-bottom: 5px;
                font-size: 15px;
            }

            QPushButton {
                background-color: #3d3d3d;
                color: white;
                padding: 10px 14px;
                border-radius: 10px;
                font-weight: bold;
                transition: background-color 0.3s ease;
                
                
            }

            QPushButton:hover {
                background-color: #464646;
            }

            QLineEdit, QSpinBox, QDateTimeEdit {
                background-color: #3d3d3d;
                border: 1px solid #3d3d3d;
                border-radius: 8px;
                padding: 8px;
                color: white;
            }

            QListWidget, QTableWidget {
                background-color: #3d3d3d;
                border: 1px solid #3d3d3d;
                border-radius: 10px;
            }

            QHeaderView::section {
                background-color: #3d3d3d;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }

            QListWidget::item:selected, QTableWidget::item:selected {
                background-color: #cccc;
                color: white;
            }

            QTableWidget {
                gridline-color: #555;
            }
        """)

        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            password='sqladmin',
            database='meal_base',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        self.layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()


        self.left_layout.setContentsMargins(10, 10, 10, 10)
        self.left_layout.setSpacing(10)
        self.right_layout.setContentsMargins(10, -5, 10, 10)
        self.right_layout.setSpacing(10)

        self.restaurant_list = QListWidget()
        self.restaurant_list.setStyleSheet("""
            QListWidget {
                font-size: 16pt;
            }
        """)
        self.restaurant_list.itemClicked.connect(self.show_menu)

        self.photo_label = QLabel('Фото ресторана')
        self.photo_label.setScaledContents(True)
        self.photo_label.setMaximumWidth(400)
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setStyleSheet('''
            QLabel {
                border: 3px solid #3d3d3d;
                background-color: #3d3d3d;
                border-radius: 10px;
                color: #888;
            }
        ''')

        self.menu_table = QTableWidget()
        self.menu_table.setColumnCount(3)
        self.menu_table.verticalHeader().setVisible(False)
        self.menu_table.setHorizontalHeaderLabels(['Блюдо', 'Цена (₴)', 'Масса (г.)'])
        self.menu_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.menu_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.menu_table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)


        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Ваше имя')

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('Ваш телефон')

        self.datetime_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_input.setCalendarPopup(True)

        self.people_input = QSpinBox()
        self.people_input.setMinimum(1)
        self.people_input.setMaximum(20)

        self.reserve_button = QPushButton('Забронировать и Заказать')
        self.reserve_button.clicked.connect(self.make_reservation)

        self.view_all_button = QPushButton('📖 Посмотреть все записи')
        self.view_all_button.clicked.connect(self.show_all_reservations)

        self.left_layout.addWidget(QLabel('📍 Рестораны:'))
        self.left_layout.addWidget(self.restaurant_list)

        self.right_layout.addWidget(QLabel('🍽️ Добро пожаловать в систему ресторанов!'))
        self.right_layout.addWidget(self.photo_label)
        self.right_layout.addWidget(QLabel('📋 Меню ресторана:'))
        self.right_layout.addWidget(self.menu_table)
        self.right_layout.addWidget(QLabel('📝 Бронирование столика:'))
        self.right_layout.addWidget(self.name_input)
        self.right_layout.addWidget(self.phone_input)
        self.right_layout.addWidget(self.datetime_input)
        self.right_layout.addWidget(QLabel('Количество человек:'))
        self.right_layout.addWidget(self.people_input)
        self.right_layout.addWidget(self.reserve_button)
        self.right_layout.addWidget(self.view_all_button)

        self.layout.addLayout(self.left_layout, 3)
        self.layout.addLayout(self.right_layout, 5)
        self.setLayout(self.layout)

        self.selected_rest_id = None
        self.all_reservations_window = None
        self.load_restaurants()

    def load_restaurants(self):
        self.restaurant_list.clear()
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, rest_name, photo FROM restaurant")
            restaurants = cursor.fetchall()
            self.restaurants = {rest['id']: rest for rest in restaurants}
            for rest in restaurants:
                self.restaurant_list.addItem(f"{rest['id']}: {rest['rest_name']}")

    def show_all_reservations(self):
        if self.all_reservations_window is None or not self.all_reservations_window.isVisible():
            self.all_reservations_window = AllReservationsWindow(self.connection)
            self.all_reservations_window.show()
        else:
            self.all_reservations_window.raise_()
            self.all_reservations_window.activateWindow()

    def show_menu(self, item):
        text = item.text()
        self.selected_rest_id = int(text.split(':')[0])
        restaurant = self.restaurants.get(self.selected_rest_id)

        if restaurant and restaurant['photo']:
            pixmap = QPixmap(restaurant['photo'])
            if not pixmap.isNull():
                self.photo_label.setPixmap(pixmap)
                self.photo_label.adjustSize()  # Подгоняет QLabel под изображение
            else:
                self.photo_label.setText('Нет фото')
        else:
            self.photo_label.setText('Нет фото')

        with self.connection.cursor() as cursor:
            cursor.execute("SELECT meal_id, meal_name, price, ccal FROM menu WHERE rest_id = %s", (self.selected_rest_id,))
            meals = cursor.fetchall()

            self.menu_table.setRowCount(len(meals))
            for row, meal in enumerate(meals):
                self.menu_table.setItem(row, 0, QTableWidgetItem(meal['meal_name']))
                self.menu_table.setItem(row, 1, QTableWidgetItem(f"{meal['price']:.2f}"))
                self.menu_table.setItem(row, 2, QTableWidgetItem(str(meal['ccal']) if meal['ccal'] else ''))
                self.menu_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, meal['meal_id'])

    def make_reservation(self):
        if not self.selected_rest_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите ресторан перед бронированием.')
            return

        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        datetime_value = self.datetime_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        people_count = self.people_input.value()

        selected_items = self.menu_table.selectedItems()
        if not name or not phone:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля.')
            return
        if not selected_items:
            QMessageBox.warning(self, 'Ошибка', 'Выберите хотя бы одно блюдо для заказа.')
            return

        selected_meals = {}
        for item in selected_items:
            row = item.row()
            meal_id = self.menu_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            price = float(self.menu_table.item(row, 1).text())
            selected_meals[meal_id] = price

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO reserv (rest_id, person_name, person_phone, time, people_count)
                    VALUES (%s, %s, %s, %s, %s)
                """, (self.selected_rest_id, name, phone, datetime_value, people_count))
                self.connection.commit()
                reserv_id = cursor.lastrowid

                for meal_id, price in selected_meals.items():
                    cursor.execute("""
                        INSERT INTO orders (id_rest, id_meal, id_table, count_of_meals, price, order_time)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (self.selected_rest_id, meal_id, reserv_id, 1, price, datetime_value))
                self.connection.commit()

            QMessageBox.information(self, 'Успех', 'Бронирование и заказ блюд успешно оформлены!')
            self.name_input.clear()
            self.phone_input.clear()
            self.people_input.setValue(1)
            self.datetime_input.setDateTime(QDateTime.currentDateTime())
            self.menu_table.clearSelection()

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка базы данных:\n{str(e)}')



class AllReservationsWindow(QWidget):
    def __init__(self, connection):
        super().__init__()
        self.setWindowTitle("Все бронирования и заказы")
        self.resize(1000, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #262626;
                color: #EDEDED;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QTableWidget {
                background-color: #3d3d3d;
                border: 1px solid #3d3d3d;
                border-radius: 10px;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: white;
                font-weight: bold;
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #3d3d3d;
            }
        """)

        self.connection = connection
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.verticalHeader().setVisible(False)

        self.table.setHorizontalHeaderLabels([
            'Имя', 'Телефон', 'Дата/время', 'Ресторан', 'Блюдо', 'Цена (₴)'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    r.person_name,
                    r.person_phone,
                    r.time,
                    res.rest_name,
                    m.meal_name,
                    o.price
                FROM orders o
                JOIN reserv r ON o.id_table = r.table_id
                JOIN restaurant res ON o.id_rest = res.id
                JOIN menu m ON o.id_meal = m.meal_id
                ORDER BY r.time DESC
            """)
            rows = cursor.fetchall()

            self.table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                self.table.setItem(row_idx, 0, QTableWidgetItem(row['person_name']))
                self.table.setItem(row_idx, 1, QTableWidgetItem(row['person_phone']))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(row['time'])))
                self.table.setItem(row_idx, 3, QTableWidgetItem(row['rest_name']))
                self.table.setItem(row_idx, 4, QTableWidgetItem(row['meal_name']))
                self.table.setItem(row_idx, 5, QTableWidgetItem(f"{row['price']:.2f}"))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RestaurantApp()
    window.show()
    sys.exit(app.exec())
