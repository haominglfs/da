
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QUrl
import sys
import os
from pyecharts.charts import Bar
import pandas as pd

class QFileDialogWindow(QWidget):
    def __init__(self):
        super(QFileDialogWindow,self).__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.button = QPushButton('打开文件')
        self.button.clicked.connect(self.loadText)
        self.layout.addWidget(self.button)

        self.contents = QWebEngineView()
        self.contents.setFixedHeight(500)
        self.contents.setFixedWidth(1000)
        self.layout.addWidget(self.contents)

        self.setLayout(self.layout)
        self.setWindowTitle('文件对话框')

    def loadText(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        if dialog.exec_():
            filenames = dialog.selectedFiles()
            df = pd.read_excel(filenames[0])
            dfsum = df.groupby('Energy').sum()
            y = dfsum['Net capacity (MW)'].to_list()
            x = dfsum.index.to_list()
            bar = Bar()
            bar.add_xaxis(x)
            bar.add_yaxis("Net capacity (MW)", y)
            bar.render()
            url = os.getcwd() + '/render.html'
            self.contents.load(QUrl.fromLocalFile(url))

    def loadweb(self):
        bar = Bar()
        bar.add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
        bar.add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
        # render 会生成本地 HTML 文件，默认会在当前目录生成 render.html 文件
        # 也可以传入路径参数，如 bar.render("mycharts.html")
        bar.render()
        url = os.getcwd()+'/render.html'
        self.contents.load(QUrl.fromLocalFile(url))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = QFileDialogWindow()
    main.show()
    sys.exit(app.exec_())