import os.path
import sys

import cv2
from ultralytics import YOLO
import torch

# Cargar el checkpoint
#checkpoint = torch.load("D:\\Downloads\\modelos\\comictextdetector.pt")

# Verificar las claves del checkpoint
#print(checkpoint.keys())

#model = YOLO("D:\\Downloads\\modelos\\comictextdetector.pt")


from simple_lama_inpainting import SimpleLama
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

from ModelHandler import ModelHandler

def showImage(img):
    plt.imshow(img)
    plt.axis('off')  # Desactivar los ejes
    plt.show()

modelsHandler = ModelHandler()

modelsHandler.loadTextBubbleDetectionModel("D:\\Downloads\\modelos\\SecondFineTunning\\best last.pt")

img_path = "D:\\Coding\\Python\\MangaDownloader\\MangaDownloader\\images\\mangaPage5.jpg"

img = cv2.imread(img_path)
mask = np.zeros(img.shape, dtype=np.uint8)

rects = modelsHandler.getRectsFromTextBubbleDetectionModle(img, 0.5)

for rect in rects:

    xyxy = rect[0]
    mask[xyxy[1]:xyxy[3], xyxy[0]:xyxy[2]] = 255

cv2.imwrite("mask.jpg", mask)

print(rects)

simple_lama = SimpleLama()

image = Image.open(img_path)
mask = Image.fromarray(mask).convert('L')

result = simple_lama(image, mask)
result.save("inpainted.png")






"""
import psutil
import platform
import cpuinfo

def get_system_info():
    # Obtener información de la RAM
    ram = psutil.virtual_memory()
    total_ram = ram.total / (1024 ** 3)  # Convertir a GB

    # Obtener información del almacenamiento
    disk = psutil.disk_usage('/')
    total_disk = disk.total / (1024 ** 3)  # Convertir a GB

    # Obtener información del procesador
    processor_info = cpuinfo.get_cpu_info()

    return total_ram, total_disk, processor_info

def main():
    total_ram, total_disk, processor_info = get_system_info()

    print(f"Total RAM: {total_ram:.2f} GB")
    print(f"Total Disk Space: {total_disk:.2f} GB")
    print(f"Processor: {processor_info['brand_raw']}")

if __name__ == "__main__":
    main()"""




sys.path.insert(1, "comic_text_detector")
from inference import model2annotations

# comic_text_detector/

print(os.path.exists(r'D:\Coding\Python\JgkMangaTranslator\JgkMangaTranslator\comic_text_detector\data\comictextdetector.pt'))

model_path = r'D:\Coding\Python\JgkMangaTranslator\JgkMangaTranslator\comic_text_detector\data\/comictextdetector.pt'
img_dir = r'D:\Coding\Python\JgkMangaTranslator\JgkMangaTranslator\comic_text_detector\data\/examples'
save_dir = r'D:\Coding\Python\JgkMangaTranslator\JgkMangaTranslator\comic_text_detector\data\/examples/annotations'

model2annotations(model_path, img_dir, save_dir, save_json=False)