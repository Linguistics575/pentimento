#!/bin/sh
scriptdir=`dirname $0`/../../stanford_ner 

java -mx700m -cp "$scriptdir/stanford-ner.jar:$scriptdir/lib/*" edu.stanford.nlp.ie.crf.CRFClassifier -loadClassifier $scriptdir/classifiers/english.all.3class.distsim.crf.ser.gz -outputFormat inlineXML -textFile $1 > teigeneratortool/temp/stanford_ner_output.txt

python3 teigeneratortool/ner.py
