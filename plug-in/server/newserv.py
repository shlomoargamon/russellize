# -*- coding: utf-8 -*-
import requests 
import nltk
from bs4 import BeautifulSoup 
from inspect import getsourcefile
from flask import Flask,  request
from flask_cors import CORS, cross_origin
from os.path import abspath, join, dirname
from urllib.parse import urlparse
from urllib.parse import urljoin

#app = Flask(__name__, static_url_path='/settings')
app = Flask(__name__)
#app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
#app.config['CORS_HEADERS'] = 'Content-Type'

#cors = CORS(app, resources={r"/foo": {"origins": "http://localhost:port"}})

"""
We have to take out the vocabulary and the result of our analyzer to 
filter all the synonyms we get
"""
def dict_vocab ():
    dictio = {}
    full_filepath = join(dirname(abspath(getsourcefile(lambda:0))), "Analyzer")
    full_filepath = join(full_filepath, "output.vocab")
    with open(full_filepath, "r", encoding="utf-8" ) as f:
        text = f.readlines()
        for i in text: 
            i = i.split()
            dictio[i[0]]=i[1]
    return dictio


"""
We look for the synonymous in the dictionary and apply a threshold.
"""
def vocab (name, noun,lexicon_dictio):
    if (noun in lexicon_dictio) & (name in lexicon_dictio):
        polarity = float(lexicon_dictio[noun])
        polarity_sys = float(lexicon_dictio[name])
        threshold = 0.0001
        if ((polarity > threshold) & (polarity_sys > threshold)) | ((polarity< threshold) & (polarity_sys < threshold))  :
            return 1
        if ((polarity > -threshold) & (polarity < threshold)) & (polarity_sys> -threshold) & (polarity_sys < threshold)  :
            return 1 
        else: 
            return 0
    return 0
 
    
"""
We analyze each synonym of our word, in case it passes 
the filter we introduce it into our web page.
"""
def add(noun, lista, POS):
    result = '<div id="text'+str(POS)+'" class="dropdown-content">'
    for i in lista:                             
        result += str('<a onclick="mytoggle(this,dropdownclass'+str(POS)+')">'+i+'</a>')
    result += '<a onclick="mytoggle2(this, '+str(POS)+')" id="last'+str(POS)+'">All</a>'
    result += str('</div></div>')
    return result

def synonyms(noun, POS, lexicon_dictio, polarity):
    dictio ={}
    lista = []
    for syns in nltk.corpus.wordnet.synsets(noun):
        for l in syns.lemmas():
            if l.name().lower() != noun.lower():
                if l.name() not in dictio:
                    name = str(l.name()).replace("_", " ")
                    if polarity != 3:
                        back = vocab(name, noun, lexicon_dictio)
                        if back == 0 and polarity == 0:
                            lista.append(name)
                            dictio[l.name()]=1
                        if back == 1 and polarity == 1:
                            lista.append(name)
                            dictio[l.name()]=1
                    elif polarity == 3:
                        lista.append(name)
                        dictio[l.name()]=1
    if len(lista) != 0:
        result = add(noun, lista, POS)
        boolean = 1
    else: 
        result = ''
        boolean = 0
    return result, boolean


"""
Translate to the language used by nltk
"""
def translate(POS):
    if POS == 0:
        return 'JJ'
    elif POS == 1:
        return 'NN'
    elif POS == 2:
        return 'RB'
    return 'JJ'

       
"""
Create the button in each of the adjectives that we have highlighted 
to display the synonyms
"""
def button(noun, sys, number):
    text_html = '<div id="'+str(number)+'" class="dropdown">'
    text_html +='<button onclick="iitbutton(\''+str(number)+'\')"'
    text_html += 'class="dropbtn"'
    text_html += 'id="dropdownclass'+str(number)+'">'+noun+sys
    text_html += "</button>"
    return text_html

def BOLD(noun, sys, number):
    return "<B>" + noun + "</b>"


"""
Look at all the words and highlight the adjectives we have.
"""                   
def highlight(url):
    page = requests.get(url)
    page_soup = BeautifulSoup(page.content, 'html.parser')

    header = page_soup.find('head')

    base_string = "<base href=\"" + url + "\"/>"
    base_soup = BeautifulSoup(base_string,'html.parser')

    header.append(base_soup)

    para_list = page_soup.find_all('p')
    for para in para_list:
        result = ''
        sent_text = nltk.sent_tokenize(para.text)
        for sent in sent_text:
            tokens = nltk.word_tokenize(sent)
            position = 0
            for token in tokens:
                if position % 3 == 0:
                    text = BOLD(noun, sys1, number)
                    result += text
                else: 
                    result += noun + ' '
                position += 1
        para.replaceWith(BeautifulSoup(result, 'html.parser'))

    return page_soup

"""
Parameters of the server where we collect the variables that we need.
"""
#@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
@app.route('/')
def hello():
    print("Hello, World!")
    return("Hello!")
app.add_url_rule('/','hello',hello)


@app.route('/worker')
def worker():
    print("Worker")
    src_url = request.args.get('url')
    POS = request.args.get('position')
    polarity = request.args.get('polarity')
    POS = 'NN'
    polarity = 1.0
    new_html = highlight(src_url)
    
    return new_html.prettify()
#app.add_url_rule('/','worker',worker)


@app.errorhandler(404)
def page_not_found(error):
    return 'ACK!! This page does not exist', 404

@app.errorhandler(400)
def page_not_found(error):
    return 'Could not understand: ' + str(error), 400

def exception_handler(*args):
    print("BAD REQUEST:")
    print(request.url)
    return "Something wrong happened", 400

if __name__ == '__main__':

    app.run(debug=True,use_reloader=False)

 
