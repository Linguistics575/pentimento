#!/bin/sh

#Do OCR on chapter 1 of Sandwith (pg 17-27)
#This takes a few minutes

for i in `seq 17 27`
do
    convert -density 200 pdfs/sandwith-$i.pdf -depth 8 -strip -background white -alpha off chapter1/sandwith$i-200.tiff
    convert -density 500 pdfs/sandwith-$i.pdf -depth 8 -strip -background white -alpha off chapter1/sandwith$i-500.tiff
    python3 do_ocr.py chapter1/sandwith$i-500.tiff > chapter1/sandwith$i-500.txt
    python3 do_ocr.py chapter1/sandwith$i-200.tiff > chapter1/sandwith$i-200.txt
done
