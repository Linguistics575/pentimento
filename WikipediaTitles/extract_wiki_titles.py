#!/usr/bin/python3

for line in open('enwiki-latest-page.sql'):
    if line.startswith('INSERT INTO'):
        start = line.index('(')
        end = -2
        exec("a = [" + line[start:end].replace('NULL', 'None') + "]")
        for aa in a:
            print(aa[2])
