import os

class Eval():

	def __init__(self, retr_method, table_fname=None, max_result=999):
		#io
		self.eval_table_dir = 'evaluation'
		if not os.path.exists(self.eval_table_dir):
			os.makedirs(self.eval_table_dir)
		self.query_result_dir = 'results/' + retr_method
		self.rel_dir = 'test-collection/cacm.rel.txt'
		self.table_fname = table_fname

		#data structures
		self.query_list = [] #[query_id]
		self.result_lookup = {} #{query_id: [doc_id]}
		self.rel_lookup = {} #{query_id: [rel_doc_id]}
		self.max_result = max_result
		self.parse_rel()
		self.parse_query()
		
		

	def parse_rel(self):
		with open(self.rel_dir, 'r') as f:
			for line in f:
				items = line[:-1].split(' ')
				query_id = int(items[0])
				self.rel_lookup[query_id] = self.rel_lookup.get(query_id, []) + [items[2]]

		self.query_list = list(self.rel_lookup.keys())
		self.query_list.sort()

	def parse_query(self):
		for fname in os.listdir(self.query_result_dir):
			full_path = os.path.join(self.query_result_dir, fname)

			#read search query result for a particular query from file
			with open(full_path, 'r') as f:
				n_results = 0
				results = []
				query_id = -1
				for line in f:
					#enforce maximum result for each query
					if n_results > self.max_result:
						break

					#get doc ids for a query
					row = line[:-1].split('\t')
					results.append(row[2])
					n_results += 1

					#get query id
					if n_results < 3 and row[1].isdigit():
						query_id = int(row[1])

				self.result_lookup[query_id] = results[1:] #store results in dictionary


	def MAP(self, mrr=False):
		map_ = 0.0

		for query_id in self.query_list:
			#do search & get references
			reference = self.rel_lookup[query_id]
			results = self.result_lookup[query_id]
			
			#calculate average precision
			n_results = 0
			n_rel = 0
			avg_precision = 0.0
			for item in results:
				n_results += 1
				if item in reference:
					n_rel += 1
					if mrr:
						avg_precision += float(n_rel) / float(n_results)
						break
						
					avg_precision += float(n_rel) / float(n_results)

			if n_rel != 0: #check if there is a relevant query resu
				avg_precision = avg_precision / n_rel
				map_ += avg_precision #add average precision to overall MAP
			else:
				avg_precision = 0
			#print('query id: {}, n_rel: {}, precision: {}'.format(query_id, n_rel, avg_precision))

		return map_ / len(self.query_list)


	def MRR(self):
		return self.MAP(mrr=True)

	def avg_PatK(self, k):
		#calculates average precision at result position k over all queries
		avg_pak = 0.0
		for query_id in self.query_list:
			#do search & get references
			reference = self.rel_lookup[query_id]
			results = self.result_lookup[query_id]

			#calculate p at k
			n_rel = 0
			for item in results[:k]:
				if item in reference:
					n_rel +=1

			avg_pak += float(n_rel) / float(k)

		return avg_pak / len(self.query_list)

	def precision_recall(self, k):
		#for each run, calculate precision & recall at rank position k for each query
		#each row: (query_id, precision, recall)
		#table: [row1, row2,...,row_n]
		table = []

		for query_id in self.query_list:
			#do search & get references
			reference = self.rel_lookup[query_id]
			results = self.result_lookup[query_id]
			
			#git number of relevant docs
			n_rel = 0
			for item in results[:k]:
				if item in reference:
					n_rel +=1

			#calculate precision & recall
			precision = float(n_rel) / float(k)
			recall = float(n_rel) / float(len(reference))

			#append results
			table.append((query_id, precision, recall))

		#write table to file
		if self.table_fname:
			table_full_path = os.path.join(self.eval_table_dir, self.table_fname)
			with open(table_full_path, 'w') as f:
				f.write('query_id\tprecision\trecall\n')
				for row in table:
					line = '\t'.join([str(x) for x in row]) + '\n'
					f.write(line)
			print('Written table to file')

		return table



if __name__ == '__main__':
	pass













