__author__ = 'eslamelsawy'

import xml.etree.cElementTree as ET
import xml.dom.minidom as Minidom

def main():
    input_file_name = "input.txt"
    tei_header_file_name = "teiheader.xml"
    output_file_name = "output.xml"

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

    for line in content_lines:
        if line.strip():
            ET.SubElement(body_root, "p").text = line

    # prettify
    pretty_xml_str = Minidom.parseString(ET.tostring(tei_root)).toprettyxml(indent="   ")

    # write to output file
    with open(output_file_name, "w") as f:
        f.write(pretty_xml_str)

if __name__ == "__main__":
    main()