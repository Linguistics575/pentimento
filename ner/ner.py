import os
from nltk.tag import StanfordNERTagger

st = StanfordNERTagger('../stanford_ner/classifiers/english.all.3class.distsim.crf.ser.gz',
'../stanford_ner/stanford-ner.jar', encoding = 'utf-8')

data_dir = '../emma_diaries'
output_dir = '../ner_markup'

titles = ['Mr.', 'Miss', 'Mrs.', 'Ms.', 'Lady', 'Dr.', 'Madame', 'M.', 'Mme.', 'Mlle.']

files = os.listdir(data_dir)
for x in files:
    with open(os.path.join(data_dir, x), 'r') as f:
        content_lines = f.readlines()
        
    content_lines = [z.strip() for z in content_lines]
    content_lines = [z for z in content_lines if len(z) > 0]
    output_lines = []
    
    for line in content_lines:
        tokens = line.split(' ')
        tokens = [z for z in tokens if len(z) > 0]
        ner = st.tag(tokens)
        for ix in range(0, len(ner)):
            if ner[ix][1] != 'O':
                tokens[ix] = '<ner>' + tokens[ix] + '</ner>'
        line = ' '.join(tokens)
        print(line)
        output_lines.append(line)
        
    with open(os.path.join(output_dir, x), "w") as f:
        f.write("\n\n".join(output_lines))