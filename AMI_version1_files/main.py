# pyinstaller --hidden-import cv2 --hidden-import torch --hidden-import PIL main.py
# above command tp be used to convert it into an executable (optional)

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from cv2 import cv2
import numpy as np
from PIL import Image, ImageEnhance
import torch
import time

camera = 0
threshold = 0.6
model = torch.hub.load(r'.', 'custom', path='best (1).pt', force_reload=True, source='local')


def getColor(name):
    if name == "RBC":
        return 255, 0, 0
    elif name == "WBC":
        return 0, 0, 255
    else:
        return 0, 255, 255


class Ui_MainWindow(object):

    def __init__(self):
        self.filter_open = False
        self.worker = WorkerClassCamera()
        self.worker.start()
        self.worker.ImageUpdate.connect(self.ImageUpdateSlot)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(QtCore.QSize(1290, 900))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.ImagePrev = QtWidgets.QLabel(self.centralwidget)
        self.ImagePrev.setGeometry(QtCore.QRect(0, 0, 1290, 900))
        self.ImagePrev.setText("")
        self.ImagePrev.setObjectName("ImagePrev")
        self.ImagePrev.setScaledContents(True)
        self.camera = QtWidgets.QLabel(self.centralwidget)
        self.camera.setGeometry(QtCore.QRect(1230, 10, 40, 40))
        self.camera.setText("")
        self.camera.setPixmap(QtGui.QPixmap("Images/camera.png"))
        self.camera.setScaledContents(True)
        self.camera.setObjectName("camera")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(10, 860, 361, 521))
        self.widget.setStyleSheet("background-color: rgb(150,150,150);\n"
                                  "border-radius: 20px;")
        self.widget.setObjectName("widget")
        self.formWidget = QtWidgets.QWidget(self.widget)
        self.formWidget.setGeometry(QtCore.QRect(20, 40, 321, 476))
        self.formWidget.setStyleSheet("background-color: rgba(255,255,255, 0);")
        self.formWidget.setObjectName("formWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formWidget)
        self.formLayout.setRowWrapPolicy(QtWidgets.QFormLayout.WrapAllRows)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setObjectName("formLayout")
        self.f1 = QtWidgets.QLabel(self.formWidget)
        self.f1.setStyleSheet("background-color: rgba(255,255,255, 0); color: white;")
        self.f1.setObjectName("f1")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.f1)
        self.f1b = QtWidgets.QSlider(self.formWidget)
        self.f1b.setStyleSheet("background-color: rgba(255,255,255, 0);")
        self.f1b.setOrientation(QtCore.Qt.Horizontal)
        self.f1b.setObjectName("f1b")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.f1b)
        self.f2 = QtWidgets.QLabel(self.formWidget)
        self.f2.setStyleSheet("background-color: rgba(255,255,255, 0); color: white;")
        self.f2.setObjectName("f2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.f2)
        self.f2b = QtWidgets.QSlider(self.formWidget)
        self.f2b.setStyleSheet("background-color: rgba(255,255,255, 0);")
        self.f2b.setOrientation(QtCore.Qt.Horizontal)
        self.f2b.setObjectName("f2b")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.f2b)
        self.f6 = QtWidgets.QLabel(self.formWidget)
        self.f6.setStyleSheet("background-color: rgba(255,255,255, 0); color: white;")
        self.f6.setObjectName("f6")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.f6)
        self.f6b = QtWidgets.QSlider(self.formWidget)
        self.f6b.setStyleSheet("background-color: rgba(255,255,255, 0);")
        self.f6b.setOrientation(QtCore.Qt.Horizontal)
        self.f6b.setObjectName("f6b")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.f6b)
        self.f8 = QtWidgets.QLabel(self.formWidget)
        self.f8.setStyleSheet("background-color: rgba(255,255,255, 0); color: white;")
        self.f8.setObjectName("f8")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.f8)
        self.f8b = QtWidgets.QSlider(self.formWidget)
        self.f8b.setStyleSheet("background-color: rgba(255,255,255, 0);")
        self.f8b.setOrientation(QtCore.Qt.Horizontal)
        self.f8b.setObjectName("f8b")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.f8b)
        self.filter_menu = QtWidgets.QLabel(self.widget)
        self.filter_menu.setGeometry(QtCore.QRect(160, 0, 41, 41))
        self.filter_menu.setStyleSheet("background-color: rgba(255,255,255, 0);")
        self.filter_menu.setText("")
        self.filter_up = QtGui.QPixmap("Images/arrow.png")
        self.filter_down = QtGui.QPixmap("Images/arrow.png").transformed(QtGui.QTransform().rotate(180))
        self.filter_menu.setPixmap(self.filter_up)
        self.filter_menu.setScaledContents(True)
        self.filter_menu.setObjectName("filter_menu")
        self.logo = QtWidgets.QLabel(self.centralwidget)
        self.logo.setGeometry(QtCore.QRect(10, 0, 81, 51))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("Images/logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        MainWindow.setCentralWidget(self.centralwidget)

        self.filter_menu.mousePressEvent = self.FilterMenuToggle

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    @staticmethod
    def brightness(image, value):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(image)
        value = value / 50 + 1
        return cv2.cvtColor(np.asarray(ImageEnhance.Brightness(im_pil).enhance(value)), cv2.COLOR_RGB2BGR)

    @staticmethod
    def contrast(image, value):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(image)
        value = value / 20 + 1
        return cv2.cvtColor(np.asarray(ImageEnhance.Contrast(im_pil).enhance(value)), cv2.COLOR_RGB2BGR)

    @staticmethod
    def shadows(image, value):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(image)
        value = 1 - value / 100
        return cv2.cvtColor(np.asarray(ImageEnhance.Brightness(im_pil).enhance(value)), cv2.COLOR_RGB2BGR)

    @staticmethod
    def sharpness(image, value):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(image)
        value = value / 20 + 1
        return cv2.cvtColor(np.asarray(ImageEnhance.Sharpness(im_pil).enhance(value)), cv2.COLOR_RGB2BGR)

    def ImageUpdateSlot(self, image):
        if self.f1b.value() > 0:
            image = self.brightness(image, self.f1b.value())
        if self.f2b.value() > 0:
            image = self.contrast(image, self.f2b.value())
        if self.f8b.value() > 0:
            image = self.sharpness(image, self.f8b.value())
        if self.f6b.value() > 0:
            image = self.shadows(image, self.f6b.value())
        self.ImagePrev.setPixmap(QtGui.QPixmap.fromImage(convertToQImage(image)))

    def FilterMenuToggle(self, MainWindow):
        if not self.filter_open:
            self.filter_open = True
            self.filter_menu.setPixmap(self.filter_down)
            self.widget.setGeometry(QtCore.QRect(10, 610, 361, 521))
        else:
            self.filter_open = False
            self.filter_menu.setPixmap(self.filter_up)
            self.widget.setGeometry(QtCore.QRect(10, 860, 361, 521))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AMI v0.1"))
        self.f1.setText(_translate("MainWindow", "Brightness"))
        self.f2.setText(_translate("MainWindow", "Contrast"))
        self.f6.setText(_translate("MainWindow", "Shadows"))
        self.f8.setText(_translate("MainWindow", "Sharpness"))


def convertToQImage(Image):
    return QtGui.QImage(Image.data, Image.shape[1], Image.shape[0], QtGui.QImage.Format_BGR888)


class WorkerClassCamera(QThread):
    ImageUpdate = QtCore.pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.ActiveThread = True

    def run(self):
        Captured = cv2.VideoCapture(camera)
        pT = 0
        nT = 0

        while self.ActiveThread:
            ret, frame = Captured.read()

            frame = cv2.flip(frame, 1)
            nT = time.time()
            fps = 1 / (nT - pT)
            pT = nT

            class_ids = []
            labels = []
            id = 0
            confidences = []
            boxes = []
            results = model([frame])
            res = results.pandas().xyxy[0]
            for index, row in res.iterrows():
                if row['confidence'] >= threshold:
                    class_ids.append(id)
                    id += 1
                    confidences.append(row['confidence'])
                    boxes.append([row['xmin'], row['xmax'], row['ymin'], row['ymax']])
                    labels.append(row['name'])

            font = cv2.FONT_HERSHEY_PLAIN
            for i in range(len(class_ids)):
                xmin, xmax, ymin, ymax = boxes[i]
                color = getColor(labels[i])
                cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 1)
                cv2.putText(frame, labels[i] + " " + str(round(confidences[i], 2)), (int(xmin), int(ymin) - 3), font, 1,
                            color, None)

            cv2.putText(frame, "FPS: " + str(int(fps)), (570, 460), font, 1, (100, 255, 0), None)
            self.ImageUpdate.emit(frame)

    def stop(self):
        self.ActiveThread = False
        self.quit()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
