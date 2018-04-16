import os
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

st = StanfordNERTagger('../stanford_ner/classifiers/english.all.3class.distsim.crf.ser.gz',
'../stanford_ner/stanford-ner.jar', encoding = 'utf-8')

data_dir = '../emma_diaries'
output_dir = '../ner_output'

files = os.listdir(data_dir)
for x in files:
	with open(os.path.join(data_dir, x), 'r') as f:
		text = f.read()
	tokenized_text = word_tokenize(text)
	classified_text = st.tag(tokenized_text)
	print(classified_text)
	with open(os.path.join(output_dir, x), 'w') as f:
		for token in classified_text:
			f.write('{}\t{}\n'.format(token[0], token[1]))

