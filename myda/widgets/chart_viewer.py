from myda.utils import get_logger
from PyQt5 import QtCore, QtGui, QtWidgets, sip
import os
import sys
import tempfile
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import QUrl


logger = get_logger(__name__)
# try:
#     from PyQt5 import QtWebEngineWidgets
# except ImportError as e:
#     if e.msg == "QtWebEngineWidgets must be imported before a QCoreApplication instance is created":
#         logger.info("Reinitialized existing QApplication instance to allow import of QtWebEngineWidgets.")
#
#         app = QtWidgets.QApplication.instance()
#         app.quit()
#         sip.delete(app)
#         from PyQt5 import QtWebEngineWidgets
#
#         app.__init__(sys.argv)
#     else:
#         raise e


class ChartViewer(QtWebEngineWidgets.QWebEngineView):
    def __init__(self):
        super().__init__()
        self.resize(1000, 1000)

    def set_figure(self):
        url = os.getcwd() + '/render.html'
        self.load(QUrl.fromLocalFile(url))