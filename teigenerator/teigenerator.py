__author__ = 'eslamelsawy'

import sys
import xml.etree.cElementTree as ET
import xml.dom.minidom as Minidom
import dateutil.parser as DateParser

REFYEAR = None

def main(argv):
    # DEFAULT VALUES
    parse_dates_enabled = True
    #input_file_name = "input.txt"
    input_file_name = "input_no_ner.txt"
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

            if line.lower().startswith("page"):
                pagenumber = line.split()[1]
                line_element = ET.SubElement(body_root, "pb")
                line_element.set("n", pagenumber.__str__())

                current_div = ET.SubElement(body_root, "div")
                current_div.set("xml:id", "EBAYYYYMMDD")
                current_div.set("type", "Entry")
                current_div_empty = True
            elif parse_dates_enabled:

                parsed_date = is_date(line.strip())
                if parsed_date is not None:
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
                else:
                    line_element = ET.SubElement(current_div, "p")

                    if istitle(line):
                        title_element = ET.SubElement(line_element, "title")
                        scan_paragraph_for_dates(line, title_element)
                    else:
                        scan_paragraph_for_dates(line, line_element)
                    current_div_empty = False
            else:
                line_element = ET.SubElement(body_root, "p")
                line_element.text = line

    # prettify
    pretty_xml_str = Minidom.parseString(ET.tostring(tei_root)).toprettyxml(indent="   ")

    # write to output file
    with open(output_file_name, "w") as f:
        f.write(pretty_xml_str)


def istitle(line):
    for word in line.split():
        if not word[0].isupper() and not word[0].isnumeric():
            return False
    return True


def scan_paragraph_for_dates(paragraph, parent):
    parsed_dates_dic = {}
    words = paragraph.split(" ")
    for window in [6, 5, 4, 3, 2]:
        for index in range(len(words) - window + 1):
            substring = " ".join(words[index:index+window])
            parsed_date = is_date(substring)
            if parsed_date:
                is_new_Date = True
                for previous_date in parsed_dates_dic:
                    if substring.strip() in previous_date.strip():
                        is_new_Date = False
                        break

                if is_new_Date:
                    parsed_dates_dic[substring] = parsed_date

    if not parsed_dates_dic:
        parent.text = paragraph

    first_child = True
    last_child_date = None
    for parsed_date in parsed_dates_dic:
        index = paragraph.find(parsed_date)
        part1 = paragraph[:index]
        paragraph = paragraph[index+len(parsed_date):]

        if first_child:
            first_child = False
            parent.text = part1
        else:
            last_child_date.tail = part1

        date_element = ET.SubElement(parent, "date")
        date_element.text = parsed_date
        date_element.set("When", parsed_dates_dic[parsed_date].__str__())

        last_child_date = date_element

    if last_child_date is not None:
        last_child_date.tail = paragraph


def is_date(x):
    try:
        return parse_date(x)
    except ValueError:
        return None


def parse_date(string):
    global REFYEAR
    ref_date1 = DateParser.parse("April 8th. 1100.")
    ref_date2 = DateParser.parse("May 9th. 1101.")

    trail_1 = DateParser.parse(string.__str__(), default=ref_date1)
    trail_2 = DateParser.parse(string.__str__(), default=ref_date2)

    is_orig_year = True
    is_orig_month = True
    is_orig_day = True

    if trail_1.year == ref_date1.year and trail_2.year == ref_date2.year:
        is_orig_year = False

    if trail_1.month == ref_date1.month and trail_2.month == ref_date2.month:
        is_orig_month = False

    if trail_1.day == ref_date1.day and trail_2.day == ref_date2.day:
        is_orig_day = False

    if is_orig_year and is_orig_month and is_orig_day:
        REFYEAR = str(trail_1.year)
        return DateParser.parse(string)
    if is_orig_month and is_orig_day:
        if REFYEAR is not None:
            default = DateParser.parse(REFYEAR)
            return DateParser.parse(string, default=default)
        else:
            return DateParser.parse(string)


if __name__ == "__main__":
    main(sys.argv[1:])