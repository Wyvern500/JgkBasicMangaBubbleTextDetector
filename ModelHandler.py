import cv2
import translate.providers
from ultralytics import YOLO
from PIL import Image
from manga_ocr import MangaOcr
from translate import Translator
from translate.providers import LibreProvider

class ModelHandler:

    def __init__(self):
        self.textBubbleDetectionModel = None
        self.mangaOcr = None
        self.translator = None
        self.mangaOcr = MangaOcr()
        """self.translator = LibreProvider(from_lang="ja", to_lang="en",
                                        base_url="https://translate.astian.org/",
                                         secret_access_key=None)"""

    def loadTextBubbleDetectionModel(self, path):
        self.textBubbleDetectionModel = YOLO(path)
        print("Model Loaded")

    def getTextBubbleDetectionModel(self):
        return self.textBubbleDetectionModel

    def getMangaOcr(self):
        return self.mangaOcr

    def translate(self, text):
        return self.translator.get_translation(text)

    def onLoadLobbyData(self, data):
        if "text_bubble_detection_model_path" in data:
            self.loadTextBubbleDetectionModel(data["text_bubble_detection_model_path"])

    def getTextFromPILImage(self, img):
        return self.mangaOcr(img)

    def cropAndGetTextFromNumpyImage(self, img, data):
        img = Image.fromarray(img[data[1]:data[3], data[0]:data[2]].astype('uint8'),
                              'RGB')
        return self.mangaOcr(img)

    def getTextFromNumpyImage(self, img):
        img = Image.fromarray(img.astype('uint8'), 'RGB')
        return self.mangaOcr(img)

    def getRect(self, box, originalSize, inputImageSize=(640, 640)):
        minX = int((box[0].item() / inputImageSize[0]) * originalSize[1])
        minY = int((box[1].item() / inputImageSize[1]) * originalSize[0])
        maxX = int((box[2].item() / inputImageSize[0]) * originalSize[1])
        maxY = int((box[3].item() / inputImageSize[1]) * originalSize[0])
        return minX, minY, maxX, maxY

    def getRectsFromTextBubbleDetectionModle(self, img, confidenceThreshold):
        rects = []

        if self.textBubbleDetectionModel is not None:
            results = self.textBubbleDetectionModel.predict(cv2.resize(img,
                                                                       (640, 640), cv2.INTER_LINEAR))
            for r in results:

                boxes = r.boxes
                for box in boxes:
                    b = box.xyxy[0]
                    x1, y1, x2, y2 = self.getRect(b, img.shape)
                    conf = box.conf[0].item()
                    cls = box.cls[0].item()
                    if conf > confidenceThreshold:
                        rects.append(((x1, y1, x2, y2), (cls, conf)))
        return rects
