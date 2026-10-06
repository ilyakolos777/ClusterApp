import sys
from PyQt6.QtWidgets import QApplication
from ui import ClusterApp

def main():
    app = QApplication(sys.argv)
    window = ClusterApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()