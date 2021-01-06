from PyQt5 import QtCore, QtGui, QtWidgets, sip
from PyQt5.QtCore import Qt
from typing import Union, List, Iterable


class Dragger(QtWidgets.QWidget):

    itemDropped = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def __init__(self, sources: List[str],
                 destinations: List[str], source_types: List[str]):
        super().__init__()
        self.remembered_values = {}
        # Search box
        self.search_bar = QtWidgets.QLineEdit()
        # self.search_bar.textChanged.connect(self.filter)

        # Sources list
        self.source_tree = self.SourceTree(self)
        self.source_tree.setHeaderLabels(['Name', 'Type'])
        self.set_sources(sources, source_types)
        self.source_tree.setSortingEnabled(True)

        # Depends on Search Box and Source list
        # self.filter()

        # Destinations tree
        self.dest_tree = self.DestinationTree(self)
        self.dest_tree.setHeaderLabels(['Name', ''])
        self.dest_tree.setColumnHidden(1, True)
        self.dest_tree.setItemsExpandable(False)
        self.dest_tree.setRootIsDecorated(False)

        # Configure drag n drop
        sorc = self.source_tree
        dest = self.dest_tree

        sorc.setDragDropMode(sorc.DragOnly)
        sorc.setSelectionMode(sorc.ExtendedSelection)
        sorc.setDefaultDropAction(QtCore.Qt.CopyAction)
        dest.setDragDropMode(dest.DragDrop)
        dest.setSelectionMode(dest.ExtendedSelection)
        dest.setDefaultDropAction(QtCore.Qt.MoveAction)

        # Buttons
        # self.kwargs_button = QtWidgets.QPushButton("Custom Kwargs")
        self.reset_button = QtWidgets.QPushButton("重置")
        self.finish_button = QtWidgets.QPushButton("完成")

        # Signals
        self.itemDropped.connect(self.apply_tree_settings)
        self.finish_button.clicked.connect(self.finish)
        self.reset_button.clicked.connect(self.reset)

        # Layout
        self.source_tree_layout = QtWidgets.QVBoxLayout()
        self.source_tree_layout.addWidget(self.search_bar)
        self.source_tree_layout.addWidget(self.source_tree)

        self.button_layout = QtWidgets.QHBoxLayout()
        # self.button_layout.addWidget(self.kwargs_button)
        self.button_layout.addWidget(self.reset_button)
        self.button_layout.addWidget(self.finish_button)

        self.main_layout = QtWidgets.QGridLayout()
        self.main_layout.addLayout(self.source_tree_layout, 0, 0)
        self.main_layout.addWidget(self.dest_tree, 0, 1)
        self.main_layout.addLayout(self.button_layout, 1, 0, 1, 2)

        self.setLayout(self.main_layout)

    def set_sources(self, sources: List[str], source_types: List[str]):

        for i in range(len(sources)):
            item = QtWidgets.QTreeWidgetItem(self.source_tree,
                                             [str(sources[i]), str(source_types[i])])

        #self.filter()

    def reset(self):
        self.remembered_values = {}
        self.clear_tree()

    # Clear tree items under each sections
    def clear_tree(self):
        root = self.dest_tree.invisibleRootItem()
        to_delete = []
        for i in range(root.childCount()):
            child = root.child(i)
            for j in range(child.childCount()):
                sub_child = child.child(j)
                to_delete.append(sub_child)

        for item in to_delete:
            sip.delete(item)

    class DestinationTree(QtWidgets.QTreeWidget):
        def dropEvent(self, e: QtGui.QDropEvent):
            super().dropEvent(e)
            self.parent().itemDropped.emit()

    class SourceTree(QtWidgets.QTreeWidget):
        def dropEvent(self, e: QtGui.QDropEvent):
            super().dropEvent(e)
            self.parent().itemDropped.emit()

    def set_destinations(self, destinations: List[str]):
        # Delete all sections
        root = self.dest_tree.invisibleRootItem()
        for i in reversed(range(root.childCount())):
            sip.delete(root.child(i))

        for dest in destinations:
            section = QtWidgets.QTreeWidgetItem(self.dest_tree, [dest])

            if dest in self.remembered_values.keys():
                for val in self.remembered_values[dest]:
                    item = QtWidgets.QTreeWidgetItem(section, [val])


    def apply_tree_settings(self):
        # Destination tree
        root = self.dest_tree.invisibleRootItem()
        root.setFlags(Qt.ItemIsEnabled)

        for i in range(root.childCount()):
            child = root.child(i)
            child.setExpanded(True)

            child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled)

            for j in range(child.childCount()):
                sub_child = child.child(j)
                sub_child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # Source tree
        root = self.source_tree.invisibleRootItem()
        root.setFlags(Qt.ItemIsEnabled)

        for i in range(root.childCount()):
            child = root.child(i)
            child.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        # Remember values
        self.remembered_values.update(self.get_data())

    def finish(self):
        self.finished.emit()

    def get_data(self):
        data = {}

        root = self.dest_tree.invisibleRootItem()
        for i in range(root.childCount()):
            child = root.child(i)
            section = child.text(0)
            data[section] = []

            for j in range(child.childCount()):
                sub_child = child.child(j)
                value = sub_child.text(0)
                data[section].append(value)

        return data