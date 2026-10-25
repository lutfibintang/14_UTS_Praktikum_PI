"""Uji semua sel dan menu notebook pada data kecil dari kelima sumber."""
import contextlib, csv, io, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
class NotebookTests(unittest.TestCase):
    def test_cells_and_cli(self):
        notebook = json.loads((ROOT/'main.ipynb').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for source in ('etd-usk','etd-ugm','kompas','tempo','mojok'):
                folder = root/'datasets'/source
                folder.mkdir(parents=True)
                with (folder/'data.csv').open('w',newline='',encoding='utf-8') as stream:
                    writer=csv.writer(stream);writer.writerow(['judul','konten'])
                    writer.writerows([['pendidikan matematika','pendidikan matematika siswa'],['lagu anime','lagu anime musik']])
            env={};capture=io.StringIO()
            with contextlib.redirect_stdout(capture):
                for cell in notebook['cells']:
                    source=''.join(cell['source'])
                    if cell['cell_type']!='code' or source.startswith('%pip'): continue
                    source=source.replace('BASE_DIR = Path.cwd()',f'BASE_DIR = Path({str(root)!r})')
                    exec(compile(source,'main.ipynb','exec'),env)
                original=env['engine'].search('lagu anime')
                env['engine'].load()
                self.assertEqual(original,env['engine'].search('lagu anime'))
                with patch('builtins.input',side_effect=['9','1','2','lagu anime','3']): env['menu_cli']()
                env['engine'].ix.close()
            self.assertEqual(len(original),5)
            self.assertIn('Pilih 1, 2, atau 3.',capture.getvalue())
            self.assertIn('Selesai.',capture.getvalue())
            self.assertTrue((root/'hasil_pengujian_notebook/results.json').exists())
if __name__=='__main__': unittest.main()
