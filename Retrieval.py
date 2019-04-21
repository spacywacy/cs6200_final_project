import Indexer
from Indexer import number_of_terms1
import math
from math import log
import os
import nltk
import string
from nltk.stem import PorterStemmer

parsed_queries = []
number_of_terms1 = dict()
query_freq = dict()
index_dict = dict()

def generate_snippet(query, docID, sentence_dict_origin, parsed_sentence_dict, highlight=True):
  sentences = parsed_sentence_dict[docID]
  max_factor = 0
  max_factor_index = -1

  for idx, sentence in enumerate(sentences):
    sig_factor = calculate_sentence_significance(query, sentence)
    if sig_factor > max_factor:
      max_factor = sig_factor
      max_factor_index = idx
  print "generate snippet for " + docID + "..." + str(max_factor) + " " + str(max_factor_index)
  if max_factor_index >= 0:
    snippet = sentence_dict_origin[docID][max_factor_index]
  else:
    snippet = ""
  
  if highlight and len(snippet) > 0:
    query_token = query.split()
    snippet_token = snippet.split()
    highlighted = []
    for word in snippet_token:
      if word.translate(None, string.punctuation).lower() in query_token:
        word = "*" + word + "*"
      highlighted.append(word)
    snippet = " ".join(highlighted)
  return snippet

def calculate_sentence_significance(query, sentence):
  ps = PorterStemmer()
  query_token = query.split()
  sentence_token = sentence.split()
  # stemmed_query = list(map(lambda qt: ps.stem(qt), query_token))
  # stemmed_sentence = list(map(lambda st: ps.stem(st), sentence_token))
  return calculate_span_factor(query_token, sentence_token)
  # return calculate_span_factor(stemmed_query, stemmed_sentence)


def calculate_span_factor(query_array, sentence_array):
  match_count = 0
  match_index = []
  for idx, word in enumerate(sentence_array):
    if word in query_array:
      match_count += 1
      match_index.append(idx)

  if len(match_index) == 0:
    return 0
  if len(match_index) == 1:
    return 1.0 / len(sentence_array)

  return float(match_count * match_count) / (match_index[len(match_index)-1] - match_index[0] + 1)


def write_results_to_file(model, res_dict , query_id, query, show_snippet=False):
    with open("doc_sentence_dict_parsed.txt", 'r') as fin:
        # use eval to read input file as dictionary
      parsed_sentence_dict = eval(fin.read())

    with open("doc_sentence_dict_origin.txt", 'r') as fin:
      sentence_dict_origin = eval(fin.read())
  
    if not os.path.exists('results'):
        os.mkdir('results')

    ranking = 1

    if not os.path.exists('results/'+model):
        os.mkdir('results/'+model)

    f = open('results/'+model+'/'+model+'-' + str(query_id) + ".txt", 'w')
    if show_snippet:
      f.write("ranking\tQueryID\tDOC\tScore\tSnippet\n")
    else:
      f.write("ranking\tQueryID\tDOC\tScore\n")
    
    for k in sorted(res_dict, key=res_dict.get , reverse=True)[:100]:
      if show_snippet:
        docID = k
        snippet = generate_snippet(query, docID, sentence_dict_origin, parsed_sentence_dict)
        f.write(str(ranking)+"\t"+ str(query_id)+"\t"+k +"\t"+ str(res_dict[k])+ "\t" + snippet + "\n")
      else:
        f.write(str(ranking)+"\t"+ str(query_id)+"\t"+k +"\t"+ str(res_dict[k])+"\n")
      ranking = ranking+1

def write_queries_to_file(filename, queries):
    f = open(filename +".txt", 'w')
    for query in queries:
        f.write(query+"\n")
    f.close()

def read_query_doc():
    global parsed_queries
    fr = open('test-collection/cacm.query.txt', 'r')
    queries = fr.read()
    while queries.find('<DOC>') != -1:
        query = queries[queries.find('</DOCNO>') + 8 : queries.find('</DOC>')]
        query = query.strip().replace('\n'," ")
        new_query = Indexer.transformText(query, True, True)
        parsed_queries.append(new_query)
        queries = queries[queries.find('</DOC>') + 6 : ]
    write_queries_to_file("parsed-queries",parsed_queries)

def read_query_doc_stem():
    global parsed_queries_stem
    parsed_queries_stem = (line.rstrip('\n') for line in open('test-collection/cacm_stem.query.txt', 'r'))



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


def computAvgLen():
  path = os.getcwd() + '/articles/'
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

def BM25(index_dict, query, query_id):
  result_dict = dict()
  (avg_len, total, len_dict) = computAvgLen()

  for docID in len_dict:
    result_dict[docID] = calculat_BM25_score(docID, index_dict, query, avg_len, total, len_dict)
  write_results_to_file('BM25', result_dict, query_id, query)

def terms_in_collection():
    total_count = 0
    for doc in number_of_terms1:
        total_count = total_count + number_of_terms1[doc]
    return total_count


def build_query_freq(query):
    query_freq = dict()
    for w in query.split(" "):
        if w.strip():
            if w in query_freq:
                query_freq[w] += 1
            else:
                query_freq[w] = 1
    return query_freq


def QLM(index_dict, query , query_id):
    QLM_dict = dict()
    c = terms_in_collection()
    query_freq = build_query_freq(query)

    for q_term in query_freq:
        if (q_term,) in index_dict:
            cq = 0
            for docID in index_dict[(q_term,)]:
                cq = cq + len(index_dict[(q_term,)][docID])

            for docID in index_dict[(q_term,)]:
                d = number_of_terms1[docID]
                fq = len(index_dict[(q_term,)][docID])

                part_1 = float(1 - 0.35) * (float(fq)/float(d))
                part_2 = float(0.35) * (float(cq)/float(c))

                if docID in QLM_dict:
                    QLM_dict[docID] = QLM_dict[docID] + math.log(part_1 + part_2)
                else:
                    QLM_dict[docID] = math.log(part_1 + part_2)

    write_results_to_file('QLM', QLM_dict , query_id, query)

def main():
    global number_of_terms1
    global index_dict

    print "Select 1 for BM25"
    print "Select 2 for tf-idf"
    print "select 3 for query likelihood"
    print "select 4 for BM25 with stemmed corpus and quires"

    choice = input("Choose retrieval model")

    if choice == 4 or choice == 5:
      Indexer.build_stem()

    if choice != 4 and choice != 5:
      print "Parsing the corpus ... "
      Indexer.parse_corpus()

      print "Building the index ... "
      Indexer.build()



    number_of_terms1 = Indexer.number_of_terms1
    index_dict = Indexer.index_dict

    print "Reading queries from query doc ..."
    read_query_doc()
    read_query_doc_stem()

    query_id = 1
    if choice == 4:
      for query in parsed_queries_stem:
        BM25(index_dict, query, query_id)
        query_id = query_id + 1

    if choice == 5:
      for query in parsed_queries_stem:
        tf_idf(index_dict , number_of_terms1, query, query_id)
        query_id += 1

    for query in parsed_queries:
        if choice == 1:
            BM25(index_dict, query, query_id)
        elif choice == 2:
            tf_idf(index_dict , number_of_terms1, query, query_id)
        else:
            QLM(index_dict, query, query_id)
        query_id = query_id + 1



if __name__ == '__main__':
    main()
