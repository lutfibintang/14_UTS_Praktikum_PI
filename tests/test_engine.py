import csv
import tempfile
import unittest
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from ir_system.engine import SearchEngine, SOURCES
from ir_system.preprocessing import preprocess

class EngineTests(unittest.TestCase):
    def test_preprocessing(self):
        self.assertEqual(preprocess('<b>PENDIDIKAN</b> dan Matematika!'), 'pendidikan matematika')

    def test_ranking_persistence_and_empty_query(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for source in SOURCES:
                folder = root/'datasets'/source
                folder.mkdir(parents=True)
                with (folder/'data.csv').open('w',newline='',encoding='utf-8') as file:
                    writer = csv.writer(file); writer.writerow(['judul','konten'])
                    writer.writerows([['apel','apel jeruk'],['pisang','pisang'],['','dan yang']])
            engine = SearchEngine(root/'index')
            stats = engine.build(root/'datasets')
            self.assertEqual(stats['total'],10)
            self.assertEqual(stats['skipped'],5)
            self.assertEqual(engine.search('dan yang'),[])
            self.assertEqual(engine.search('xyzqq'),[])
            self.assertEqual(engine.search(''),[])
            result = engine.search('apel jeruk')
            full = cosine_similarity(engine.vectorizer.transform(['apel jeruk']),engine.matrix).ravel()
            self.assertEqual(len(result),5)
            self.assertAlmostEqual(result[0]['score'], float(max(full)))
            self.assertAlmostEqual(result[0]['score'],3/(10**0.5))
            restored = SearchEngine(root/'index'); restored.load()
            self.assertEqual(result, restored.search('apel jeruk'))
            with self.assertRaises(ValueError): restored.build(root/'missing')
            self.assertEqual(result, restored.search('apel jeruk'))
            restored.ix.close(); engine.ix.close()

if __name__ == '__main__': unittest.main()
