__author__ = 'eslamelsawy'

import sys
import xml.etree.cElementTree as ET
import xml.dom.minidom as Minidom
import dateutil.parser as DateParser

REFYEAR = None

def main(argv):
    # DEFAULT VALUES
    markup_filename = "markup.xml"
    variations_filename = "variations.xml"
    output_filename = "markupresolved.xml"

    markup_root = ET.parse(markup_filename).getroot()
    variations_root = ET.parse(variations_filename).getroot()

    resolveVariations(markup_root,variations_root)

    # prettify
    for elem in markup_root.iter('*'):
        if elem.text is not None:
            elem.text = elem.text.strip()
        if elem.tail is not None:
            elem.tail = elem.tail.strip()
    pretty_xml_str = Minidom.parseString(ET.tostring(markup_root)).toprettyxml(indent="   ")
    with open(output_filename, "w") as f:
        f.write(pretty_xml_str)


def resolveVariations(markup_root, variations_root):
    # build variation dictinary
    variation_to_reference_location_dic = {}
    for location in variations_root:
        # find reference name
        reference_name = ""
        modern_element = location.find('modern-name')
        if modern_element is not None:
            reference_name = modern_element.text
        else:
            wiki_page_Element = location.find('wiki-page')
            reference_name = wiki_page_Element.text

        # find variations
        for wiki_variation in location.findall("wiki-variation"):
            variation_to_reference_location_dic[wiki_variation.text] = reference_name

        for manual_variation in location.findall("manual-variation"):
            variation_to_reference_location_dic[manual_variation.text] = reference_name

    # read markup
    for placename in markup_root.iter("placeName"):
        reference = findreference(placename.text, variation_to_reference_location_dic)

        if reference is not None:
            # print("location: " + placename.text + " reference: "+ reference)
            placename.attrib["ref"] = "#" + reference
        else:
            # attribute ref should be defaulted to the placeName.text
            if placename.attrib["ref"] is None or placename.attrib["ref"] is "" or placename.attrib["ref"] is "#":
                placename.attrib["ref"] = placename.text
                # print("defaulting location: " + placename.text + " reference: " + placename.attrib["ref"])
            # else:
                # already tagged



def findreference(location, dic):
    for key in dic:
        if location.strip().lower() == key.strip().lower():
            return dic[key]
    return None


def readxmlfile(file_name):
    # read tei header file
    with open(file_name) as f:
        tei_header_lines = f.readlines()

    xml_str = ''
    for line in tei_header_lines:
        xml_str += line.strip() + " "

    return ET.fromstring(xml_str)


if __name__ == "__main__":
    main(sys.argv[1:])