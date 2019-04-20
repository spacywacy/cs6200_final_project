import Indexer
import Retrieval
from Evaluation import Eval


def main():
	method = 'TFIDF'
	#index_retri()
	eval_test(method)

def index_retri():
	Indexer.parse_corpus()
	Indexer.build()
	number_of_terms1 = Indexer.number_of_terms1
	index_dict = Indexer.index_dict
	parsed_queries = Retrieval.read_query_doc()

	query_id = 1
	for query in parsed_queries:
		Retrieval.tf_idf(index_dict, number_of_terms1, query, query_id)
		query_id += 1

def eval_test(method):
	#evaluation
	table_fname = 'precison_recall.txt'
	eval_ = Eval(method, table_fname=table_fname, max_result=10)
	map_ = eval_.MAP()
	mrr_ = eval_.MRR()
	avg_pak = eval_.avg_PatK(5)
	print('map:', map_)
	print('mrr:', mrr_)
	print('avg_pak:', avg_pak)

	eval_.precision_recall(20)

	




















if __name__ == '__main__':
	main()


















