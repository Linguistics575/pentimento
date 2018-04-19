The script is doing the following:
- The output TEI consists of two parts (1) 'teiHeader" element(2) 'text' element
- The script reads 'teiHeader' from teiheader.xml, we can modify the file later, so this just serves as a template
- The script reads the content of "input.txt" and puts it into 'text' element
- Finally prettify and output the xml to "output.xml"

Run Instructions:
python teigenerator.py