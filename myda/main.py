import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from myda import mainWin

if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    mainWin = mainWin.MainWindow()
    sys.exit(app.exec())