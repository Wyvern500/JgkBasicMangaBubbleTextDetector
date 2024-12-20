import os

import cv2
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QTabWidget, QVBoxLayout,
                             QPushButton, QStackedWidget, QListWidget, QMenuBar, QAction, QLabel, QLineEdit)
from PyQt5.QtCore import pyqtSignal

from Data import DataManager
from ImageViewer import ImageViewer
from JgkWidgets import ImageListItemWidget
from ModelHandler import ModelHandler


class WindowPage(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.parent = parent

    def onLobbyDataLoaded(self, data):
        pass

    def nextWindow(self):
        self.parent.nextPage()

    def prevWindow(self):
        self.parent.prevPage()

class MainWorkspacePage(WindowPage):

    def __init__(self, parent):
        super().__init__(parent)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.stretch(1)

        self.addLeftLayout()

        self.addCentralLayout()

        self.addRightLayout()

        self.setLayout(self.mainLayout)

    # Gui setup

    def addLeftLayout(self):
        self.leftLayout = QVBoxLayout()

        self.images = QListWidget()
        self.images.itemActivated.connect(self.onChooseImage)

        self.leftLayout.addWidget(self.images)

        self.mainLayout.addLayout(self.leftLayout)

    def onChooseImage(self, item):
        self.view.load_image({item.toolTip(): {}})

    def addCentralLayout(self):
        self.centralLayout = QVBoxLayout()

        self.addImageViewer()

        self.mainLayout.addLayout(self.centralLayout)

    def addImageViewer(self):
        self.view = ImageViewer(self)
        self.view.selectedRectSignal.connect(self.onSelectRect)
        self.view.rectTransformed.connect(self.updatePropertiesForRect)

        srcDir = "D:\\Coding\\Python\\MangaDownloader\\MangaDownloader\\images"

        self.view.load_image({f"{srcDir}\\185.jpg": {}})
        self.view.resetZoom()

        self.centralLayout.addWidget(self.view)

    def addRightLayout(self):
        self.rightLayout = QVBoxLayout()

        predict = QPushButton("Predict")
        predict.clicked.connect(self.toPredict)
        self.rightLayout.addWidget(predict)

        self.mainLayout.addLayout(self.rightLayout)

    # Misc stuff

    def toPredict(self):
        img = self.view.getCurrentImageAsNumpyImage()
        boxes = (self.parent.modelHandler
                 .getRectsFromTextBubbleDetectionModle(img, self.parent.dataManager
                                                       .confidenceThreshold))
        for box in boxes:
            rect = self.view.addRectByPoints(box[0])
            text = self.parent.modelHandler.cropAndGetTextFromNumpyImage(img, box[0])
            print("Xd")
            #translatedText = self.parent.modelHandler.translate(text)
            #print(f"Translated Text: {translatedText}")
            rect.setToolTip("Class: {} Confidence: {} Text: {}"
                            .format(box[1][0], box[1][1], text))


    def onSelectRect(self, rect):
        pass

    def updatePropertiesForRect(self, rect):
        pass

    def onLobbyDataLoaded(self, data):
        self.images.clear()
        files = os.listdir(data["project_directory"])
        for file in files:
            if "jpg" in file or "png" in file:
                self.images.addItem(ImageListItemWidget(os.path.basename(file),
                                                        os.path.join(
                                                            data["project_directory"],
                                                            file)))

    def closeEvent(self, a0):
        super().closeEvent(a0)

class ProjectConfigPage(WindowPage):

    def __init__(self, parent):
        super().__init__(parent)

        self.mainLayout = QVBoxLayout()

        self.addConfigurationWidgets()

        self.saveAndExit = QPushButton("Save And Exit")
        self.saveAndExit.clicked.connect(self.toSaveAndExit)

        self.mainLayout.addWidget(self.saveAndExit)

        self.setLayout(self.mainLayout)

    def addConfigurationWidgets(self):

        self.textBubbleDetectionModelLayout = QHBoxLayout()
        self.textBubbleDetectionModelLabel = QLabel("Text Bubble Detection Model")
        self.textBubbleDetectionModelField = QLineEdit()
        self.picktextBubbleDetectionModel = QPushButton("Pick")

        self.picktextBubbleDetectionModel.clicked.connect(self.toPickTextBubbleDetectionModel)

        self.textBubbleDetectionModelLayout.addWidget(self.textBubbleDetectionModelLabel)
        self.textBubbleDetectionModelLayout.addWidget(self.textBubbleDetectionModelField)
        self.textBubbleDetectionModelLayout.addWidget(self.picktextBubbleDetectionModel)

        self.mainLayout.addLayout(self.textBubbleDetectionModelLayout)

        self.confidenceLayout = QHBoxLayout()

        self.confidenceLayout.addWidget(QLabel("Confidence Threshold: "))

        self.confidence = QLineEdit()
        self.confidenceLayout.addWidget(self.confidence)

        self.mainLayout.addLayout(self.confidenceLayout)

    def toPickTextBubbleDetectionModel(self):
        result = QtWidgets.QFileDialog.getOpenFileName()
        model = str(result[0])
        if model != "" and model is not None:
            self.textBubbleDetectionModelField.setText(model)
            self.parent.getDataManager().setTextBubbleDetectionModelPath(model)

    def toSaveAndExit(self):
        self.nextWindow()
        modelPath = self.parent.getDataManager().textBubbleDetectionModelPath
        if modelPath != "":
            self.parent.modelHandler.loadTextBubbleDetectionModel(modelPath)
        self.parent.getDataManager().setConfidenceThreshold(float(self.confidence.text()))
        self.parent.getDataManager().saveData()
        self.parent.getDataManager().loadData()

    def onLobbyDataLoaded(self, data):
        if "text_bubble_detection_model_path" in data:
            self.textBubbleDetectionModelField.setText(data["text_bubble_detection_model_path"])
        if "confidence_threshold" in data:
            self.confidence.setText(str(data["confidence_threshold"]))

    def closeEvent(self, a0):
        super().closeEvent(a0)

class MainWindow(QMainWindow):
    loadDataSignal = pyqtSignal(DataManager)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.pages = [MainWorkspacePage(self), ProjectConfigPage(self)]

        self.createActions()
        self.addMenuBar()

        self.modelHandler = ModelHandler()

        self.dataManager = DataManager()
        self.dataManager.initFiles()
        self.dataManager.onLoadLobbyData.connect(self.onDataLoaded)
        self.dataManager.loadData()

        self.loadDataSignal.connect(self.dataManager.loadData)

        self.stackedWidgets = QStackedWidget()

        for page in self.pages:
            self.stackedWidgets.addWidget(page)

        """self.centralWidget = QWidget(self)

        self.layoutWidget = QWidget(self.centralWidget)
        self.layoutWidget.setFixedSize(QtWidgets.QApplication.primaryScreen().size().width(),
                                       QtWidgets.QApplication.primaryScreen().size().height() - 100)
        self.centralLayout = QHBoxLayout(self.layoutWidget)
        self.centralLayout.stretch(1)

        self.view = ImageViewer(self)
        self.view.selectedRectSignal.connect(self.onSelectRect)
        self.view.rectTransformed.connect(self.updatePropertiesForRect)
        self.loadDataSignal.connect(self.dataManager.loadData)

        srcDir = "D:\\Coding\\Python\\MangaDownloader\\MangaDownloader\\images"

        self.view.load_image({f"{srcDir}\\185.jpg": {}})
        self.view.fitToWindow()

        self.centralLayout.addWidget(self.view)

        self.tabs.tab1 = self.centralWidget"""

        self.setCentralWidget(self.stackedWidgets)
        #self.setCentralWidget(self.centralWidget)

        self.resize(640, 380)

    # Gui

    def createActions(self):
        self.openAct = QtWidgets.QAction(
            "&Open...", self, shortcut="Ctrl+O", triggered=self.open
        )
        self.configurationAct = QtWidgets.QAction(
            "&Configuration...", self, triggered=self.openConfigurationPage
        )

    def addMenuBar(self):
        self.fileMenu = QtWidgets.QMenu(self.tr("&File"), self)
        self.fileMenu.addAction(self.openAct)
        self.viewMenu = QtWidgets.QMenu(self.tr("&View"), self)
        self.editMenu = QtWidgets.QMenu(self.tr("&Edit"), self)
        self.editMenu.addAction(self.configurationAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.editMenu)

    def open(self):
        projectDir = str(QtWidgets.QFileDialog.getExistingDirectory(self,
                                                              "Select Directory"))
        self.dataManager.setProjectDirectory(projectDir)

    def openConfigurationPage(self):
        self.stackedWidgets.setCurrentWidget(self.pages[1])

    def getDataManager(self) -> DataManager:
        return self.dataManager

    # Events

    def closeEvent(self, a0):
        for page in self.pages:
            page.closeEvent(a0)
        self.dataManager.saveData()
        super().closeEvent(a0)

    def onDataLoaded(self, data):
        self.modelHandler.onLoadLobbyData(data)
        for page in self.pages:
            page.onLobbyDataLoaded(data)

    # Misc

    def nextPage(self):
        currentIndex = self.stackedWidgets.currentIndex() + 1

        if currentIndex > len(self.pages) - 1:
            currentIndex = 0
        self.stackedWidgets.setCurrentIndex(currentIndex)

    def prevPage(self):
        currentIndex = self.stackedWidgets.currentIndex() - 1

        if currentIndex < 0:
            currentIndex = len(self.pages) - 1
        self.stackedWidgets.setCurrentIndex(currentIndex)