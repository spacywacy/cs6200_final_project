import os
import nltk
import Indexer
import Retrieval

nltk.download('punkt')

stop_words = []
parsed_queries = []
searchResult = dict()
count = 0
expanded_queries = []


def runSearchQuery(searchTerm , result, nVal):
    global count
    diceRes = dict()

    # for each term in the result dictionary
    for k,v in result.items():
        termList = result[k]
        count = 0

        # finding the common docIDs for the term in result dictionary with all the terms in the search query
        # and evaluating the dice coefficent using the formula (2 * n(a,b) / n(a)+n(b))
        for word in searchTerm.split():
            if word in result:
                count = count+1
                docList = result.get(word)
                commonDocs = list(set(docList) & set(termList))
                diceCalc = 2.00 * len(commonDocs)/(len(docList) + len(termList))
                val = diceRes.setdefault(k, 0.0)
                diceRes[k] += diceCalc
        diceRes[k] = diceRes[k]/count

    # sorting the dice results dictionary in descending order of the dice coefficient value
    sortedDice = sorted(diceRes.items(), key=lambda x: x[1], reverse=True)

    expanded_query = searchTerm
    for k,v in sortedDice[0:nVal]:
        if not k in expanded_query:
            expanded_query = expanded_query + " "+k
    expanded_queries.append(expanded_query)


def generateUnigramDocFreq(stopWords, queryId):
    result = dict()
    for f in os.listdir('n10/'+ str(queryId) + "/"):
        fRead = open('n10/' + str(queryId) + '/' + f, 'r')
        doc = fRead.read()
        docID = fRead.name.split('/')[2].split('.')[0]
        tokens = nltk.word_tokenize(doc)
        termFreq = nltk.FreqDist(tokens)

        # for each term the documentIDs are stored in result dictionary
        for k, v in termFreq.most_common():
            if k not in stopWords:
                result.setdefault(k,set()).add(docID);
        fRead.close()
    return result

def main():
    global stop_words
    global parsed_queries

    Indexer.read_stop_words()
    Retrieval.read_query_doc()
    # generate the unigrams from the lucene results for k=10 or 20
    stop_words = Indexer.stop_words
    parsed_queries = Retrieval.parsed_queries

    # evaluating the dice coefficient on the search query with n=8 or 6
    query_id = 0
    for query in parsed_queries:
        query_id = query_id + 1
        result = generateUnigramDocFreq(stop_words, query_id)
        runSearchQuery(query.lower(), result, 8)

    Retrieval.write_queries_to_file("expanded-queries", expanded_queries)

if __name__ == '__main__':
    main()
