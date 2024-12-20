import copy
from typing import List

import cv2
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QPointF, QTimer, QRect, pyqtSignal

import json, numpy as np

from PyQt5.QtGui import QPainter, QTransform
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsItem

from RectWidgets import RectMarker, TextItem
from RectWidgets import PreviewRect

class ImageData:

    def __init__(self, pixmap, img):
        self.pixmap: QGraphicsPixmapItem = pixmap
        self.img = img
        self.rects: List[RectMarker] = []

class ImageViewer(QtWidgets.QGraphicsView):
    factor = 1.3
    selectedRectSignal = pyqtSignal(RectMarker)
    rectTransformed = pyqtSignal(RectMarker)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main stuff
        import main
        self.parent: main.MainWindow = parent
        self.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform
        )
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.setBackgroundRole(QtGui.QPalette.Dark)

        # Misc Stuff
        self.rectsData = {}

        self.currentImageData = None
        self.selectedRects = []
        self.rectHovered = None
        self.point1: QPointF = None
        self.point2: QPointF = None

        self.canAddSelection = True
        self.ctrl = False

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)

        # Widgets stuff
        scene = QtWidgets.QGraphicsScene()
        scene.setParent(self)
        self.setScene(scene)

        self._pixmap_item = QtWidgets.QGraphicsPixmapItem()
        scene.addItem(self._pixmap_item)

        self.textItem = TextItem()
        scene.addItem(self.textItem)

        self.previewRect: PreviewRect = None
        self.setFocus()

    def render(self, painter, target = ..., source = ..., mode = ...):
        print("Render")
        super().render(painter, target, source, mode)

    def repaint(self):
        print("Repaing")
        super().repaint()

    def paintEngine(self):
        print("paintEngine")
        super().paintEngine()

    def paintEvent(self, event):
        print("paintEvent")
        super().paintEvent(event)

    def update(self):

        # Used for update the geometry of the preview rectangle
        if self.point1 and self.point2 and self.rectHovered is None and not self.ctrl:
            minx = min(self.point1.x(), self.point2.x())
            miny = min(self.point1.y(), self.point2.y())
            xmax = max(self.point1.x(), self.point2.x())
            ymax = max(self.point1.y(), self.point2.y())
            w = abs(xmax - minx)
            h = abs(ymax - miny)

            self.previewRect.update()
            self.previewRect.updateGeometry(minx, miny, w, h)

        super().update()

    def updatePropertiesForRect(self, rect: RectMarker):
        self.rectTransformed.emit(rect)

    def updateRectFromProperties(self, text):
        sender = self.sender()

        if sender.objectName() == "x":
            for rect in self.selectedRects:
                rect.setX(float(text))
        elif sender.objectName() == "y":
            for rect in self.selectedRects:
                rect.setY(float(text))
        elif sender.objectName() == "width":
            for rect in self.selectedRects:
                newRect = rect.rect()
                newRect.setWidth(float(text))
                rect.setRect(newRect)
        elif sender.objectName() == "height":
            for rect in self.selectedRects:
                newRect = rect.rect()
                newRect.setHeight(float(text))
                rect.setRect(newRect)

    def load_image(self, data):
        self.clearRects()
        fileName = list(data.keys())[0]
        pixmap = QtGui.QPixmap(fileName)
        if pixmap.isNull():
            return False
        self._pixmap_item.setPixmap(pixmap)
        self.setImageDataFor(pixmap, cv2.imread(fileName))
        self.addRectsFromData(data[fileName])
        return True

    def addRectsFromData(self, data):
        for rect in data:
            self.scene().addItem(RectMarker(rect["x"], rect["y"], rect["w"],
                                            rect["h"]).setParent(self))

    def getCurrentImageAsNumpyImage(self):
        return self.currentImageData.img

    def clearRects(self):
        for rect in self.getRects():
            self.scene().removeItem(rect)

    def addRectByWidthAndHeight(self, data):
        rect = RectMarker(data[0], data[1], data[2], data[3])
        rect.setParent(self)
        self.scene().addItem(rect)
        return rect

    def addRectByPoints(self, data):
        rect = RectMarker(data[0], data[1], data[2] - data[0], data[3] - data[1])
        rect.setParent(self)
        self.scene().addItem(rect)
        return rect

    def qt_image_to_array(self, img, share_memory=False):
        """ Creates a numpy array from a QImage.

            If share_memory is True, the numpy array and the QImage is shared.
            Be careful: make sure the numpy array is destroyed before the image,
            otherwise the array will point to unreserved memory!!
        """
        assert isinstance(img, QtGui.QImage), "img must be a QtGui.QImage object"
        assert img.format() == QtGui.QImage.Format.Format_RGB32, \
            "img format must be QImage.Format.Format_RGB32, got: {}".format(img.format())

        img_size = img.size()
        buffer = img.constBits()

        # Sanity check
        n_bits_buffer = len(buffer) * 8
        n_bits_image  = img_size.width() * img_size.height() * img.depth()
        assert n_bits_buffer == n_bits_image, \
            "size mismatch: {} != {}".format(n_bits_buffer, n_bits_image)

        assert img.depth() == 32, "unexpected image depth: {}".format(img.depth())

        # Note the different width height parameter order!
        arr = np.ndarray(shape  = (img_size.height(), img_size.width(), img.depth()//8),
                         buffer = buffer,
                         dtype  = np.uint8)

        if share_memory:
            return arr
        else:
            return copy.deepcopy(arr)

    def setImageDataFor(self, pixmap, img):
        self.currentImageData = ImageData(pixmap, img)

    def loadRectsData(self, data):
        with open(self.parent.dataManager.imageLabelingDataFile) as f:
            imageLabelingData = json.load(f)

    def getSerializedRects(self):
        rects = self.getRects()
        newRects = []
        for i in range(0, len(rects)):
            rect = rects[i]
            boundingRect = rect.boundingRect()
            newRects.append({"x": rect.x(), "y": rect.y(), "w": boundingRect
                            .width(), "h": boundingRect.height()})
        return newRects


    def getRects(self):
        rects = []
        for item in self.scene().items(Qt.DescendingOrder):
            if type(item) == RectMarker:
                rects.append(item)
        return rects

    def zoomIn(self):
        self.zoom(self.factor)

    def zoomOut(self):
        self.zoom(1 / self.factor)

    def zoom(self, f):
        self.scale(f, f)

    def resetZoom(self):
        self.resetTransform()

    def fitToWindow(self):
        self.fitInView(self.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def setHoveredItem(self, item):
        self.rectHovered = item

    def mousePressEvent(self, event):

        self.rectHovered = None

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        print(self.scene().selectedItems(), self.scene().itemAt(self.mapToScene(event.pos()), QTransform()))
        if len(self.scene().selectedItems()) == 0:
            self.canAddSelection = True
            if self.canAddSelection and not self.ctrl:
                if len(self.selectedRects) == 0 and self.rectHovered is None:
                    mousePos = self.mapToScene(event.pos())

                    # If the point one is null then give it a value
                    if self.point1 is None:
                        self.point1 = QPointF(mousePos.x(), mousePos.y())
                        self.previewRect = PreviewRect(mousePos.x(), mousePos.y(), 0, 0)
                        self.scene().addItem(self.previewRect)
                        self.timer.start(30)
                    else:
                        self.point2 = QPointF(mousePos.x(), mousePos.y())

                        # Add Selection

                        minx = min(self.point1.x(), self.point2.x())
                        miny = min(self.point1.y(), self.point2.y())
                        xmax = max(self.point1.x(), self.point2.x())
                        ymax = max(self.point1.y(), self.point2.y())
                        w = abs(xmax - minx)
                        h = abs(ymax - miny)

                        self.scene().addItem(RectMarker(minx, miny, w, h).setParent(self))

                        if not self._pixmap_item.pixmap().isNull():
                            image = self._pixmap_item.pixmap().size()
                            generalImageX = minx / image.width()
                            generalImageY = miny / image.height()
                            generalImageW = w / image.width()
                            generalImageH = h / image.height()

                            print(f"x: {generalImageX} y: {generalImageY} w: {generalImageW} h: {generalImageH}")

                        self.timer.stop()
                        self.scene().removeItem(self.previewRect)
                        self.previewRect = None
                        self.point1 = self.point2 = None
                elif self.point1:
                    mousePos = self.mapToScene(event.pos())

                    self.point2 = QPointF(mousePos.x(), mousePos.y())

                    # Add Selection

                    minx = min(self.point1.x(), self.point2.x())
                    miny = min(self.point1.y(), self.point2.y())
                    xmax = max(self.point1.x(), self.point2.x())
                    ymax = max(self.point1.y(), self.point2.y())
                    w = abs(xmax - minx)
                    h = abs(ymax - miny)

                    self.scene().addItem(RectMarker(minx, miny, w, h).setParent(self))

                    self.timer.stop()
                    self.scene().removeItem(self.previewRect)
                    self.previewRect = None
                    self.point1 = self.point2 = None"""

        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):

        self.point2 = self.mapToScene(event.pos())

        super().mouseMoveEvent(event)

    def wheelEvent(self, event):

        if self.ctrl:
            if event.angleDelta().y() > 0:
                self.zoomIn()
            else:
                self.zoomOut()

        super().wheelEvent(event)

    def processClickedItem(self, item: RectMarker):

        if not self.ctrl:
            # If it has not been selected yet
            if item not in self.selectedRects:
                # if there is a previous rect, remove it
                for rect in self.selectedRects:
                    rect.unselected()
                self.selectedRects.clear()
                # Adding the rect
                self.addItemToSelection(item)
                item.selected()
            else:
                self.selectedRects.clear()
                item.unselected()
        else:
            if item not in self.selectedRects:
                if len(self.selectedRects) != 0:
                    item.selected()
                self.addItemToSelection(item)
                item.selected()
            else:
                item.unselected()
                self.selectedRects.remove(item)

    def addItemToSelection(self, item: RectMarker):
        self.selectedRects.append(item)

        self.selectedRectSignal.emit(item)

    def keyPressEvent(self, event):

        # To remove selections
        if event.key() == Qt.Key_Delete:
            for rect in self.selectedRects:
                self.scene().removeItem(rect)
            self.selectedRects.clear()
        elif event.key() == Qt.Key_Control:
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
            self.ctrl = True
            self.canAddSelection = False
        #print(event.key())

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):

        if event.key() == Qt.Key_Control:
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
            self.ctrl = False

        super().keyReleaseEvent(event)