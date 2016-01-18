import sys
from PyQt5 import QtCore, QtGui, QtWidgets

class Visualisation_v1Application(QtWidgets):
  def __init__(self, None):
    super(QtGui.QWidget, self).__init__(parent)
    self.createWidgets()

  def createWidgets(self):
    self.ui = Ui_Frame()
    self.ui.setupUi(self)

if __name__ == "__main__":
  app = QApplication(sys.argv)
  myapp = Visualisation_v1Application()
  myapp.show()
  sys.exit(app.exec_())

