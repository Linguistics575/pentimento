__author__ = 'eslamelsawy'

import os
import pytesseract
from PIL import Image, ImageEnhance, ImageOps

def main():
    input_dir = 'input/'
    for file in os.listdir(input_dir):

        if file.startswith("."):
            continue

        # open image
        im = Image.open(input_dir + file)

        # save original
        filename = os.path.splitext(file)[0]
        print('processing:' + filename)
        extension = os.path.splitext(file)[1]
        output_dir = 'output/' + filename + "/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        im.save(output_dir + "1_original" + extension)

        # increase contrast
        enhancer = ImageEnhance.Contrast(im)
        im = enhancer.enhance(4)

        # remove noise
        im = im.point(lambda i: i < 150 and 255)
        im = ImageOps.invert(im)
        im.save(output_dir + "2_enhanced" + extension, dpi=(600, 600))

        # cropping
        width, height = im.size
        margin_top = 100
        margin_bottom = 100
        margin_left = 800
        margin_right = 200
        left_upper_x = margin_left
        left_upper_y = margin_top
        right_lower_x = width - margin_right
        right_lower_y = height - margin_bottom
        im = im.crop((left_upper_x, left_upper_y, right_lower_x, right_lower_y))
        im.save(output_dir + "3_cropped" + extension, dpi=(600, 600))

        # resizing
        basewidth = 2000
        wpercent = (basewidth / float(im.size[0]))
        hsize = int((float(im.size[1]) * float(wpercent)))
        im = im.resize((basewidth, hsize), Image.ANTIALIAS)
        im.save(output_dir + "4_resized" + extension, dpi=(600, 600))

        # ocr
        text = pytesseract.image_to_string(Image.open(output_dir + "4_resized" + extension))
        with open(output_dir + "5_ocr.txt", 'w') as the_file:
            the_file.write(text)


if __name__ == "__main__":
    main()