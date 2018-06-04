import xml.etree.cElementTree as ET
import xml.dom.minidom as Minidom
import teigeneratorui.dateutil.parser as DateParser

REFYEAR = None

def generateXML(content_lines, header_root, variations_root):
    parse_dates_enabled = True

    # remove whitespaces
    content_lines = [x.strip() for x in content_lines]

    # build xml
    tei_root = ET.Element("TEI")
    tei_root.append(header_root)
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
                    if current_div is None:
                        current_div = ET.SubElement(body_root, "div")
                        current_div.set("xml:id", "EBAYYYYMMDD")
                        current_div.set("type", "Entry")

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
    pretty_xml_str = clean_and_prettifyxml(tei_root, "", "")

    # xml validation and resolve variations:
    validated_tei_root = ET.fromstring(pretty_xml_str)
    resolveVariations(validated_tei_root, variations_root)
    validated_pretty_xml_str = clean_and_prettifyxml(validated_tei_root, "   ", "\n")

    return validated_pretty_xml_str

def clean_and_prettifyxml(markup, intend, newline):
    for elem in markup.iter('*'):
        if elem.text is not None:
            elem.text = elem.text.strip()
        if elem.tail is not None:
            elem.tail = elem.tail.strip()

    pretty_xml_str = Minidom.parseString(ET.tostring(markup)).toprettyxml(indent=intend, newl=newline)


    pretty_xml_str = pretty_xml_str.replace("&lt;", "<")
    pretty_xml_str = pretty_xml_str.replace("&gt;", ">")
    pretty_xml_str = pretty_xml_str.replace("&quot;", "\"")
    return pretty_xml_str

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
            #print("location: " + placename.text + " reference: "+ reference)
            placename.attrib["ref"] = "#" + reference
        else:
            # attribute ref should be defaulted to the placeName.text
            if placename.attrib["ref"] is None or placename.attrib["ref"] is "" or placename.attrib["ref"] is "#":
                placename.attrib["ref"] = placename.text
                #print("defaulting location: " + placename.text + " reference: " + placename.attrib["ref"])
            # else:
                # already tagged


def findreference(location, dic):
    for key in dic:
        if location.strip().lower() == key.strip().lower():
            return dic[key]
    return None