import math
from collections import Counter
import logging

class BM25:
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b

    def fit(self, corpus):
        self.corpus = corpus
        self.doc_len = [len(doc.split()) for doc in corpus]
        
        # Handle empty corpus
        if not self.doc_len:
            self.avg_doc_len = 0 
            self.doc_freqs = Counter()
            self.idf = {}
            return
        
        self.avg_doc_len = sum(self.doc_len) / len(self.doc_len)
        self.doc_freqs = Counter()
        for doc in corpus:
            self.doc_freqs.update(set(doc.split()))
        self.idf = {}
        for word, freq in self.doc_freqs.items():
            # smoothing to avoid division by zero
            self.idf[word] = math.log((len(corpus) - freq + 0.5) / (freq + 0.5 + 1e-10) + 1)

    def get_score(self, query, doc_index):
        score = 0
        doc = self.corpus[doc_index]
        doc_len = self.doc_len[doc_index]
        for word in query.split():
            if word not in doc:
                continue
            f = doc.count(word)
            # Add smoothing to avoid division by zero
            score += (self.idf.get(word, 0) * f * (self.k1 + 1)
                      / (f + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len) + 1e-10))
        return score

def rerank_results(results, query):
    corpus = [result['text'] for result in results]
    
    # Handle empty corpus
    if not corpus:
        logging.warning("Corpus is empty, skipping reranking.")
        return results
    
    bm25 = BM25()
    bm25.fit(corpus)
    
    for i, result in enumerate(results):
        result['bm25_score'] = bm25.get_score(query, i)
    
    return sorted(results, key=lambda x: x['bm25_score'], reverse=True)