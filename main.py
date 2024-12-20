from PyQt5 import QtWidgets

from Window import MainWindow

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.showMaximized()
    sys.exit(app.exec_())
