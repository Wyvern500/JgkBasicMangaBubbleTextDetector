from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

"""
# Open the image
img = Image.open('inpainted.png')

text = "Sample Text"
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("ldfcomicsans-font/Ldfcomicsans-jj7l.ttf", 16)
rect = (0, 0, 100, 30)
print(font.getbbox(text))
# draw.text((x, y),"Sample Text",(r,g,b))
draw.rectangle(rect, outline="red")
draw.text((0, 0), text,(200, 0, 0),font=font)
img.show()"""

from translate import Translator

def translate_text(text, src_lang="en", dest_lang="es"):
    translator = Translator(from_lang=src_lang, to_lang=dest_lang)
    return translator.translate(text)

if __name__ == "__main__":
    text = "Hello, world!"
    from_lang = "en"
    to_lang = "es"

    try:
        translated_text = translate_text(text, from_lang, to_lang)
        print("Translated text:", translated_text)
    except Exception as e:
        print("An error occurred:", e)