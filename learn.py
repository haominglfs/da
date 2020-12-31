import sys
from PyQt5.Qt import *

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.test_signal()

    def test_signal(self):
        self.obj = QObject()
        def destory_cao():
            print("对象被释放了")
        self.obj.destroyed.connect(destory_cao)

        del self.obj

        btn = QPushButton(self)
        btn.setText("点击我")
        # btn.clicked.connect()

class App(QApplication):
    def notify(self, receiver,evt):
        if receiver.inherits('QPushButton') and evt.type() == QEvent.MouseButtonPress:
            print(receiver,evt)
        return super().notify(receiver,evt)
        # print(receiver,evt)
        # return True

if __name__ == '__main__':
    app = App(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())