import Indexer
import Retrieval
from Evaluation import Eval
from query_based_stem import Qbase_stem
import task3A
import os


def main():
	result_evaluations()
	
def result_evaluations():
	result_dir = 'results_for_eval'
	for run_dir in os.listdir(result_dir):
		if run_dir[0] == '.':
			continue

		full_run_dir = os.path.join(result_dir, run_dir)
		table_fname = '{}_precison_recall.txt'.format(run_dir)

		eval_ = Eval(table_fname=table_fname,
					max_result=20,
					result_dir=full_run_dir)

		map_ = eval_.MAP()
		mrr_ = eval_.MRR()
		avg_pak_5 = eval_.avg_PatK(5)
		avg_pak_20 = eval_.avg_PatK(20)
		print ''
		print run_dir
		print 'map:', map_
		print 'mrr:', mrr_
		print 'avg_pak_5:', avg_pak_5
		print 'avg_pak_20:', avg_pak_20

		eval_.precision_recall(20)

		metric_fname = 'evaluation/{}_metrics.txt'.format(run_dir)
		with open(metric_fname, 'w') as m_f:
			m_f.write('MAP: {}'.format(map_) + '\n')
			m_f.write('MRR: {}'.format(mrr_) + '\n')
			m_f.write('Average P@K(K=5): {}'.format(avg_pak_5) + '\n')
			m_f.write('Average P@K(K=20): {}'.format(avg_pak_20) + '\n')
			



def index_retri(method):
	Indexer.parse_corpus()
	Indexer.build()
	number_of_terms1 = Indexer.number_of_terms1
	index_dict = Indexer.index_dict
	parsed_queries = Retrieval.read_query_doc()
	query_stem = True

	if query_stem:
		qs = Qbase_stem()
		print('done building stem classes')

	query_id = 1
	for query in parsed_queries:

		if query_stem:
			query = qs.stem_expand(query)

		if method == 'TFIDF':
			Retrieval.tf_idf(index_dict, number_of_terms1, query, query_id)
		elif method == 'BM25':
			Retrieval.BM25(index_dict, query, query_id)
		elif method == 'QLM':
			Retrieval.QLM(index_dict, query, query_id)

		query_id += 1

def stop_and_stem():
	global stop_words
	stop_words = Indexer.read_stop_words()
	print "Parsing the corpus"
	task3A.parse_corpus()
	print "creating the index"
	index_dict, number_of_terms1 = task3A.build()
	print "Parsing the queries"
	queries = task3A.parse_queries()
	Retrieval.write_queries_to_file("stopped-queries", queries)
	query_id = 1
	qs = Qbase_stem()
	print('done building stem classes')

	for query in queries:
		query = qs.stem_expand(query)
		task3A.tf_idf(index_dict , number_of_terms1, query, query_id)
		query_id = query_id + 1

def eval_test(method):
	#evaluation
	table_fname = 'precison_recall_{}.txt'.format(method)
	eval_ = Eval(method, table_fname=table_fname, max_result=10, result_dir='stop-results/TFIDF')
	map_ = eval_.MAP()
	mrr_ = eval_.MRR()
	avg_pak = eval_.avg_PatK(5)
	print 'map:', map_
	print 'mrr:', mrr_
	print 'avg_pak:', avg_pak

	eval_.precision_recall(20)

	




















if __name__ == '__main__':
	main()


















