import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
from myda import mainWin
import myda.dbutils

if __name__ == '__main__':
    myda.dbutils.create_db()
    myda.dbutils.create_table()
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    mainWin = mainWin.MainWindow()
    sys.exit(app.exec())