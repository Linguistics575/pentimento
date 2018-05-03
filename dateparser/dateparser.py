__author__ = 'eslamelsawy'
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
import subprocess
import os
from dateutil import parser
import xml.etree.cElementTree as ET
import xml.dom.minidom as Minidom


def main():
    input = "eslam Monday.  April 8th. 2002 .  SS. Berlin. April 8th. 2003 ashraf"
    input2 = "Sailed this morning for Genoa - where we will wait 15 " \
             "days for our boat for Alexandria.  Have my old appartment which is the" \
             " Captain’s, and very commodious and comfortable, and which I occupied two years ago." \
             "  We know a few of the passengers.  The 4 days we passed in New York were dismal in the extreme - " \
             "it rained all the time, I took a severe cold, and did not go out of the house after the first day " \
             "- and had to cancel a long standing engagement to drive with the Fairfield Osborns, who" \
             " had invited a lot of pleasant people to meet us. It was altogether a great piece of disappointment," \
             " that visit in New York."

    tei_root = ET.Element("TEI")

    scan_paragraph_for_dates(input, tei_root)

    # tei_root.text = parsed_paragraph
    pretty_xml_str = Minidom.parseString(ET.tostring(tei_root)).toprettyxml(indent="   ")

    print(pretty_xml_str)
    str1 = "SS. Berlin. Oct."
    print(str1.istitle())
    # x = parser.parse("Hi", fuzzy=True)
    #isdate, parsed_date = is_date(input)

    # parsed_date = parse(input, fuzzy=True)
    # parsed_date2 = parse(input2, default=parsed_date)
    # test = datetime.strptime()

    # print(parsed_date2)

    # print(datetime.now().year)
    # print(datetime.now().month)
    # print(datetime.now().day)
    # print(datetime.now().hour)

def scan_paragraph_for_dates(paragraph, parent):
    parsed_dates_dic = {}
    words = paragraph.split(" ")
    for window in [6, 5, 4, 3, 2]:
        for index in range(len(words) - window + 1):
            substring = " ".join(words[index:index+window])
            parsed_date = is_date(substring)
            if parsed_date and validate_date_components(substring):
                is_new_Date = True
                for previous_date in parsed_dates_dic:
                    if substring.strip() in previous_date.strip():
                        is_new_Date = False
                        break

                if is_new_Date:
                    parsed_dates_dic[substring] = parsed_date

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


def validate_date_components(string):
    ref_date1 = parse("April 8th. 1912.")
    ref_date2 = parse("May 9th. 1913.")

    trail_1 = parse(string, fuzzy=True, default=ref_date1)
    trail_2 = parse(string, fuzzy=True, default=ref_date2)

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
        return True
    if is_orig_month and is_orig_day:
        return True
    return False


def is_date(string):
    try:
        parsed_date = parse(string)
        return parsed_date
    except ValueError:
        return None

if __name__ == "__main__":
    main()