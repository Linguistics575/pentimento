import os, re
from Levenshtein import jaro_winkler
from bs4 import BeautifulSoup
import numpy as np
from sklearn.cluster import AffinityPropagation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

titles = ['Mr.', 'Miss', 'Mrs.', 'Ms.', 'Lady', 'Dr.', 'Madame', 'M.', 'Mme.', 'Mlle.', 'Sir', 'Major', 'SS. ']

data_dir = '../ner_markup'
output_dir = '../ner_output'
files = os.listdir(data_dir)
for x in files:
    with open(os.path.join(data_dir, x), 'r') as f:
        content = f.read()
    content = re.sub('<PERSON>', '<persName>', content)
    content = re.sub('</PERSON>', '</persName>', content)
    content = re.sub('<LOCATION>', '<placeName ref="#">', content)
    content = re.sub('</LOCATION>', '</placeName>', content)
    content = re.sub('<ORGANIZATION>', '<orgName ref="#">', content)
    content = re.sub('</ORGANIZATION>', '</orgName>', content)
    soup = BeautifulSoup(content, 'lxml')
    for node in soup.find_all('persname'):
        node.string = re.sub(r'\n', u'</persName>\n', node.string)
    for node in soup.find_all('orgname'):
        node.string = re.sub(r'\n', u'</orgName>\n', node.string)
    for node in soup.find_all('placename'):
        node.string = re.sub(r'\n', u'</placeName>\n', node.string)
                 
    soup = str(soup)
    soup = re.sub('&lt;', '<', soup)
    soup = re.sub('&gt;', '>', soup)
    soup = re.sub('</p></body></html>', '', soup)
    soup = re.sub('<html><body><p>', '', soup)
    soup = re.sub('persname', 'persName', soup)
    soup = re.sub('placename', 'placeName', soup)
    soup = re.sub('orgname', 'orgName', soup)
    
    with open(os.path.join(output_dir, x), 'w') as f:
        f.write(soup)
        
files = os.listdir(output_dir)
person_names = []
for x in files:
    with open(os.path.join(output_dir, x), 'r') as f:
        content = f.read()
    soup = BeautifulSoup(content, 'lxml')
    for node in soup.find_all(['orgname', 'placename', 'persname']):
        if 'S.S.' in node.text or 'SS. ' in node.text:
            node.name = 'name'
            node.attrs = {'type': 'vessel', 'ref': '#{}'.format(re.sub(' ', '_', node.text))}
        elif 'Hotel' in node.text:
            node.name = 'name'
            node.attrs = {'type': 'hotel', 'ref': '#{}'.format(re.sub(' ', '_', node.text))}
        if node.name == 'persname':
            person_names.append(node.text)
    soup = str(soup)
    soup = re.sub('</p></body></html>', '', soup)
    soup = re.sub('<html><body><p>', '', soup)
    soup = re.sub('persname', 'persName', soup)
    soup = re.sub('placename', 'placeName', soup)
    soup = re.sub('orgname', 'orgName', soup)
    with open(os.path.join(output_dir, x), 'w') as f:
        f.write(soup)
person_names = Counter(person_names)

for x in files:
    with open(os.path.join(output_dir, x), 'r') as f:
        content = f.read()
    soup = BeautifulSoup(content, "lxml")
    ix = 0
    person_dict = {}
    for node in soup.find_all('persname'):
        person_dict[ix] = node.text
        ix += 1
    lex_sim_mat = np.zeros((len(person_dict), len(person_dict)))
    for i in range(0, len(person_dict)):
        for j in range(0, len(person_dict)):
            lex_sim_mat[i, j] = jaro_winkler(person_dict[i], person_dict[j])

    elems = []    
    p = soup.p
    e = soup.p.next_element
    elems.append(e)  
    while e.next_sibling:
        e = e.next_sibling
        elems.append(e)
        
    contexts = []
    for e in elems:
        if e.name == 'persname':
            context = [e.previous_sibling + e.next_sibling]
            contexts.append(context[0])
    
    tfidf = TfidfVectorizer(binary = True)
    tfidf_vecs = tfidf.fit_transform(contexts)
    svd = TruncatedSVD(300)
    normalizer = Normalizer(copy = False)
    pipeline = make_pipeline(svd, normalizer)
    vecs = pipeline.fit_transform(tfidf_vecs)   
    sem_sim_mat = cosine_similarity(vecs)
    
    sim_mat = lex_sim_mat + sem_sim_mat
    af = AffinityPropagation(damping = 0.74, affinity = 'precomputed')
    clusters = af.fit_predict(sim_mat)
    
    cluster_dict = dict()
    num_clusters = len(set(clusters))
    for i in range(0, num_clusters):
        names = []
        for ix in person_dict.keys():
            if clusters[ix] == i:
                names.append(person_dict[ix])
        cluster_name = Counter(names).most_common()[0][0]
        cluster_name = '#' + cluster_name
        cluster_name = re.sub(' ', '_', cluster_name)
        cluster_dict[i] = cluster_name
        
    ref_dict = dict()
    for ix in person_dict.keys():
        ref_dict[ix] = cluster_dict[clusters[ix]]
    for ix in person_dict:
        print(person_dict[ix], '\t', ref_dict[ix])
    ix = 0
    for e in elems:
        if e.name == 'persname':
            if e.text == 'Theo' or e.text == 'Theodore':
                e['ref'] = '#Davis_Theodore'
            elif e.text == 'Nettie' or e.text == 'Miss Buttles':
                e['ref'] = '#Buttles_Jeanette'
            else:
                e['ref'] = ref_dict[ix]
            ix += 1
            
    soup = str(soup)
    soup = re.sub('</p></body></html>', '', soup)
    soup = re.sub('<html><body><p>', '', soup)
    soup = re.sub('persname', 'persName', soup)
    soup = re.sub('placename', 'placeName', soup)
    soup = re.sub('orgname', 'orgName', soup)
    
    
    with open(os.path.join(output_dir, x), 'w') as f:
        f.write(soup)   
    
    
