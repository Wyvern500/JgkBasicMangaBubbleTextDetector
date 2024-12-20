from PyQt5.QtWidgets import QListWidgetItem

class ImageListItemWidget(QListWidgetItem):

    def __init__(self, text, imagePath):
        super().__init__(None)

        self.setText(text)
        self.setToolTip(imagePath)
