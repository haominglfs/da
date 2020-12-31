# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Callable
from PyQt5 import QtCore, QtWidgets
from myda.widgets.navigator import Navigator
from myda.store import Store,GuiDataFrame
from myda.widgets.grapher import Grapher
import pandas as pd

refs = []


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.stacked_widget = None
        self.navigator = None
        self.splitter = None
        self.store = Store()
        refs.append(self)
        self.store.mainWin = self
        self.init_ui()

        df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        self.store.add_dataframe(df, 'simple')
        self.navigator.setCurrentItem(self.navigator.topLevelItem(0))

    def init_ui(self):
        self.resize(QtCore.QSize(int(0.7 * QtWidgets.QDesktopWidget().screenGeometry().width()),
                                 int(0.7 * QtWidgets.QDesktopWidget().screenGeometry().height())))
        # Center window on screen
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2), )
        self.setWindowTitle("myda")

        self.stacked_widget = QtWidgets.QStackedWidget()

        # self.stacked_widget.addWidget(Grapher(GuiDataFrame(df)))
        # Make the navigation bar
        self.navigator = Navigator(self.store)
        # Make splitter to hold nav and DataFrameExplorers
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.navigator)
        self.splitter.addWidget(self.stacked_widget)

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        nav_width = self.navigator.sizeHint().width()
        self.splitter.setSizes([nav_width, self.width() - nav_width])
        self.splitter.setContentsMargins(10, 10, 10, 10)

        self.make_menu_bar()
        self.setCentralWidget(self.splitter)
        self.show()

    ####################
    # Menu bar functions

    def make_menu_bar(self):
        menubar = self.menuBar()

        @dataclass
        class MenuItem:
            name: str
            func: Callable
            shortcut: str = ''

        items = {'Edit': [MenuItem(name='Import',
                                   func=self.import_dialog)
                    ]}

        # 添加菜单
        for menu_name in items.keys():
            menu = menubar.addMenu(menu_name)
            for x in items[menu_name]:
                action = QtWidgets.QAction(x.name, self)
                action.setShortcut(x.shortcut)
                action.triggered.connect(x.func)
                menu.addAction(action)

    def import_dialog(self):
        dialog = QtWidgets.QFileDialog()
        paths, _ = dialog.getOpenFileNames(filter="*.csv *.xlsx")
        for path in paths:
            self.store.import_dataframe(path)