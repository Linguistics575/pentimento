import MySQLdb
import xml.etree.cElementTree as ET
import xml.dom.minidom as Minidom

def main():
    output_file_name = "output.xml"
    input_file_name = "input.txt"
    conn = MySQLdb.connect(host="localhost",
                           user="root",
                           passwd="****",
                           db="wikipedia")

    previous_output_root = ET.parse(output_file_name).getroot()
    previous_output_dic = {}
    for title in previous_output_root:
        previous_output_dic[title.text.strip()] = title

    with open(input_file_name) as f:
        locations = f.readlines()

    output_root = ET.Element("Variations")

    for location in locations:
        if not location.strip() or location.startswith("--"):
            continue

        location = location.strip()

        if location in previous_output_dic:
            print("Cache Hit:" + location)
            output_root.append(previous_output_dic[location])
            continue

        print("Query:"+location)

        # adding the location name as title.txt and one of the variations
        location_element = ET.SubElement(output_root, "title")
        location_element.text = location

        variation_element = ET.SubElement(location_element, "variation")
        variation_element.text = location

        # query wiki db for variations
        cursor = conn.cursor()
        cursor.execute("SELECT  p.page_title, r.rd_title  "
                       "FROM redirect as r "
                       "JOIN page as p "
                       "ON p.page_id = r.rd_from "
                       "where r.rd_title = '" + location.strip() + "'")
        rows = cursor.fetchall()
        for row in rows:
            variation = row[0].decode("utf-8")
            variation_element = ET.SubElement(location_element, "variation")
            variation_element.text = variation
            print("%s" % variation)
        print("\nNumber of rows returned: %d" % cursor.rowcount)
        print("-------")
        cursor.close()

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