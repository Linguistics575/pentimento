#!/bin/bash
cd ../stanford_ner
./ner.sh
cd ../ner
python ner.py
