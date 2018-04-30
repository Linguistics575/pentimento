__author__ = 'eslamelsawy'

import sys
import xml.etree.cElementTree as ET
import xml.dom.minidom as Minidom
import re
import os


def main(argv):

    input_dir = 'input/'
    for file in os.listdir(input_dir):
        if file.startswith("."):
            continue

        output_file_name = 'output/' + file
        print(file)
        # read wiki file
        tree = ET.parse(input_dir + file)
        wiki_root = tree.getroot()

        # build xml
        output_root = ET.Element("Output")

        # find pages
        terminating_tags = []
            # "==Gallery==", "==References==", "==External links==", "==See also==",
            # "== Gallery ==", "== References ==", "== External links ==", "== See also =="]

        forbidden_line_starts = []
        # ["==", "File:", "[[", "{{", "* ", "}}"]
        for page_tag in wiki_root.findall("page"):
            title = page_tag.find("title")
            if title.text.startswith("Category"):
                continue
            output_page = ET.SubElement(output_root, "page")
            output_title = ET.SubElement(output_page, "title")
            output_title.text = title.text

            revision_tag = page_tag.find("revision")
            text_tag = revision_tag.find("text")
            lines = [s.strip() for s in text_tag.text.splitlines()]
            for line in lines:
                if not line:
                    continue

                if line.strip() in terminating_tags:
                    break

                skip_line = False
                for word in forbidden_line_starts:
                    if line.strip().startswith(word):
                        skip_line = True
                        break
                if skip_line:
                    continue

                # remove non alpha numeric
                line = re.sub(r'\W+', ' ', line).strip()

                # upper case words
                words = line.split()
                upper_words = list(filter(lambda x: x[0].isupper(), words))

                for word in upper_words:
                    output_line = ET.SubElement(output_page, "line")
                    output_line.text = word

                # for testing
                # line = " ".join(upper_words)
                # output_line = ET.SubElement(output_page, "line")
                # output_line.text = line

        # prettify
        pretty_xml_str = Minidom.parseString(ET.tostring(output_root)).toprettyxml(indent="   ")

        # write to output file
        with open(output_file_name, "w") as f:
            f.write(pretty_xml_str)

if __name__ == "__main__":
    main(sys.argv[1:])