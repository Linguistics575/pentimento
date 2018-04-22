__author__ = 'eslamelsawy'
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
import subprocess
import os
from dateutil import parser

def main():
    input = "x"
    # x = parser.parse("Hi", fuzzy=True)
    isdate, parsed_date = is_date(input)

    print(isdate)
    print(parsed_date)

def is_date(string):
    try:
        parsed_date = parse(string)
        return True, parsed_date
    except ValueError:
        return False, None

if __name__ == "__main__":
    main()