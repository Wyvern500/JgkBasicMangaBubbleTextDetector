from PyQt5.QtCore import Qt, QPointF, QRect, QSizeF, QRectF, QSize
from PyQt5.QtGui import QPen, QColor, QBrush, QPainter, QImage, QPixmap
from PyQt5.QtWidgets import (QGraphicsRectItem, QGraphicsItem,
                             QGraphicsPixmapItem, QGraphicsTextItem)


class TextItem(QGraphicsTextItem):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.offset = QPointF()
        self.mouse_delta = QPointF()
        self.selected_edge = None
        self.borderWidth = 2
        self.size = QSizeF(100, 100)
        #self.setScale(20)
        #self.document().setPageSize(QSizeF(100, 100))

    """def paint(self, painter, option, widget):

        print("-2")

        painter.save()

        print("-1")

        doc = self.document().clone()

        print("0")

        background = QPixmap(int(self.size.width()), int(self.size.height()))

        print("1")

        backgroundPainter = QPainter(background)

        background.fill(Qt.GlobalColor.transparent)

        backgroundPainter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        print("2")

        layout = HorizontalTextDocumentLayout(doc)

        doc.setPlainText("Hola que pedo")
        doc.drawContents(backgroundPainter)

        print("3")

        rect = QRectF(self.pos(), self.size)
        source = QRectF(QPointF(0, 0), self.size)

        print("4")

        painter.drawPixmap(rect, background, source)

        print("5")

        backgroundPainter.end()

        painter.restore()

        print("6")

        super().paint(painter, option, widget)

        print("7")

    def rect(self):
        return QRectF(int(self.pos().x()), int(self.pos().y()), int(self.document().size()
                     .width()), int(self.document().size().height()))

    def setRect(self, rect: QRectF):
        print("0")
        self.setPos(rect.x(), rect.y())
        print("1")
        self.document().setPageSize(rect.size())
        print("2")

    def getEdges(self, pos):
        # return a proper Qt.Edges flag that reflects the possible edge(s) at
        # the given position; note that this only works properly as long as the
        # shape() override is consistent and for *pure* rectangle items; if you
        # are using other shapes (like QGraphicsEllipseItem) or items that have
        # a different boundingRect or different implementation of shape(), the
        # result might be unexpected.
        # Finally, a simple edges = 0 could suffice, but considering the new
        # support for Enums in PyQt6, it's usually better to use the empty flag
        # as default value.

        print("Xd1")

        edges = Qt.Edges()

        print("Xd2")

        rect = self.rect()

        print(f"Xd3 rect: {str(rect)}")

        border = self.borderWidth

        print(f"rectX: {rect.x()} rectY: {rect.y()} rectWidth: {rect.width()} rectHeight: {rect.height()} mouseX: {pos.x()} mosueY: {pos.y()}")

        if pos.x() < rect.x() + border:
            edges |= Qt.LeftEdge
        elif pos.x() > rect.right() - border:
            edges |= Qt.RightEdge
        if pos.y() < rect.y() + border:
            edges |= Qt.TopEdge
        elif pos.y() > rect.bottom() - border:
            edges |= Qt.BottomEdge

        return edges"""

    """def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected_edge = self.getEdges(event.pos())
            self.offset = QPointF()
        else:
            self.selected_edge = Qt.Edges()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if self.selected_edge:
            mouse_delta = event.pos() - event.buttonDownPos(Qt.LeftButton)
            # print(f"MouseDelta: {mouse_delta}")

            rect = self.rect()
            pos_delta = QPointF()
            border = self.borderWidth

            if self.selected_edge & Qt.LeftEdge:
                print("Left")
                # ensure that the width is *always* positive, otherwise limit
                # both the delta position and width, based on the border size
                diff = min(mouse_delta.x() - self.offset.x(), rect.width() - border)
                if rect.x() < 0:
                    offset = diff / 2
                    self.offset.setX(self.offset.x() + offset)
                    pos_delta.setX(offset)
                    rect.adjust(offset, 0, -offset, 0)
                else:
                    pos_delta.setX(diff)
                    rect.setWidth(rect.width() - diff)
            elif self.selected_edge & Qt.RightEdge:
                print("Right")
                if rect.x() < 0:
                    print("x0")
                    diff = max(mouse_delta.x() - self.offset.x(), border - rect.width())
                    print("x1")
                    offset = diff / 2
                    print("x2")
                    self.offset.setX(self.offset.x() + offset)
                    print("x3")
                    pos_delta.setX(offset)
                    print("x4")
                    rect.adjust(-offset, 0, offset, 0)
                    print("x5")
                else:
                    print("x6")
                    rect.setWidth(int(max(border, event.pos().x() - rect.x())))
                    print("x7")

            if self.selected_edge & Qt.TopEdge:
                print("Top")
                # similarly to what done for LeftEdge, but for the height
                diff = min(mouse_delta.y() - self.offset.y(), rect.height() - border)
                if rect.y() < 0:
                    offset = diff / 2
                    self.offset.setY(self.offset.y() + offset)
                    pos_delta.setY(offset)
                    rect.adjust(0, offset, 0, -offset)
                else:
                    pos_delta.setY(diff)
                    rect.setHeight(rect.height() - diff)
            elif self.selected_edge & Qt.BottomEdge:
                print("Bottom")
                if rect.y() < 0:
                    diff = max(mouse_delta.y() - self.offset.y(), border - rect.height())
                    offset = diff / 2
                    self.offset.setY(self.offset.y() + offset)
                    pos_delta.setY(offset)
                    rect.adjust(0, -offset, 0, offset)
                else:
                    rect.setHeight(max(border, event.pos().y() - rect.y()))
            print("Hello")
            if rect != self.rect():
                self.setRect(rect)
                if pos_delta:
                    self.setPos(self.pos() + pos_delta)
        else:
            # use the default implementation for ItemIsMovable
            super().mouseMoveEvent(event)

            if self.pos().x() <= 0:
                self.setX(0)

            if self.pos().y() <= 0:
                self.setY(0)

        self.mouse_delta = event.pos() - event.buttonDownPos(Qt.LeftButton)
        #self.parent.updatePropertiesForRect(self)
        # print(f"MouseDelta: {self.mouse_delta}")

    def mouseReleaseEvent(self, event):
        self.selected_edge = Qt.Edges()
        if event.button() == Qt.LeftButton:
            #if self.mouse_delta.isNull():
                #self.parent.processClickedItem(self)
            self.mouse_delta = QPointF()
        super().mouseReleaseEvent(event)

    def hoverMoveEvent(self, event):
        print("Hello0")
        edges = self.getEdges(event.pos())
        print("Hello1")
        if not edges:
            self.unsetCursor()
        elif edges in (Qt.TopEdge | Qt.LeftEdge, Qt.BottomEdge | Qt.RightEdge):
            self.setCursor(Qt.SizeFDiagCursor)
        elif edges in (Qt.BottomEdge | Qt.LeftEdge, Qt.TopEdge | Qt.RightEdge):
            self.setCursor(Qt.SizeBDiagCursor)
        elif edges in (Qt.LeftEdge, Qt.RightEdge):
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.setCursor(Qt.SizeVerCursor)"""


