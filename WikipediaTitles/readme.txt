In this directory, we extract tokens in Wikipedia page titles from the Wikipedia database dump: https://dumps.wikimedia.org/enwiki/latest/

extract_wiki_titles.py takes enwiki-latest-page.sql as input (~5.1 GB uncompressed), outputs article titles as they appear in the URL

tokenize_and_count.py takes the output from extract_wiki_titles.py, tokenizes the titles into words (lowercasing to normalize), and counts the frequency of the words.

titleWordCount.tsv is the output of tokenize_and_count.py

The full directory with data is available on Patas: /projects/ling575_2018/WikipediaTitles
