import sys
import random
from PySide6.QtWidgets import *
from PySide6.QtGui import QColor
from PySide6 import QtCore
from PySide6.QtGui import QFont
from lib import new_db
import re
from datetime import datetime


colors = {1: ['#E9E0E0', 'Comum'], 2: ['#51E369', 'Incomum'], 3: ['#5CCFF5', 'Raro'],
          4: ['#C881FF', 'Épico'], 5: ['#F5D94F', 'Lendário'], 0: ['#c3e3e5', 'Unknown']}


class MainView(QWidget):
    def __init__(self, *args):
        super(MainView, self).__init__(*args)
        self.layout = Layout.horizontal(self)
        self.create_members_widgets()

        frame_layout = Layout.vertical(self)
        self.layout.addLayout(frame_layout, 6)

        self.name_label = QLabel(self)
        frame_layout.addWidget(self.name_label, 1)

        self.year_frame_layout = Layout.horizontal(self)
        frame_layout.addLayout(self.year_frame_layout, 1)

        self.month_frame_layout = Layout.horizontal(self)
        frame_layout.addLayout(self.month_frame_layout, 1)

        self.day_frame_layout = Layout.horizontal(self)
        frame_layout.addLayout(self.day_frame_layout, 1)

        self.gifts_frame = QScrollArea(self)
        self.gifts_frame.setWidgetResizable(True)
        self.g_widget = QWidget(self.gifts_frame)
        # self.gifts_frame.setStyleSheet("background-color: red")
        self.gifts_frame_layout = Layout.vertical(self.g_widget)
        self.gifts_frame_layout.setSpacing(1)
        frame_layout.addWidget(self.gifts_frame, 10)
        self.gifts_frame.setWidget(self.g_widget)


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
        gifts = new_db.get_gifts(name)

        self.clear_gifts()
        for gift in gifts:
            g = GiftWidget(self.g_widget, gift=gift)
            self.gifts_frame_layout.addWidget(g)

    def clear_gifts(self):
        for i in reversed(range(self.gifts_frame_layout.count())):
            self.gifts_frame_layout.itemAt(i).widget().setParent(None)

    def clear_dates(self):
        for i in reversed(range(self.year_frame_layout.count())):
            self.year_frame_layout.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.month_frame_layout.count())):
            self.month_frame_layout.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.day_frame_layout.count())):
            self.day_frame_layout.itemAt(i).widget().setParent(None)

    def fill_dates(self, dates):
        self.clear_dates()

        years = set(())
        months = set(())
        days = set(())
        for date in dates:
            d = date.gift_timestamp
            years.add(d.year)
            months.add(d.month)
            days.add(d.day)

        for year in years:
            button = QPushButton(str(year), self)
            self.year_frame_layout.addWidget(button)

        for month in months:
            button = QPushButton(str(month), self)
            self.month_frame_layout.addWidget(button)

        for day in days:
            button = QPushButton(str(day), self)
            self.day_frame_layout.addWidget(button)

    def update_list(self):
        pattern = self.members_searchbar.text().lower().strip()
        self.member_list.clear()
        for member in self.members:
            if re.findall(pattern, member.name, re.IGNORECASE):
                member_item = QListWidgetItem(member.name)
                self.member_list.addItem(member_item)
        self.members_label.setText(f'Membros ({self.member_list.count()})')


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
        name_label.setAlignment(QtCore.Qt.AlignCenter)
        gift_label = GiftLabel(f"{self.gift.gift} Lv. {self.gift.level}", self, colors.get(self.gift.level)[0])
        gift_label.setAlignment(QtCore.Qt.AlignCenter)
        left_layout.addWidget(name_label)
        left_layout.addWidget(gift_label)

        date_label = GiftLabel(f'{self.gift.gift_timestamp:%d/%B/%Y}', self, '#ffffff')
        date_label.setAlignment(QtCore.Qt.AlignCenter)
        time_label = GiftLabel(f'{self.gift.gift_timestamp:%H:%M:%S}', self, "#ffffff")
        time_label.setAlignment(QtCore.Qt.AlignCenter)
        right_layout.addWidget(date_label)
        right_layout.addWidget(time_label)



class ReportView(QWidget):
    def __init__(self, *args):
        super(ReportView, self).__init__(*args)


class ConfigView(QWidget):
    def __init__(self, *args):
        super(ConfigView, self).__init__(*args)


tab_buttons = {'Main': MainView, 'Relatórios': ReportView, "Configs": ConfigView}


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
        self.setStyleSheet(f"color: {color}")
        font = QFont("Segou UI", 14, 10)
        self.setFont(font)





if __name__ == '__main__':
    app = QApplication([])
    root = GUI()
    root.show()
    sys.exit(app.exec())
