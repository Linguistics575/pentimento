Dependencies:
tesseract-ocr libtesseract-dev libleptonica-dev (apt-get install tesseract-ocr libtesseract-dev libleptonica-dev)
tesserocr (pip install tesserocr)
imagemagick (to convert pdf to tiff)
pdfseparate (to split pdfs into individual pages, but this isn't part of any script yet)

Structure of this directory:
chapter1.sh:
    do OCR on chapter 1 of Sandwith
do_ocr.py:
    takes image file(s) as command line arg, and outputs UTF-8 text
pdfs/:
    input pdf files
chapter1/:
    All data processed for chapter1 of sandwith
        *.tiff: pdfs converted to tiff format
        sandwith*.txt: output of OCR
        merge*.txt: Manually merged output of OCR. Created by doing diff of outputs and then selecting the best alternative
        gold*.txt: Gold standard of chapter 1 output (merge file that has been proofread). I think it is correct, but please correct any errors :)
