#!/bin/sh
scriptdir=`dirname $0`

for file in $scriptdir/../emma_diaries/*; 
do 
output_file=$(basename "$file")
java -mx700m -cp "$scriptdir/stanford-ner.jar:$scriptdir/lib/*" edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier $scriptdir/classifiers/english.all.3class.distsim.crf.ser.gz -outputFormat inlineXML -textFile "$file" > ../ner_markup/"$output_file"
done
