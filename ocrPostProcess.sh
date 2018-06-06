#!/bin/sh
            
# Usage: ./pdfToText.sh pathToInputPdf dataDirectory
#
# dataDirectory should have data in the format as outputted by ./pdfToText.sh
# 
# Outputs:
#   normalized_ocr/ directory of text files, same structure as raw_ocr, containing output of ocr/normalize.py
#   merged_ocr/     directory of text and html files, result of ocr/merge.py run on normalized_ocr/ files. This will take n-1 steps, where n in the number of subdirectories of normalized_ocr. The step with the largest number is the final output. These files can be imported into the pentimenti.github.io tool
#
# In every output directory, the naming convetion is [number].[extension]. For example: 1.txt, 2.txt, ... for directories with text files.
#
# In order to run this tool you need
#   * nltk


for dir in `ls "$1/raw_ocr"`
do
    mkdir -p "$1/normalized_ocr/$dir"
    for file in `ls "$1/raw_ocr/$dir"`
    do
        echo $file
        ./ocr/normalize.py < "$1/raw_ocr/$dir/$file" > "$1/normalized_ocr/$dir/$file"
    done
done

first=""
second=""
step=1
for dir in `ls "$1/normalized_ocr/"`
do
    if [ "$first" == "" ]; then
        echo "first"
        echo $dir
        first="$1/normalized_ocr/$dir"
    else
        echo "second"
        echo $dir
        second="$1/normalized_ocr/$dir"
        out="$1/merged_ocr/step$step-html/"
        mkdir -p "$out"
        ./ocr/merge.py "$first" "$second" "$out" hc
        second="$1/normalized_ocr/$dir"
        out="$1/merged_ocr/step$step-txt/"
        mkdir -p "$out"
        ./ocr/merge.py "$first" "$second" "$out"
        first=$out
        step=$((step+1))
    fi
done