class RectMarker(QGraphicsRectItem):
    selected_edge = None

    def __init__(self, x, y, width, height, onCenter=False):

        if onCenter:
            super().__init__(-width / 2, -height / 2, width, height)
        else:
            super().__init__(0, 0, width, height)

        self.mouse_delta: QPointF = QPointF()
        import ImageViewer
        self.parent: ImageViewer.ImageViewer = None
        self.setPos(x, y)
        self.setFlags(QGraphicsItem.ItemIsMovable)
        self.setAcceptHoverEvents(True)
        self.setPen(QPen(QColor(255, 0, 0, 100), 5))
        self.setBrush(QBrush(QColor(0, 255, 0, 100)))

    def setParent(self, parent):
        self.parent = parent
        return self

    def getEdges(self, pos):
        # return a proper Qt.Edges flag that reflects the possible edge(s) at
        # the given position; note that this only works properly as long as the
        # shape() override is consistent and for *pure* rectangle items; if you
        # are using other shapes (like QGraphicsEllipseItem) or items that have
        # a different boundingRect or different implementation of shape(), the
        # result might be unexpected.
        # Finally, a simple edges = 0 could suffice, but considering the new
        # support for Enums in PyQt6, it's usually better to use the empty flag
        # as default value.

        edges = Qt.Edges()
        rect = self.rect()
        border = self.pen().width() * 2

        if pos.x() < rect.x() + border:
            edges |= Qt.LeftEdge
        elif pos.x() > rect.right() - border:
            edges |= Qt.RightEdge
        if pos.y() < rect.y() + border:
            edges |= Qt.TopEdge
        elif pos.y() > rect.bottom() - border:
            edges |= Qt.BottomEdge

        return edges

    def selected(self):
        self.setPen(QPen(QColor(255, 255, 255, 100), 5))

    def unselected(self):
        self.setPen(QPen(QColor(255, 0, 0, 100), 5))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent.setHoveredItem(self)
            self.selected_edge = self.getEdges(event.pos())
            self.offset = QPointF()
        else:
            self.selected_edge = Qt.Edges()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if self.selected_edge:
            mouse_delta = event.pos() - event.buttonDownPos(Qt.LeftButton)
            # print(f"MouseDelta: {mouse_delta}")

            rect = self.rect()
            pos_delta = QPointF()
            border = self.pen().width()

            if self.selected_edge & Qt.LeftEdge:
                # ensure that the width is *always* positive, otherwise limit
                # both the delta position and width, based on the border size
                diff = min(mouse_delta.x() - self.offset.x(), rect.width() - border)
                if rect.x() < 0:
                    offset = diff / 2
                    self.offset.setX(self.offset.x() + offset)
                    pos_delta.setX(offset)
                    rect.adjust(offset, 0, -offset, 0)
                else:
                    pos_delta.setX(diff)
                    rect.setWidth(rect.width() - diff)
            elif self.selected_edge & Qt.RightEdge:
                if rect.x() < 0:
                    diff = max(mouse_delta.x() - self.offset.x(), border - rect.width())
                    offset = diff / 2
                    self.offset.setX(self.offset.x() + offset)
                    pos_delta.setX(offset)
                    rect.adjust(-offset, 0, offset, 0)
                else:
                    rect.setWidth(max(border, event.pos().x() - rect.x()))

            if self.selected_edge & Qt.TopEdge:
                # similarly to what done for LeftEdge, but for the height
                diff = min(mouse_delta.y() - self.offset.y(), rect.height() - border)
                if rect.y() < 0:
                    offset = diff / 2
                    self.offset.setY(self.offset.y() + offset)
                    pos_delta.setY(offset)
                    rect.adjust(0, offset, 0, -offset)
                else:
                    pos_delta.setY(diff)
                    rect.setHeight(rect.height() - diff)
            elif self.selected_edge & Qt.BottomEdge:
                if rect.y() < 0:
                    diff = max(mouse_delta.y() - self.offset.y(), border - rect.height())
                    offset = diff / 2
                    self.offset.setY(self.offset.y() + offset)
                    pos_delta.setY(offset)
                    rect.adjust(0, -offset, 0, offset)
                else:
                    rect.setHeight(max(border, event.pos().y() - rect.y()))

            if rect != self.rect():
                self.setRect(rect)
                if pos_delta:
                    self.setPos(self.pos() + pos_delta)
        else:
            # use the default implementation for ItemIsMovable
            super().mouseMoveEvent(event)

            if self.pos().x() <= 0:
                self.setX(0)

            if self.pos().y() <= 0:
                self.setY(0)

        self.mouse_delta = event.pos() - event.buttonDownPos(Qt.LeftButton)
        self.parent.updatePropertiesForRect(self)
        # print(f"MouseDelta: {self.mouse_delta}")

    def mouseReleaseEvent(self, event):
        self.selected_edge = Qt.Edges()
        if event.button() == Qt.LeftButton:
            if self.mouse_delta.isNull():
                self.parent.processClickedItem(self)
            self.mouse_delta = QPointF()
        super().mouseReleaseEvent(event)

    def hoverMoveEvent(self, event):
        edges = self.getEdges(event.pos())
        if not edges:
            self.unsetCursor()
        elif edges in (Qt.TopEdge | Qt.LeftEdge, Qt.BottomEdge | Qt.RightEdge):
            self.setCursor(Qt.SizeFDiagCursor)
        elif edges in (Qt.BottomEdge | Qt.LeftEdge, Qt.TopEdge | Qt.RightEdge):
            self.setCursor(Qt.SizeBDiagCursor)
        elif edges in (Qt.LeftEdge, Qt.RightEdge):
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.setCursor(Qt.SizeVerCursor)


class PreviewRect(QGraphicsRectItem):

    def __int__(self, x, y, width, height):
        super().__init__(0, 0, width, height)
        self.setPos(x, y)
        self.setPen(QPen(QColor(255, 0, 0, 100), 2))
        self.setBrush(QBrush(QColor(255, 255, 0, 100)))

    def updateGeometry(self, x, y, w, h):
        self.setRect(x, y, w, h)
