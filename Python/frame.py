# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'frame.ui'
#
# Created: Tue Jan  5 16:16:44 2016
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        Frame.resize(400, 300)
        Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)

        self.retranslateUi(Frame)

    def retranslateUi(self, Frame):
        _translate = QtCore.QCoreApplication.translate
        Frame.setWindowTitle(_translate("Frame", "Frame"))

