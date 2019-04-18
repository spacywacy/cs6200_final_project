import os
import nltk
from nltk.util import ngrams
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import re
from py2casefold import casefold

stop_words = []
position_index = dict()
number_of_terms1 = dict()
index_dict = dict()

def read_stop_words():
    global stop_words
    fr = open('test-collection/common_words', 'r')
    stop_words = fr.read().splitlines()

def write_number_of_term( n, number_of_terms_dict):
    with open("number_of_terms" + str(n) + ".txt", 'w+') as fout:
        for doc_id, num in number_of_terms_dict.items():
            line = doc_id + ": " + str(num) + "\n"
            fout.write(line)

def write_inverted_indexer( n, index_dict):
    with open("inverted_indexer" + str(n) + ".txt", "w+") as fout:
        for term, doc_dict in index_dict.items():
            line = "(" + ", ".join(term) + "): ["
            for doc_id, freq_array in doc_dict.items():
                line  = line + "(" + doc_id + ", " + str(len(freq_array)) + "), "
            line = line.rstrip(", ") + "]" + "\n"
            fout.write(line)

def write_doc_freq( n, index_dict):
    sorted_index_dict = sorted(index_dict.keys())

    with open("document_freq" + str(n) + ".txt", "w+") as fout:
        for term in sorted_index_dict:
            doc_dict = index_dict[term]
            line = "(" + ", ".join(term) + "): ["
            line = line + ", ".join(doc_dict.keys()) + "], "
            line = line + str(len(doc_dict.keys())) + "\n"
            fout.write(line)

def write_position_index( n, index_dict):
    with open("position_index" + str(n) + ".txt", "w+") as fout:
        for term, doc_dict in index_dict.items():
            line = "(" + ", ".join(term) + "): ["
            for doc_id, freq_array in doc_dict.items():
                line = line + doc_id + ": (" + ", ".join(map(str, freq_array)) + "); "
            line = line.rstrip("; ") + "]" + "\n"
            fout.write(line)

def build_n_grams(token, doc_id, n, n_grams_dict, n_index_dict):
    n_grams = ngrams(token, n)
    current_count = 0
    for gram in n_grams:
        current_count += 1

        # build inverted indexer
        if gram in n_index_dict:
            freq_dict = n_index_dict[gram]
            if doc_id in freq_dict:
                freq_dict[doc_id].append(current_count)
            else:
                freq_dict[doc_id] = [current_count]
            n_index_dict[gram] = freq_dict
        else:
            freq_dict = {}
            freq_dict[doc_id] = [current_count]
            n_index_dict[gram] = freq_dict

        # build trigram freq
        if gram in n_grams_dict:
            n_grams_dict[gram] += 1
        else:
            n_grams_dict[gram] = 1
    return current_count

def build():
    path = os.getcwd() + '/articles/'
    global index_dict
    onegrams_dict = {}
    global number_of_terms1
    count = 0

    for filename in os.listdir(path):
        # if count > 10:
        #   break

        # ignore non txt file
        if ".txt" not in filename:
            continue

        fullpath = path + filename

        with open(fullpath, 'r') as content_file:
            content = content_file.read()
            token = nltk.word_tokenize(content)
            doc_id = filename.rstrip(".txt")

            total_1 = build_n_grams(token, doc_id, 1, onegrams_dict, index_dict)

        number_of_terms1[doc_id] = total_1

        count += 1

    onegrams_sorted_key = sorted(onegrams_dict, key=onegrams_dict.get, reverse=True)
    onegrams_dict = onegrams_dict

    with open("onegram.txt", 'w+') as fout:
        for key in onegrams_sorted_key:
            line = ", ".join(key) + ": " + str(onegrams_dict[key]) + "\n"
            fout.write(line)

    write_number_of_term(1, number_of_terms1)
    write_inverted_indexer(1, index_dict)
    write_doc_freq(1, index_dict)
    write_position_index(1, index_dict)


def write_to_corpus(parsedText, docID):
    # create corpus folder
    if not os.path.exists('articles'):
        os.mkdir('articles')

    filename = ''
    for chr in docID:
        if chr.isalnum():
            filename += chr

    # write to the file
    wcorpus = open('articles/' + filename + ".txt", 'w')
    wcorpus.write(parsedText)
    wcorpus.close()

def transformText(parseText, punctuations, casefolding):
    newcontent = ''

    if casefolding:
        parseText = casefold(parseText.decode('utf-8'))

    if punctuations:
        for letter in parseText:
            if letter.isalnum() or letter == '-' or letter == ' ':
                newcontent += letter
    return newcontent

def parse_corpus():
    for f in os.listdir('test-collection/cacm/'):
        fr = open('test-collection/cacm/' + f, 'r')
        doc = fr.read()
        docID = fr.name.split('/')[2].split('.')[0]

        soup = BeautifulSoup(doc, 'html.parser')
        content = soup.find("pre").get_text().encode('utf-8')

        doc_end = re.search(r'\sAM|\sPM', content)
        if doc_end:
            content = content[:doc_end.end()]

        content = content.replace('\n',' ')
        content = content.strip()

        transformed_content = transformText(content, True, True)
        write_to_corpus(transformed_content,docID)

