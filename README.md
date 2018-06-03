# pentimento

The goal of this project is to create an end-to-end system for parsing historical documents pertaining to the Emma B. Andrews Diary Project. The system has three components: OCR, named entity recognition and normalization, and XML generation. Additionally, there are two user interfaces. The first is to aid the user in running OCR and correcting any mistakes. The second is to aid in named entity recognition and XML markup.

USER GUIDE

1. OCR


2. NER and XML Generation


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

TECHNICAL DOCUMENTATION

1. OCR


2. Named Entity Recognition

The NER component is available in the user interface. Additionally, 

3. Named Entity Normalization (People)


4. Named Entity Normalization (Places)


5. XML Generation
