import sys
import random
from PySide6.QtWidgets import *
from PySide6.QtGui import QColor
from PySide6 import QtCore
from PySide6.QtGui import QFont
from lib import new_db
import re
from datetime import datetime
import gifts_grabber


colors = {1: ['#E9E0E0', 'Comum'], 2: ['#51E369', 'Incomum'], 3: ['#5CCFF5', 'Raro'],
          4: ['#C881FF', 'Épico'], 5: ['#F5D94F', 'Lendário'], 0: ['#c3e3e5', 'Unknown']}
today = datetime.today()


class MainView(QWidget):
    def __init__(self, *args):
        super(MainView, self).__init__(*args)
        self.layout = Layout.horizontal(self)
        self.create_members_widgets()

        frame_layout = Layout.vertical(self)
        self.layout.addLayout(frame_layout, 6)

        self.name_label = QLabel(self)
        frame_layout.addWidget(self.name_label, 1)

        self.date_buttons = DateButtonsFrame(self)
        frame_layout.addWidget(self.date_buttons)


        self.gifts_frame = QScrollArea(self)
        self.gifts_frame.setWidgetResizable(True)
        self.g_widget = QWidget(self.gifts_frame)
        # self.gifts_frame.setStyleSheet("background-color: red")
        self.gifts_frame_layout = Layout.vertical(self.g_widget)
        self.gifts_frame_layout.setSpacing(1)
        frame_layout.addWidget(self.gifts_frame, 10)
        self.gifts_frame.setWidget(self.g_widget)

        get_gifts = QPushButton('Pegar Presentes')
        get_gifts.setStyleSheet("background-color: #00ffff")
        frame_layout.addWidget(get_gifts)
        get_gifts.clicked.connect(gifts_grabber.main)

    def create_members_widgets(self):
        self.members_layout = Layout.vertical(self)
        self.layout.addLayout(self.members_layout)

        self.members_label = QLabel('Membros', self)
        self.members_layout.addWidget(self.members_label)

        self.members_searchbar = QLineEdit(self)
        self.members_searchbar.textChanged.connect(self.update_list)
        self.members_layout.addWidget(self.members_searchbar)

        self.member_list = QListWidget(self)
        self.member_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.members_layout.addWidget(self.member_list)
        self.members = new_db.get_all_members()
        self.update_list()

    def on_selection_changed(self):
        name = self.member_list.selectedItems()[0].text()
        self.name_label.setText(name)
        dates = new_db.get_member_dates(name)
        self.fill_dates(dates)
        # gifts = new_db.get_gifts(name)
        self.add_gifts()

    def add_gifts(self):
        name = self.member_list.selectedItems()[0].text()
        gifts = new_db.get_gifts_by_date(name, self.date_buttons.selected_year, self.date_buttons.selected_month,
                                         self.date_buttons.selected_day)
        print(f'{self.date_buttons.selected_day}/{self.date_buttons.selected_month}/{self.date_buttons.selected_year}')

        self.clear_gifts()
        for gift in gifts:
            g = GiftWidget(self.g_widget, gift=gift)
            self.gifts_frame_layout.addWidget(g)

    def clear_gifts(self):
        for i in reversed(range(self.gifts_frame_layout.count())):
            self.gifts_frame_layout.itemAt(i).widget().setParent(None)

    def clear_dates(self):
        self.date_buttons.clear()

    def fill_dates(self, dates):
        self.date_buttons.clear()
        self.date_buttons.add(dates)
        self.date_buttons.set_closest_date()

    def update_list(self):
        pattern = self.members_searchbar.text().lower().strip()
        self.member_list.clear()
        for member in self.members:
            if re.findall(pattern, member.name, re.IGNORECASE):
                member_item = QListWidgetItem(member.name)
                self.member_list.addItem(member_item)
        self.members_label.setText(f'Membros ({self.member_list.count()})')


