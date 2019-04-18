import Indexer
from Indexer import number_of_terms1

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

def QLM(index_dict, query):
    col_term_count = terms_in_collection()
    query_freq = build_query_freq(query)

    for q_term in query_freq:
        if q_term in index_dict.keys():
            for docID in index_dict[q_term]:
                q_term_collection = q_term_collection + len(index_dict[q_term][docID])
            print q_term_collection
        else:
            print "not in index_dict "+str(q_term)

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

    for query in parsed_queries:
        if choice == 1:
            BM25()
        elif choice == 2:
            tf_idf()
        else:
            QLM(index_dict, query)


if __name__ == '__main__':
    main()