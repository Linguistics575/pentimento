__author__ = 'eslamelsawy'

import sys
import xml.etree.cElementTree as ET
import xml.dom.minidom as Minidom
import re
import os


def main(argv):

    input_file = "enwiki-20180420-redirect.sql"
    with open(input_file) as f:
        lines = f.readlines()


    count = 0;
    for line in lines:
        if not line.startswith("INSERT"):
            continue
        # write to output file
        with open(str(count)+".sql", "w") as f:
            f.write(line.replace("`redirect`", "redirect"))
            count = count + 1
            break



if __name__ == "__main__":
    main(sys.argv[1:])