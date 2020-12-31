from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import tempfile
import os


class Navigator(QtWidgets.QTreeWidget):
    def __init__(self,store):
        super().__init__()
        self.store = store
        store.navigator = self
        self.expandAll()
        self.setHeaderLabels(["Name", "Shape"])
        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 150)

    def sizeHint(self):
        # Width
        width = 0
        for i in range(self.columnCount()):
            width += self.columnWidth(i)
        return QtCore.QSize(300, 500)

    def selectionChanged(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection) -> None:
        super().selectionChanged(selected, deselected)
        item = self.selectedItems()[0]
        df_name = item.data(0, Qt.DisplayRole)
        self.store.select_gdf(df_name)