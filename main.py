# main.py

import sys
from PySide6 import QtWidgets
from MyPySide6.Main_interface import MyWidget

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
