"""Jalankan python main.py untuk menu interaktif."""
import argparse
import json
from pathlib import Path
from ir_system.engine import SearchEngine

ROOT = Path(__file__).resolve().parent

def show(results):
    if not results:
        print('Tidak ditemukan dokumen relevan (query kosong, stopword, atau istilah tidak ada).')
    for result in results:
        print(f"\n{result['rank']}. [{result['source']}] {result['title']}")
        print(f"   ID: {result['doc_id']} | Cosine: {result['score']:.6f}")
        print('   ' + ' '.join(result['snippet'].split()))

def main():
    parser = argparse.ArgumentParser(description='Multi-Dataset Information Retrieval')
    parser.add_argument('--datasets', type=Path, default=ROOT/'datasets')
    parser.add_argument('--index', type=Path, default=ROOT/'indexdir')
    parser.add_argument('--build', action='store_true', help='Bangun index lalu keluar')
    parser.add_argument('--query', help='Cari query lalu keluar')
    args = parser.parse_args()
    engine = SearchEngine(args.index)
    try:
        if args.build:
            print(json.dumps(engine.build(args.datasets), indent=2)); return
        if args.index.exists():
            print('Memuat index dan representasi BoW...')
            engine.load()
        if args.query is not None:
            show(engine.search(args.query)); return
        while True:
            print('\n=== INFORMATION RETRIEVAL SYSTEM ===\n[1] Load & Index Dataset\n[2] Search Query\n[3] Exit\n===================================')
            choice = input('Pilihan: ').strip()
            try:
                if choice == '1':
                    print('Memproses kelima dataset. Mohon tunggu...')
                    print(json.dumps(engine.build(args.datasets), indent=2))
                elif choice == '2':
                    show(engine.search(input('Query: ')))
                elif choice == '3':
                    break
                else:
                    print('Pilihan tidak valid. Masukkan 1, 2, atau 3.')
            except (ValueError, OSError) as error:
                print(f'Gagal: {error}')
    except (ValueError, OSError) as error:
        parser.exit(1, f'Gagal: {error}\n')
    except (EOFError, KeyboardInterrupt):
        print('\nProgram dihentikan.')

if __name__ == '__main__':
    main()
