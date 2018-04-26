__author__ = 'eslamelsawy'

import sys
import xml.etree.cElementTree as ET
import xml.dom.minidom as Minidom
import dateutil.parser as DateParser

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

    for line in content_lines:
        if line.strip():

            if line.lower().startswith("page"):
                pagenumber = line.split()[1]
                line_element = ET.SubElement(body_root, "pb")
                line_element.set("n", pagenumber.__str__())
            else:
                line_element = ET.SubElement(body_root, "p")

            if parse_dates_enabled:
                try:
                    parsed_date = DateParser.parse(line.strip())
                    date_element = ET.SubElement(line_element, "date")
                    date_element.text = line
                    date_element.set("When", parsed_date.__str__())
                except ValueError:
                    line_element.text = line
            else:
                line_element.text = line

    # prettify
    pretty_xml_str = Minidom.parseString(ET.tostring(tei_root)).toprettyxml(indent="   ")

    # write to output file
    with open(output_file_name, "w") as f:
        f.write(pretty_xml_str)

if __name__ == "__main__":
    main(sys.argv[1:])