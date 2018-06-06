#!/bin/sh

# Usage: ./pdfToText.sh pathToInputPdf outputDirectory
# 
# Outputs:
#   pdfs/           input pdf separated into individual pages
#   tiffs/          input to OCR engine. Note: files in this directory are deleted after we're done with them, since they are really large
#   pngs/           pdfs/ converted to pngs. We use these for the user interface
#   raw_ocr/200/    OCR output text files where the parameter -density 200 is used.
#   raw_ocr/500/    OCR output text files where the parameter -density 500 is used.
#
# In every output directory, the naming convetion is [number].[extension]. For example: 1.txt, 2.txt, ... for directories with text files.
#
# In order to run this tool you need
#   * pdfseparate
#   * imagemagick (used for 'convert' command)
#   * tesserocr (python OCR library. To install: "pip install tesserocr")
#   * tesseract-ocr libtesseract-dev libleptonica-dev (dependencies of tesserocr. To install: "apt-get install tesseract-ocr libtesseract-dev libleptonica-dev")


mkdir -p "$2/pdfs"
mkdir -p "$2/pngs"
mkdir -p "$2/tiffs"
mkdir -p "$2/raw_ocr/200"
mkdir -p "$2/raw_ocr/500"

pdfseparate "$1" "$2/pdfs/%d.pdf"

pages=`ls "$2/pdfs/" | wc -l`

for i in `seq 1 $pages`
do
    convert -density 200 "$2/pdfs/$i.pdf" -depth 8 -strip -background white -alpha off "$2/tiffs/$i-200.tiff"
    convert -density 500 "$2/pdfs/$i.pdf" -depth 8 -strip -background white -alpha off "$2/tiffs/$i-500.tiff"
    convert -density 300 "$2/pdfs/$i.pdf" "$2/pngs/$i.png"
    python3 ocr/do_ocr.py "$2/tiffs/$i-500.tiff" > "$2/raw_ocr/500/$i.txt"
    python3 ocr/do_ocr.py "$2/tiffs/$i-200.tiff" > "$2/raw_ocr/200/$i.txt"
    rm "$2/tiffs/$i-200.tiff"
    rm "$2/tiffs/$i-500.tiff"
done
