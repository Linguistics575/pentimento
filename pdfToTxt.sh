#!/bin/sh

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
