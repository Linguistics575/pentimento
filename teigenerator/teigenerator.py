# -*- coding: utf-8 -*-

import sys
import xml.etree.cElementTree as ET
import xml.dom.minidom as Minidom
import dateutil.parser as DateParser
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

st = StanfordNERTagger('../stanford_ner/classifiers/english.all.3class.distsim.crf.ser.gz',
'../stanford_ner/stanford-ner.jar', encoding = 'utf-8')

def main(argv):
    # DEFAULT VALUES
    parse_dates_enabled = True
    input_file_name = "input.txt"
    tei_header_file_name = "teiheader.xml"
    output_file_name = "output.xml"

    # command line params
    if argv:
        input_file_name = argv[0]
        output_file_name = argv[1]

    print("input file: " + input_file_name)
    print("output file: " + output_file_name)

    # read tei header file
    with open(tei_header_file_name) as f:
        tei_header_lines = f.readlines()

    tei_header_str = ''
    for line in tei_header_lines:
        tei_header_str += line.strip() + " "

    tei_header_root = ET.fromstring(tei_header_str)

    # read content file
    with open(input_file_name) as f:
        content_lines = f.readlines()

    # remove whitespaces
    content_lines = [x.strip() for x in content_lines]

    # build xml
    tei_root = ET.Element("TEI")
    tei_root.append(tei_header_root)
    text_root = ET.SubElement(tei_root, "text")
    body_root = ET.SubElement(text_root, "body")
    current_div = None
    current_div_empty = True
    for line in content_lines:
        if line.strip():
            tokens = line.split()
            ner_tags = st.tag(tokens)
            if line.lower().startswith("page"):
                pagenumber = line.split()[1]
                line_element = ET.SubElement(body_root, "pb")
                line_element.set("n", pagenumber.__str__())

                current_div = ET.SubElement(body_root, "div")
                current_div.set("xml:id", "EBAYYYYMMDD")
                current_div.set("type", "Entry")
                current_div_empty = True
            elif parse_dates_enabled:
                try:
                    parsed_date = DateParser.parse(line.strip())
                    if not current_div_empty:
                        current_div = ET.SubElement(body_root, "div")
                        current_div.set("xml:id", "EBAYYYYMMDD")
                        current_div.set("type", "Entry")
                    line_element = ET.SubElement(current_div, "p")
                    title_element = ET.SubElement(line_element, "title")
                    date_element = ET.SubElement(title_element, "date")
                    date_element.text = line
                    date_element.set("When", parsed_date.__str__())
                    current_div_empty = False
                except ValueError:
                    line_element = ET.SubElement(current_div, "p")
                    line_text = ""
                    for i in range(0, len(ner_tags)):
                        if ner_tags[i][1] == "O":
                            line_text += ner_tags[i][0]
                            line_text += " "
                        else:
                            ner_element = ET.SubElement(line_element, "ner")
                            ner_element.text = ner_tags[i][0]
                            ner_tail = ner_tags[i+1:]
                            ner_tail = [x[0] for x in ner_tail]
                            ner_element.tail = ner_tail
                            break
                            
                    line_element.text = line_text
                                        
                    current_div_empty = False
            else:
                line_element = ET.SubElement(body_root, "p")
                line_text = ""
                for i in range(0, len(ner_tags)):
                    if ner_tags[i][1] == "O":
                        line_text += ner_tags[i][0]
                        line_text += " "
                    else:
                        ner_element = ET.SubElement(line_element, "ner")
                        ner_element.text = ner_tags[i][0]
                        ner_tail = ner_tags[i+1:]
                        ner_tail = [x[0] for x in ner_tail]
                        ner_element.tail = ner_tail
                        break
    # prettify
    pretty_xml_str = Minidom.parseString(ET.tostring(tei_root)).toprettyxml(indent="   ")

    # write to output file
    with open(output_file_name, "w") as f:
        f.write(pretty_xml_str)

if __name__ == "__main__":
    main(sys.argv[1:])
