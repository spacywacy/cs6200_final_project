import nltk
import os
from nltk.stem.porter import *


def tokenize_doc(text, punctuation=True, case_fold=True):
	tokens = nltk.word_tokenize(text)
	
	if case_fold:
		for i in range(len(tokens)):
			tokens[i] = tokens[i].lower()

	if punctuation:
		tokens_clean = []
		for i in range(len(tokens)):
			#check hyphen
			if '-' in tokens[i]:
				striped_ = ''.join(tokens[i].split('-'))
				if striped_.isalnum():
					tokens_clean.append(tokens[i])

			#check alphanum
			elif tokens[i].isalnum():
				tokens_clean.append(tokens[i])

		tokens = tokens_clean

	return tokens


class Qbase_stem():

	def __init__(self):
		self.corpus_dir = 'articles'
		self.stem = PorterStemmer().stem
		self.stem_class = {} #{stem_term: [term_variations]}; term variations in a unique set
		self.stem_class_lookup = {} #{orignial_term: [term_variations]}
		self.loop_corpus()
		self.clean_stem_class()
		self.build_lookup()

		for key, val in self.stem_class_lookup.items():
			print(key, val)

	def loop_corpus(self):
		for fname in os.listdir(self.corpus_dir):
			full_path = os.path.join(self.corpus_dir, fname)
			print(fname)
			with open(full_path, 'r') as f:
				tokens = tokenize_doc(f.read())
				self.build_stem_class(tokens)

	def build_stem_class(self, tokens):
		for token in tokens:
			stemmed = self.stem(token)
			self.stem_class[stemmed] = self.stem_class.get(stemmed, []) + [token]

	def clean_stem_class(self):
		#remove duplitcates in term variations
		for key in self.stem_class.keys():
			self.stem_class[key] = list(set(self.stem_class[key]))

	def build_lookup(self):
		for stem_term, term_vars in self.stem_class.items():

			for term in term_vars:
				self.stem_class_lookup[term] = term_vars

	def stem_expand(self, query_str):
		q_tokens = tokenize_doc(query_str)
		expansion = []
		for token in q_tokens:
			expansion += self.stem_class_lookup.get(token, [])

		expanded = list(set(q_tokens + expansion))
		return ' '.join(expanded)

				










if __name__ == '__main__':
	s = 'I am interested in articles written either by Prieve or Udo Pooch'
	qs = Qbase_stem()
	exp_s = qs.stem_expand(s)
	print(exp_s)



