class DateButtonsFrame(QWidget):
    def __init__(self, parent):
        super(DateButtonsFrame, self).__init__(parent)

        self.selected_year = None
        self.selected_month = None
        self.selected_day = None

        layout = Layout.vertical(self)

        self.year_frame_layout = Layout.horizontal(self)
        self.year_frame_layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.addLayout(self.year_frame_layout, 1)

        self.month_frame_layout = Layout.horizontal(self)
        self.month_frame_layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.addLayout(self.month_frame_layout, 1)

        self.day_frame_layout = Layout.horizontal(self)
        self.day_frame_layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.addLayout(self.day_frame_layout, 1)

    def clear(self):
        for i in reversed(range(self.year_frame_layout.count())):
            self.year_frame_layout.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.month_frame_layout.count())):
            self.month_frame_layout.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.day_frame_layout.count())):
            self.day_frame_layout.itemAt(i).widget().setParent(None)

    def add(self, dates):
        years = set(())
        months = set(())
        days = set(())
        for date in dates:
            # d = date.gift_timestamp
            years.add(date.year)
            months.add(date.month)
            days.add(date.day)

        for year in sorted(years):
            button = DateButton(str(year), self, self.set_year)
            # button = QPushButton(str(year), self)
            # button.clicked.connect(self.test)
            self.year_frame_layout.addWidget(button)

        for month in sorted(months):
            button = DateButton(str(month), self, self.set_month)
            # button = QPushButton(str(month), self)
            # button.clicked.connect(self.test)
            self.month_frame_layout.addWidget(button)

        for day in sorted(days):
            button = DateButton(str(day), self, self.set_day)
            # button = QPushButton(str(day), self)
            # button.clicked.connect(self.test)
            self.day_frame_layout.addWidget(button)

    def set_year(self):
        button = self.sender()
        self.selected_year = button.text()
        for i in range(self.year_frame_layout.count()):
            other = self.year_frame_layout.itemAt(i).widget()
            if button is other:
                pass
            else:
                other.setChecked(False)
        self.parent().add_gifts()

    def set_month(self):
        button = self.sender()
        self.selected_month = button.text()
        for i in range(self.month_frame_layout.count()):
            other = self.month_frame_layout.itemAt(i).widget()
            if button is other:
                pass
            else:
                other.setChecked(False)
        self.parent().add_gifts()

    def set_day(self):
        button = self.sender()
        self.selected_day = button.text()
        for i in range(self.day_frame_layout.count()):
            other = self.day_frame_layout.itemAt(i).widget()
            if button is other:
                pass
            else:
                other.setChecked(False)
        self.parent().add_gifts()


    def repopulate(self):
        pass

    def set_closest_date(self):
        last_year = self.year_frame_layout.count()-1
        button = self.year_frame_layout.itemAt(last_year).widget()
        button.click()
        # button.setChecked(True)

        last_month = self.month_frame_layout.count() - 1
        self.month_frame_layout.itemAt(last_month).widget().click()

        last_day = self.day_frame_layout.count() - 1
        self.day_frame_layout.itemAt(last_day).widget().click()


class DateButton(QPushButton):
    def __init__(self, text, parent, callback):
        super(DateButton, self).__init__(text, parent)
        self.setCheckable(True)
        self.clicked.connect(callback)


class GiftWidget(QWidget):
    def __init__(self, parent, gift):
        super(GiftWidget, self).__init__(parent)
        c = ('yellow', 'blue') if parent.layout().count() % 2 == 0 else ('purple', 'green')
        self.gift = gift
        self.setStyleSheet(f"background-color: {random.choice(c)}")
        self.setStyleSheet(f'background-color: #232323')
        self.setFixedHeight(80)

        self.layout = Layout.horizontal(self)

        left_layout = Layout.vertical(self)
        self.layout.addLayout(left_layout, 8)

        right_layout = Layout.vertical(self)
        self.layout.addLayout(right_layout, 1)

        name_label = GiftLabel(self.gift.member, self, '#f4ebba')
        gift_label = GiftLabel(f"{self.gift.gift} Lv. {self.gift.level}", self, colors.get(self.gift.level)[0])
        left_layout.addWidget(name_label)
        left_layout.addWidget(gift_label)

        hour = int(self.gift.seconds/60/60)
        minute = int(self.gift.seconds/60 % 60)
        second = self.gift.seconds % 60
        timestamp = datetime(self.gift.year, self.gift.month, self.gift.day, hour, minute, second)

        date_label = GiftLabel(f'{timestamp:%d/%B/%Y}', self, '#ffffff')
        time_label = GiftLabel(f'{timestamp:%H:%M:%S}', self, "#ffffff")
        right_layout.addWidget(date_label)
        right_layout.addWidget(time_label)


class ReportView(QWidget):
    def __init__(self, *args):
        super(ReportView, self).__init__(*args)


class ConfigView(QWidget):
    def __init__(self, *args):
        super(ConfigView, self).__init__(*args)


class FailsView(QWidget):
    def __init__(self, *args):
        super(FailsView, self).__init__(*args)


tab_buttons = {'Main': MainView, 'Relatórios': ReportView, "Configs": ConfigView, "Falhas": FailsView}


class GUI(QWidget):
    def __init__(self, *args):
        super(GUI, self).__init__(*args)
        screen = QApplication.primaryScreen()

        # Configure Main Window
        self.setGeometry(200, 200, 1100, 650)
        self.setMinimumSize(550, 375)
        self.layout = Layout.vertical(self)

        tabs = QTabWidget(self)
        for name, cls in tab_buttons.items():
            tabs.addTab(cls(tabs), name)
        self.layout.addWidget(tabs)


class Layout:
    @classmethod
    def configure(cls, layout):
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    @classmethod
    def vertical(cls, parent):
        layout = QVBoxLayout(parent)
        cls.configure(layout)
        return layout

    @classmethod
    def horizontal(cls, parent):
        layout = QHBoxLayout(parent)
        cls.configure(layout)
        return layout

    @classmethod
    def grid(cls, parent):
        layout = QGridLayout(parent)
        cls.configure(layout)
        return layout

    @classmethod
    def form(cls, parent):
        layout = QFormLayout(parent)
        cls.configure(layout)
        return layout


class GiftLabel(QLabel):
    def __init__(self, text, parent, color):
        super(GiftLabel, self).__init__(text, parent)
        # self.setStyleSheet("color: red")
        self.setStyleSheet(f'color: {color}')
        font = QFont("Segou UI", 14, 10)
        self.setFont(font)
        self.setAlignment(QtCore.Qt.AlignCenter)




if __name__ == '__main__':
    app = QApplication([])
    root = GUI()
    root.show()
    sys.exit(app.exec())
