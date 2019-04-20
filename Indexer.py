import os
import nltk
from nltk.util import ngrams
from nltk import sent_tokenize
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
        if chr.isalnum() or chr == '-':
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
    doc_sentence_dict_origin = dict()
    parsed_sentence_dict = dict()
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

        sentences = sent_tokenize(content)
        doc_sentence_dict_origin[docID] = sentences
        parsed_sentences = []
        for sentence in sentences:
          tmp_sentence = transformText(sentence, True, True)
          parsed_sentences.append(tmp_sentence)
        parsed_sentence_dict[docID] = parsed_sentences

        transformed_content = transformText(content, True, True)
        write_to_corpus(transformed_content , docID)
    # self.doc_sentence_dict = doc_sentence_dict
    with open("doc_sentence_dict_origin" + ".txt", 'w+') as fout:
      fout.write(str(doc_sentence_dict_origin))

    with open("doc_sentence_dict_parsed" + ".txt", 'w+') as fout:
      fout.write(str(parsed_sentence_dict))


