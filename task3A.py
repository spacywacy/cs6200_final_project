import Indexer
import Retrieval
from Indexer import stop_words
import os
from py2casefold import casefold
import nltk
from nltk.util import ngrams
from math import log
import math

stop_words = []
position_index = dict()
number_of_terms1 = dict()
index_dict = dict()
queries = []

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
    path = os.getcwd() + '/articles-stopped/'
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

def transform_text(parseText, punctuations, casefolding):
    newcontent = ''
    if casefolding:
        parseText = casefold(parseText.decode('utf-8'))
    if punctuations:
        for letter in parseText:
            if letter.isalnum() or letter == '-' or letter == ' ':
                newcontent += letter
    return newcontent

def write_to_file(file, docID):
    # create corpus folder
    if not os.path.exists('articles-stopped'):
        os.mkdir('articles-stopped')

    filename = ''
    for chr in docID:
        if chr.isalnum() or chr == '-':
            filename += chr

    # write to the file
    wcorpus = open('articles-stopped/' + filename + ".txt", 'w')
    wcorpus.write(file)
    wcorpus.close()

def parse_corpus():
    for f in os.listdir('articles/'):
        fr = open('articles/' + f, 'r')
        doc = fr.read()
        docID = fr.name.split('/')[1].split('.')[0]
        doc = doc.replace('\n',' ')
        doc = doc.strip()
        stopped_file = stopping_on_file(doc)
        write_to_file(stopped_file, docID)

def stopping_on_file(transformed_txt):
    global stop_words
    stopped_text = ""
    for word in transformed_txt.split():
        word = word.strip()
        if word not in stop_words:
            stopped_text = stopped_text + " " + word
    return stopped_text

def parse_queries():
    global queries
    with open('parsed-queries.txt') as f:
        for line in f:
            new_line = ""
            for word in line.split():
                if word not in stop_words:
                    new_line = new_line + word + " "
            new_line = new_line.rstrip()
            queries.append(new_line)
    f.close()
    return queries

def build_query_freq(query):
    query_freq = dict()
    for w in query.split(" "):
        if w.strip():
            if w in query_freq:
                query_freq[w] += 1
            else:
                query_freq[w] = 1
    return query_freq


def write_results_to_file(model, res_dict, query_id, query):
    if not os.path.exists('stop-results'):
        os.mkdir('stop-results')

    ranking = 1

    if not os.path.exists('stop-results/' + model):
        os.mkdir('stop-results/' + model)

    f = open('stop-results/' + model + '/' + model + '-' + str(query_id) + ".txt", 'w')
    f.write("ranking\tQueryID\tDOC\tScore\n")
    for k in sorted(res_dict, key=res_dict.get, reverse=True)[:100]:
        f.write(str(ranking) + "\t" + str(query_id) + "\t" + k + "\t" + str(res_dict[k]) + "\n")
        ranking = ranking + 1


def tf_idf(index_dict, number_of_terms1, query, query_id):
    tfidf_dict = dict()
    tfidf_term_dict = dict()

    query_freq = build_query_freq(query)

    for q_term in query_freq:
        if (q_term,) in index_dict:
            fij = 0
            fik = 0

            N = float(len(number_of_terms1))
            nk = float(len(index_dict[(q_term,)].keys()))
            idf = math.log(N/nk)

            for doc in index_dict[(q_term),]:
                fik = float(len(index_dict[(q_term,)][doc]))
                fij = float(number_of_terms1[doc])
                tf = fik/fij
                if (q_term,) in tfidf_term_dict:
                    tfidf_term_dict[(q_term,)][doc] = tf * idf
                else:
                    tfidf_term_dict[(q_term,)] = {}
                    tfidf_term_dict[(q_term,)][doc] = tf * idf

    for q_term in query_freq:
        if (q_term,) in index_dict:
            for doc in index_dict[(q_term,)]:
                doc_score = 0
                doc_score = doc_score + tfidf_term_dict[(q_term,)][doc]
                if doc in tfidf_dict:
                    tfidf_dict[doc] = tfidf_dict[doc] + doc_score
                else:
                    tfidf_dict[doc] = doc_score

    write_results_to_file('TFIDF', tfidf_dict, query_id, query)


def calculat_BM25_score(doc_id, index_dict, query, avg_len, total, len_dict):
    K1 = 1.2
    B = 0.75
    K2 = 100
    R = 0
    r = 0

    query_terms = query.split()
    BM25_score = 0
    query_freq = build_query_freq(query)
    K = K1 * ((1 - B) + B * len_dict[doc_id] / avg_len)
    for term in query_terms:
        if (term,) not in index_dict:
            continue

        if doc_id not in index_dict[(term,)]:
            continue
        # term frequency
        tf = len(index_dict[(term,)][doc_id])
        # query term frequnecny
        qf = query_freq[term]
        # number of documents containing term
        df = len(index_dict[(term,)])
        BM25_score += log(((r + 0.5) / (R - r + 0.5)) \
                          / ((df - r + 0.5) / (total - df - R + r + 0.5))) \
                      * ((K1 + 1) * tf) / (K + tf) \
                      * ((K2 + 1) * qf) / (K2 + qf)

    return BM25_score


def computAvgLen():
    path = os.getcwd() + '/articles-stopped/'
    avg_len = 0
    len_dict = {}
    for filename in os.listdir(path):
        # if count > 10:
        #   break

        # ignore non txt file
        if ".txt" not in filename:
            continue

        fullpath = path + filename

        with open(fullpath, 'r') as content_file:
            content = content_file.read()
            length = len(content.split())
            doc_id = filename.rstrip(".txt")
            avg_len = avg_len + length
            len_dict[doc_id] = length
    total = len(len_dict)
    avg_len = avg_len / total
    return (avg_len, total, len_dict)

def BM25(index_dict, query, query_id):
    result_dict = dict()
    (avg_len, total, len_dict) = computAvgLen()

    for docID in len_dict:
        result_dict[docID] = calculat_BM25_score(docID, index_dict, query, avg_len, total, len_dict)
    write_results_to_file('BM25', result_dict, query_id, query)


def main():
    global stop_words
    stop_words = Indexer.read_stop_words()
    print "Parsing the corpus"
    parse_corpus()
    print "creating the index"
    build()
    print "Parsing the queries"
    queries = parse_queries()
    Retrieval.write_queries_to_file("stopped-queries", queries)
    query_id = 1
    for query in queries:
        tf_idf(index_dict , number_of_terms1, query, query_id)
        query_id = query_id + 1

    query_id = 1
    for query in queries:
        BM25(index_dict, query, query_id)
        query_id = query_id + 1

if __name__ == '__main__':
    main()