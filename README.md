# Pentimento

The goal of this project is to create an end-to-end system for parsing historical documents pertaining to the Emma B. Andrews Diary Project. The system has three components: OCR, named entity recognition and normalization, and XML generation. Additionally, there are two user interfaces. The first is to aid the user in running OCR and correcting any mistakes. The second is to aid in named entity recognition and XML markup.

## User Guide

1. OCR Tool


2. NER and XML Generation Tool

The tool can be accessed here: http://eslamelsawy.pythonanywhere.com/teigenerator/

The web interface is divided into 4 sections, the top left section is for user input, you can type any text or upload a file from local disk by clicking “choose file”, then picking a .txt file from local disk then clicking “upload”

After that, click “Generate Markup”, and wait for couple of seconds until the output appears in the output section in the top right section of the page, the output can be saved to local disk as .xml file by clicking “Export”

In the lower left section you can find the TEI header section, there is a default header that you can modify or you can upload your header .xml file from local disk by clicking “choose file”, then picking a .xml file, then clicking “upload”. This header will be included in the output xml.

In the lower right section you can find the location name variations database, which you can “export” as xml file. This database is used to populate the ref attribute of placeName element in the generated markup, it tries to unify the ref attribute of different location spelling variations found in the text (e.g. Assouan and Aswân are both referring to the same name Aswan). More details about the schema of this database in the technical documentation below


3. Batch Processing NER

Batch processing for NER is not compatible with the user interface. However, it can be done via commandline. Store the documents you want to process in the ner_input directory. These documents must be plain text files. If they are image files or pdfs, they will need to go through the OCR component as described above.

From the ner directory, run the following command:

./ner.sh

The marked-up files will be available in the ner_output directory. Markup will include the following named entity XML labels:

persName
placeName
orgName
name type="hotel"
name type="vessel"

The persName tags will have a ref attribute with a normalized version of the name.

## Technical Documentation

1. OCR


2. Named Entity Recognition

The NER module uses the Stanford CoreNLP library to generate persName, placeName, and orgName tags. The Stanford CoreNLP output goes through a post-processing step to ensure that all named entities are on the same line (for compatibility with the XML generation component). There is also a rule-based post-processing step to include personal titles in the named entities (e.g. Mr., Mrs., Lord, etc.). Finally, there is another rule-based post-processing step that will reclassify named entities as vessels or hotels where applicable. 

3. Named Entity Normalization (People)

The named entity normalization step for people consists of two steps: lexical similarity and semantic similarity. The lexical similarity of named entities is computed using Levenshtein distance. 

The semantic similarity is computed using cosine distane between the contexts in which any two named entities appear. Context is defined to be the paragraph in which the named entitiy appears. The paragraphs are vectorized using a tf-idf vectorizer and then reduced to a 200-dimensional vector via SVD. 

The lexical similarity and semantic similarity are added and then clustered using affinity propagation. The most frequently occurring named entity in the cluster is used as the ref attribute.

4. Named Entity Normalization (Places)

Places names normalization is happening using places variations database (https://github.com/Linguistics575/pentimento/blob/master/teigeneratortool/teigeneratorui/static/teigeneratorui/variations.xml)

The database file is in .xml format, with <variations> element as the root, each <location> must have one <wiki-page> element which has the name of the wikipedia page that corresponds to this location

Each <location> has zero or more <wiki-variation> elements, which were automatically extracted from parsing wikipedia dumps

Each <location> can have zero or more <manual-variation> elements, which can be added manually by the annotator

Each <location> can have one <modern-name> element, which is added manually by the annotator

During generating the xml markup, we look for the <placeName> elements in the variations database, if we found a <wiki-variation> or <manual-variation> that matches the place name, we update the ref attribute of the <placeName> element with the <modern-name> if it exists otherwise we use <wiki-page>

See resolveVariations function in teigenerator.py script https://github.com/Linguistics575/pentimento/blob/master/teigeneratortool/teigeneratorui/teigenerator.py


5. XML Generation
