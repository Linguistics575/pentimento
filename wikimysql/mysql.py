import MySQLdb
import xml.etree.cElementTree as ET
import xml.dom.minidom as Minidom

def main():
    output_file_name = "variations.xml"
    input_file_name = "input.txt"
    conn = MySQLdb.connect(host="localhost",
                           user="root",
                           passwd="***",
                           db="wikipedia")

    previous_output_root = ET.parse(output_file_name).getroot()
    previous_output_dic = {}
    for previous_location in previous_output_root:
        previous_output_dic[previous_location.text.strip()] = previous_location

    with open(input_file_name) as f:
        locations = f.readlines()

    output_root = ET.Element("Variations")

    for location_list_str in locations:
        if not location_list_str.strip() or location_list_str.startswith("--"):
            continue

        location_list = location_list_str.strip().split(";")

        wiki_page_title = location_list[0]
        manual_variations = location_list[1:] if len(location_list) > 1 else []

        # getting the modern name
        modren_name = ""
        for manual_variation in manual_variations:
            if manual_variation.startswith("\""):
                modren_name = manual_variation
                break
        if modren_name:
            manual_variations.remove(modren_name)
            modren_name = modren_name[1:-1] # remove quotes
            manual_variations.append(modren_name)


        # getting wiki variations
        wiki_variations = []
        if wiki_page_title in previous_output_dic:
            print("Cache Hit:" + wiki_page_title)
            previous_element = previous_output_dic[wiki_page_title]
            for wiki_variation_element in previous_element.findall('wiki-variation'):
                wiki_variations.append(wiki_variation_element.text)
        else:
            # query wiki db for variations
            print("Query:"+ wiki_page_title)
            cursor = conn.cursor()
            cursor.execute("SELECT  p.page_title, r.rd_title  "
                           "FROM redirect as r "
                           "JOIN page as p "
                           "ON p.page_id = r.rd_from "
                           "where r.rd_title = '" + wiki_page_title.strip() + "'")
            rows = cursor.fetchall()
            for row in rows:
                variation = row[0].decode("utf-8")
                wiki_variations.append(variation)
                print("%s" % variation)
            print("\nNumber of rows returned: %d" % cursor.rowcount)
            print("-------")
            cursor.close()

        # adding the location name as title.txt and one of the variations
        location_element = ET.SubElement(output_root, "location")
        location_element.text = wiki_page_title

        variation_element = ET.SubElement(location_element, "wiki-page")
        variation_element.text = wiki_page_title

        if modren_name:
            variation_element = ET.SubElement(location_element, "modern-name")
            variation_element.text = modren_name

        for manual_variation in manual_variations:
            variation_element = ET.SubElement(location_element, "manual-variation")
            variation_element.text = manual_variation

        for wiki_variation in wiki_variations:
            variation_element = ET.SubElement(location_element, "wiki-variation")
            variation_element.text = wiki_variation

    conn.close()

    # prettify
    for elem in output_root.iter('*'):
        if elem.text is not None:
            elem.text = elem.text.strip()
        if elem.tail is not None:
            elem.tail = elem.tail.strip()
    pretty_xml_str = Minidom.parseString(ET.tostring(output_root)).toprettyxml(indent="   ")

    # write to output file
    with open(output_file_name, "w") as f:
        f.write(pretty_xml_str)

if __name__ == "__main__":
    main()