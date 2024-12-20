from PyQt5.QtCore import pyqtSignal, QObject

import os, json

class DataManager(QObject):
    onLoadLobbyData = pyqtSignal(dict)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.lobbyFile = "lobby.json"
        self.lobbyData = {}
        self.projectDirectory = None
        self.textBubbleDetectionModelPath = ""
        self.confidenceThreshold = 0.5

        self.outputDir = ""
        self.assetsDir = "{}assets".format(self.outputDir)
        self.dataDir = f"{self.assetsDir}/data"
        self.projectDataFile = f"{self.dataDir}/project_data.json"
        self.imagesDir = f"{self.assetsDir}/images"
        self.imageFolderLocationsFile = f"{self.dataDir}/image_folder_locations.json"
        self.imageFolderLocations = []
        self.imageLocations = []
        self.imageLabelingDataFile = f"{self.dataDir}/image_labeling_data_file.json"
        self.imageLabelingData = {}

    def setProjectDirectory(self, directory):
        self.projectDirectory = directory

    def setTextBubbleDetectionModelPath(self, modelPath):
        self.textBubbleDetectionModelPath = modelPath

    def setConfidenceThreshold(self, confidence):
        self.confidenceThreshold = confidence

    def reload(self):
        self.assetsDir = "{}/{}".format(self.outputDir, self.assetsDir)
        self.dataDir = f"{self.assetsDir}/data"
        self.imagesDir = f"{self.assetsDir}/images"
        self.projectDataFile = f"{self.dataDir}/project_data.json"
        self.imageFolderLocationsFile = f"{self.dataDir}/image_folder_locations.json"
        self.imageLabelingDataFile = f"{self.dataDir}/image_labeling_data_file.json"
        self.initFiles()

    def initFiles(self):
        self.createLobbyFile()
        """
        if not os.path.exists(self.assetsDir):
            os.makedirs(self.assetsDir)
        if not os.path.exists(self.dataDir):
            os.makedirs(self.dataDir)
        if not os.path.exists(self.imageFolderLocationsFile):
            file = open(self.imageFolderLocationsFile, "w")
            file.write("{}")
            file.close()
        if not os.path.exists(self.imageLabelingDataFile):
            file = open(self.imageLabelingDataFile, "w")
            file.write("{}")
            file.close()
        if not os.path.exists(self.projectDataFile):
            file = open(self.projectDataFile, "w")
            file.write("{}")
            file.close()"""

    def createLobbyFile(self):
        if not os.path.exists(self.lobbyFile):
            with open(self.lobbyFile, 'w') as f:
                json.dump({"project_directory": "",
                           "text_bubble_detection_model_path": "",
                           "confidence_threshold": ""}, f)

    def initAll(self):
        self.initFiles()
        #self.loadImageLocations()

    def loadData(self):
        if os.path.exists(self.imageFolderLocationsFile):
            with open(self.imageLabelingDataFile) as f:
                self.imageLabelingData = json.load(f)
        if os.path.exists(self.lobbyFile):
            with open(self.lobbyFile) as f:
                self.lobbyData = json.load(f)
                self.projectDirectory = self.lobbyData["project_directory"]
                if "text_bubble_detection_model_path" in self.lobbyData:
                    self.textBubbleDetectionModelPath = self.lobbyData["text_bubble_detection_model_path"]
                if "confidence_threshold" in self.lobbyData:
                    self.confidenceThreshold = float(self.lobbyData["confidence_threshold"])
                self.onLoadLobbyData.emit(self.lobbyData)

    def loadImageLocations(self):
        with open(self.imageFolderLocationsFile) as f:
            imageFolderLocations = json.load(f)
            print(imageFolderLocations)
            self.imageFolderLocations = imageFolderLocations["imageFolderLocations"]

        for imageFolderLocation in self.imageFolderLocations:
            files = os.listdir(imageFolderLocation)
            for f in files:
                if os.path.isfile(os.path.join(imageFolderLocation, f)):
                    if "jpg" in os.path.splitext(f)[1]:
                        self.imageLocations.append(os.path.join(imageFolderLocation, f))

    def saveData(self):
        self.saveLobbyData()
        #self.saveProjectData()
        #self.saveImageLocations()
        #self.saveLabelingData()

    def saveLobbyData(self):
        if self.projectDirectory is not None:
            data = {"project_directory": self.projectDirectory,
                    "text_bubble_detection_model_path": self.textBubbleDetectionModelPath,
                    "confidence_threshold": self.confidenceThreshold}
            with open(self.lobbyFile, "w") as f:
                json.dump(data, f)

    def saveProjectData(self):
        data = {"output_dir": self.outputDir}

        with open(self.projectDataFile, "w") as f:
            json.dump(data, f)

    def saveImageLocations(self):
        data = {"imageFolderLocations": self.imageFolderLocations}

        with open(self.imageFolderLocationsFile, "w") as f:
            json.dump(data, f)

    def saveLabelingData(self):
        with open(self.imageLabelingDataFile, "w") as f:
            json.dump(self.imageLabelingData, f)

    def saveForItem(self, item, serializedData):
        if self.imageLabelingData is not None:
            self.imageLabelingData[item.toolTip()] = serializedData
        with open(self.imageFolderLocationsFile, "w") as f:
            json.dump(self.imageLabelingData, f)

    def getRectsDataForItem(self, item):
        if item.toolTip() in self.imageLabelingData:
            return self.imageLabelingData[item.toolTip()]
        else:
            return {}