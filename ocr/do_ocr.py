from tesserocr import PyTessBaseAPI, OEM
import sys

images = sys.argv[1:]

with PyTessBaseAPI(oem=OEM.TESSERACT_CUBE_COMBINED) as api:
    for img in images:
        api.SetImageFile(img)
        print(api.GetUTF8Text())
