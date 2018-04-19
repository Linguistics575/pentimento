__author__ = 'eslamelsawy'

import pytesseract
from PIL import Image, ImageEnhance, ImageOps

def main():

    input_image = '1.tif'
    output_image = '1_enhanced.tif'

    im = Image.open(input_image)

    # increase contrast
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(4)

    # remove noise
    im = im.point(lambda i: i < 150 and 255)
    im = ImageOps.invert(im)

    # save
    im.save(output_image)

    # ocr
    text = pytesseract.image_to_string(Image.open(output_image))
    print(text)

if __name__ == "__main__":
    main()