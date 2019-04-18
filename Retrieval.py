import Indexer
from Indexer import number_of_terms1
import math
import os

parsed_queries = []
number_of_terms1 = dict()
query_freq = dict()
index_dict = dict()

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

def tf_idf():
    pass


def BM25():
    pass


def terms_in_collection():
    total_count = 0
    for doc in number_of_terms1:
        total_count = total_count + number_of_terms1[doc]
    return total_count


def build_query_freq(query):
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

    ranking = 1
    if not os.path.exists('results'):
        os.mkdir('results')

    f = open('results/QLM-' + str(query_id) + ".txt", 'w')
    f.write("ranking\tQueryID\tDOC\n")
    for k in sorted(QLM_dict, key=QLM_dict.get , reverse=True)[:100]:
        f.write(str(ranking)+"\t"+ str(query_id)+"\t"+k +"\n")

def main():
    global number_of_terms1
    global index_dict

    print "Select 1 for BM25"
    print "Select 2 for tf-idf"
    print "select 3 for query likelihood"

    choice = input("Choose retrieval model")

    print "Parsing the corpus ... "
    Indexer.parse_corpus()

    print "Building the index ... "
    Indexer.build()

    number_of_terms1 = Indexer.number_of_terms1
    index_dict = Indexer.index_dict

    print "Reading queries from query doc ..."
    read_query_doc()

    query_id = 1
    for query in parsed_queries:
        if choice == 1:
            BM25()
        elif choice == 2:
            tf_idf()
        else:
            QLM(index_dict, query, query_id)
        query_id = query_id + 1

if __name__ == '__main__':
    main()