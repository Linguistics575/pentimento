from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import teigeneratorui.teigenerator as TEIGenerator
import os
from django.conf import settings
import xml.etree.cElementTree as ET
import xml.dom.minidom as Minidom
import json
import subprocess


@csrf_exempt
def generatemarkup(request):
    print("PY: generating markup ...")

    json_data = json.loads(request.body)
    
    with open(os.path.join('teigeneratortool', 'temp', 'input.txt'), 'w') as f:
        f.write(json_data['text'])

    # Call named entity component
    subprocess.call('./teigeneratortool/ner.sh teigeneratortool/temp/input.txt', shell=True)

    with open(os.path.join('teigeneratortool', 'temp', 'ner_output.txt'), 'r') as f:
        json_data['text'] = f.read()
    text_lines = json_data['text'].split("\n")
    header_root = ET.fromstring(json_data['header'].replace("\n", "\n"))
    variations_root = ET.fromstring(json_data['variations'].replace("\n", "\n"))

    output = TEIGenerator.generateXML(text_lines, header_root, variations_root)
    return HttpResponse(output)


def index(request):
    # reading tei header
    teiheader_filename = os.path.join(settings.BASE_DIR, 'teigeneratorui/static/teigeneratorui/teiheader.xml')
    teiheader_root = ET.parse(teiheader_filename).getroot()
    teiheader_str = TEIGenerator.clean_and_prettifyxml(teiheader_root, "  ", "\n")

    # reading  variations
    variations_filename = os.path.join(settings.BASE_DIR, 'teigeneratorui/static/teigeneratorui/variations.xml')
    variations_root = ET.parse(variations_filename).getroot()
    variations_str = TEIGenerator.clean_and_prettifyxml(variations_root, "  ", "\n")

    context = {
        'teiheader': teiheader_str,
        'variations': variations_str
    }
    return render(request, 'teigeneratorui/index.html', context)

    # template = loader.get_template('teigeneratorui/index.html')
    # return HttpResponse(template.render(context, request))
    # return HttpResponse("Hello, world. you are at tool index.")