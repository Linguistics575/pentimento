#!/bin/sh

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
