"""Whoosh mengumpulkan kandidat; BoW cosine menentukan ranking akhir."""
import csv
import json
import shutil
import tempfile
from collections import Counter
from pathlib import Path
from time import perf_counter

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from whoosh import index
from whoosh.analysis import SpaceSeparatedTokenizer
from whoosh.fields import Schema, ID, TEXT, NUMERIC
from whoosh.query import Or, Term
from .preprocessing import preprocess

SOURCES = ('etd-usk', 'etd-ugm', 'kompas', 'tempo', 'mojok')

class SearchEngine:
    def __init__(self, index_dir):
        self.index_dir = Path(index_dir)
        self.ix = None
        self.vectorizer = None
        self.matrix = None
        self.docs = []

    def build(self, dataset_dir):
        """Validasi semua sumber sebelum membangun index pengganti."""
        start = perf_counter()
        root = Path(dataset_dir)
        docs, counts = [], Counter()
        skipped = 0
        for source in SOURCES:
            files = sorted((root / source).glob('*.csv'))
            if not files:
                raise ValueError(f'Dataset {source} tidak ditemukan di {root}.')
            for file in files:
                with file.open(encoding='utf-8-sig', newline='') as stream:
                    reader = csv.DictReader(stream)
                    if not {'judul', 'konten'} <= set(reader.fieldnames or []):
                        raise ValueError(f'{file}: wajib memiliki kolom judul dan konten.')
                    for row_no, row in enumerate(reader, 2):
                        title = (row.get('judul') or '').strip()
                        content = (row.get('konten') or '').strip()
                        clean = preprocess(title + ' ' + content)
                        if not clean:
                            skipped += 1
                            continue
                        docs.append(dict(doc_id=f'{source}/{file.name}:{row_no}',
                                         source=source, title=title or '(Tanpa judul)',
                                         content=content, clean=clean, row_id=len(docs)))
                        counts[source] += 1
            if not counts[source]:
                raise ValueError(f'Dataset {source} tidak memiliki dokumen valid.')
        vectorizer = CountVectorizer(tokenizer=str.split, token_pattern=None,
                                     preprocessor=None, lowercase=False)
        matrix = vectorizer.fit_transform(d['clean'] for d in docs)
        schema = Schema(doc_id=ID(stored=True, unique=True), source=ID(stored=True),
                        title=TEXT(stored=True), content=TEXT(stored=True),
                        clean=TEXT(stored=True, analyzer=SpaceSeparatedTokenizer()),
                        row_id=NUMERIC(stored=True))
        self.index_dir.parent.mkdir(parents=True, exist_ok=True)
        temp = Path(tempfile.mkdtemp(prefix='ir_build_', dir=self.index_dir.parent))
        try:
            ix = index.create_in(temp, schema)
            writer = ix.writer()
            for doc in docs:
                writer.add_document(**doc)
            writer.commit()
            ix.close()
            if self.ix is not None:
                self.ix.close()
            if self.index_dir.exists():
                shutil.rmtree(self.index_dir)
            temp.rename(self.index_dir)
        finally:
            if temp.exists():
                shutil.rmtree(temp)
        self.ix = index.open_dir(self.index_dir)
        self.docs, self.vectorizer, self.matrix = docs, vectorizer, matrix
        return dict(total=len(docs), per_source=dict(counts), skipped=skipped,
                    vocabulary=len(vectorizer.vocabulary_),
                    nonzero=int(matrix.nnz), seconds=perf_counter()-start)

    def load(self):
        """Rekonstruksi BoW dari teks bersih tersimpan, tanpa pickle."""
        self.ix = index.open_dir(self.index_dir)
        with self.ix.searcher() as searcher:
            self.docs = sorted(searcher.all_stored_fields(), key=lambda d:d['row_id'])
        self.vectorizer = CountVectorizer(tokenizer=str.split, token_pattern=None,
                                         preprocessor=None, lowercase=False)
        self.matrix = self.vectorizer.fit_transform(d['clean'] for d in self.docs)

    def search(self, query, top_k=5):
        if self.ix is None:
            raise ValueError('Index belum tersedia. Pilih menu 1 terlebih dahulu.')
        terms = preprocess(query).split()
        if not terms:
            return []
        vector = self.vectorizer.transform([' '.join(terms)])
        if vector.nnz == 0:
            return []
        # OR tanpa limit: semua dokumen dengan overlap harus ikut cosine.
        query_object = Or([Term('clean', t) for t in sorted(set(terms))])
        with self.ix.searcher() as searcher:
            candidates = [hit['row_id'] for hit in searcher.search(query_object, limit=None)]
        if not candidates:
            return []
        scores = cosine_similarity(vector, self.matrix[candidates]).ravel()
        ranked = sorted(zip(candidates, scores),
                        key=lambda pair: (-float(pair[1]), self.docs[pair[0]]['doc_id']))
        return [dict(rank=rank, doc_id=self.docs[i]['doc_id'],
                     source=self.docs[i]['source'], title=self.docs[i]['title'],
                     score=float(score), snippet=self.docs[i]['content'][:240])
                for rank, (i, score) in enumerate(ranked[:top_k], 1) if score > 0]
