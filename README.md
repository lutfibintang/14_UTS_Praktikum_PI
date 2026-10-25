# UTS Praktikum Penelusuran Informasi - Notebook + CLI

**Program utama: `main.ipynb`.** Notebook berisi preprocessing, BoW, Whoosh,
cosine similarity, pengujian, dan menu interaktif. `main.py` disertakan agar
antarmuka CLI yang diwajibkan PDF juga dapat dijalankan langsung dari terminal.

## Mulai dari notebook (VS Code)

1. Ekstrak seluruh ZIP, jangan membuka notebook langsung dari arsip.
2. Buka folder yang berisi `main.ipynb`, `main.py`, dan `datasets/` di VS Code.
3. Gunakan ekstensi Python dan Jupyter; pilih kernel Python pada notebook.
4. Jalankan sel instalasi, lalu sel-sel berikutnya dari atas ke bawah.
5. Bagian D nomor 7 membangun index penuh. Tunggu selesai; pemrosesan awal
   dapat memerlukan beberapa menit dan beberapa GB ruang disk.
6. Bagian E nomor 9: ubah `QUERY` untuk mencari dan melihat top-5.
7. Untuk demonstrasi **CLI wajib**, di bagian H nomor 13 ubah
   `JALANKAN_MENU = True`, jalankan sel, kemudian gunakan menu 1/2/3.
   Setelah selesai demonstrasi, ubah kembali False agar Run All tidak menunggu input.
8. Alternatif menjalankan CLI di terminal: `python main.py`.

Jupyter/IPython merupakan aplikasi untuk membuka notebook, bukan library tambahan
algoritma IR. Kode notebook hanya mengimpor standard library, pandas, Whoosh,
dan scikit-learn. Tabel hasil dicetak sebagai teks.

**Catatan index:** notebook dan main.py memakai folder `indexdir/` yang sama.
Jangan melakukan indexing dari dua proses bersamaan. Setelah perubahan dataset
atau preprocessing, bangun ulang index. Output notebook dikosongkan agar hasil
pada mesin pengguna dihitung ulang; bukti pengujian penuh sebelumnya tersedia
pada `hasil_pengujian/results.json` dan laporan.

## Pemetaan instruksi PDF

| Ketentuan | Implementasi |
|---|---|
| Python dan menu CLI 1/2/3 | main.ipynb bagian H; main.py |
| Lima dataset dalam satu folder | datasets/etd-usk, etd-ugm, kompas, tempo, mojok |
| Case folding, tokenisasi, stopword | Notebook C; ir_system/preprocessing.py |
| Bag of Words CountVectorizer | Notebook D; ir_system/engine.py |
| Whoosh indexing dan searching | Notebook D, fungsi build dan search |
| Cosine similarity dan top-5 | Notebook E; SearchEngine.search |
| Laporan PDF dengan enam bagian | Laporan_UTS_Praktikum_PI.pdf |
| README | Dokumen ini |

## Pengujian versi notebook

`python -m unittest discover -s tests -v` menjalankan pengujian mesin IR dan
notebook pada koleksi kecil terkontrol dari kelima sumber. Notebook juga memiliki
sel pengujian untuk seluruh dataset. Hasil penuh yang disertakan berasal dari
pengujian proyek awal; algoritma inti notebook dipertahankan identik.

## Dokumentasi CLI dan algoritma

Proyek UTS Praktikum Penelusuran Informasi - Informatika FMIPA USK.

**Isi sebelum dikumpulkan:** nomor kelompok, nama/NPM maksimal 3 anggota,
dan URL repository GitHub. Identitas belum diberikan sehingga tidak ditebak.

## 1. Instalasi dan menjalankan (Windows / VS Code)

Gunakan Python 3.10 atau lebih baru. Buka terminal di folder proyek (tempat main.py).

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

Tidak perlu mengaktifkan virtual environment sehingga tidak terhalang execution policy.
Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Pilih **1** untuk memuat semua CSV dan membuat index. Proses awal dapat memerlukan
beberapa menit dan RAM yang cukup untuk 49.484 dokumen. Sediakan setidaknya
6 GB ruang disk kosong untuk index dan file sementara; index tidak dimasukkan ke ZIP. Pilih **2**, ketik query,
lalu lihat maksimal lima hasil berupa judul, sumber, ID dokumen, skor, dan cuplikan.
Pilih **3** untuk keluar. Saat dijalankan kembali, index tersimpan dibuka dan BoW
dibangun kembali dari teks bersih. Setelah mengubah CSV atau stopword, pilih 1 kembali.

Di bawah ini `python` berarti interpreter virtual environment yang telah dipasang:

```bash
python main.py --build
python main.py --query "pendidikan matematika"
python main.py --datasets datasets --index indexdir
python evaluate.py
python -m unittest discover -s tests -v
```

## 2. Struktur

- `main.ipynb`: program utama dengan kode dan penjelasan per sel.
- `main.py`: menu CLI dan opsi noninteraktif.
- `ir_system/preprocessing.py`: normalisasi, case folding, tokenisasi, stopword.
- `ir_system/engine.py`: loader CSV, BoW, index Whoosh, pencarian dan cosine.
- `datasets/{etd-usk,etd-ugm,kompas,tempo,mojok}/data.csv`: seluruh dataset asli.
- `evaluate.py`: menjalankan delapan kasus uji dan menyimpan hasil aktual.
- `tests/test_engine.py`: uji rumus, preprocessing, penyimpanan index, dan input kosong.
- `hasil_pengujian/results.json`: bukti skor dan waktu aktual pada dataset penuh.
- `Laporan_UTS_Praktikum_PI.pdf`: laporan sesuai susunan tugas.
- `Laporan_UTS_Praktikum_PI.md`: isi laporan yang dapat diedit untuk identitas.
- `indexdir/`: dibuat otomatis; tidak disertakan agar paket lebih kecil.

## 3. Dataset

| Sumber | Baris awal |
|---|---:|
| etd-usk | 10000 |
| etd-ugm | 10000 |
| kompas | 10000 |
| tempo | 10000 |
| mojok | 9484 |
| Total | 49484 |

CSV harus UTF-8, memiliki header `judul,konten`. Setiap baris menjadi satu dokumen;
judul dan konten digabung tanpa bobot khusus. Satu folder sumber dapat memuat lebih
dari satu CSV. Lima folder wajib ada dan masing-masing harus berisi dokumen valid.
Baris tanpa token setelah preprocessing dilewati dan dihitung. Duplikat dipertahankan
agar jejak dataset asli tetap jelas. ID memuat sumber, nama CSV, dan nomor record
CSV (header nomor 1; bukan nomor baris fisik jika konten mengandung newline).

## 4. Pipeline dan algoritma

1. Baca semua CSV menggunakan library standar `csv`.
2. Normalisasi Unicode NFKC, decode HTML entity, hapus tag, lowercase, tokenisasi
   alfanumerik Unicode, buang stopword Indonesia/Inggris dari daftar eksplisit.
3. `CountVectorizer` membuat sparse Bag of Words dengan hitungan mentah, bukan TF-IDF.
4. Whoosh menyimpan ID, sumber, judul, isi, teks bersih, dan nomor baris matriks.
5. Query menjalani preprocessing yang sama. Whoosh OR mencari dokumen yang memuat
   setidaknya satu token, dengan `limit=None` agar ranking awal Whoosh tidak membuang
   calon hasil cosine terbaik. Simbol query dianggap teks, bukan operator Boolean.
6. `cosine_similarity(q, D_kandidat)` menghitung skor. Urutkan skor menurun;
   skor sama diurutkan berdasarkan ID. Tampilkan maksimal 5 dokumen berskor positif.

Rumus: `cos(q,d) = sum(q_i*d_i) / (sqrt(sum(q_i^2))*sqrt(sum(d_i^2)))`.
Skor 0 berarti tidak ada overlap pada representasi ini; skor 1 berarti vektor searah.
Skor bukan persentase kebenaran. Query kosong, semua stopword, dan istilah asing di
luar vocabulary menghasilkan pesan tanpa hasil. Tidak ada stemming, pencocokan
sinonim, atau koreksi typo. Angka dipertahankan. Daftar stopword bisa disesuaikan.

Tidak menggunakan NLTK, Sastrawi, atau library tambahan di luar ketentuan.
NumPy/SciPy dipasang otomatis sebagai dependensi internal scikit-learn.

## 5. Pengujian dan batas interpretasi

Jalankan `python evaluate.py` untuk mereproduksi pengujian pada seluruh dataset.
Hasil tersimpan dalam JSON; waktu bergantung mesin. Query uji mencakup pendidikan,
bencana, teknologi, politik, hiburan, query kosong, stopword, dan istilah tidak dikenal.
Tanpa label relevansi manusia, hasil ini memverifikasi fungsi dan skor, belum dapat
menyatakan precision/recall, akurasi, atau bahwa ranking semantik pasti tepat.

## 6. Rencana pembagian kerja (sesuaikan kontribusi nyata)

- Anggota 1: loader dataset, preprocessing, validasi data.
- Anggota 2: CountVectorizer, schema dan index Whoosh.
- Anggota 3: CLI, cosine ranking, pengujian dan dokumentasi.

Semua anggota perlu memahami alur dan melakukan commit sesuai pekerjaan nyata.

## 7. GitHub dan pengumpulan

Repository **belum dibuat/diunggah** oleh paket ini. Buat repo kosong di akun kalian,
misalnya `01_UTS_Praktikum_PI` (ganti 01 dengan nomor kelompok). Dari folder proyek:

```bash
git init
git add .
git commit -m "Implementasi sistem IR multi-dataset"
git branch -M main
git remote add origin https://github.com/USERNAME/01_UTS_Praktikum_PI.git
git push -u origin main
```

Ganti USERNAME dan nomor kelompok. Pastikan izin publikasi dataset dari pengajar;
repo private dapat diberi akses ke aslab jika diperlukan. Jika sudah ada remote,
gunakan `git remote -v` untuk memeriksa, jangan menambah origin dua kali.
Isi identitas di laporan Markdown lalu ekspor kembali ke PDF menggunakan editor
Markdown yang mendukung ekspor PDF. Perbarui URL GitHub di bawah. Ubah nama ZIP
menjadi `01_UTS_Praktikum_PI.zip` sesuai nomor tim (ikuti format LMS jika berbeda).

Nomor kelompok: [ISI]

Anggota 1: [NAMA - NPM]

Anggota 2: [NAMA - NPM]

Anggota 3: [NAMA - NPM, jika ada]

URL GitHub: [ISI SETELAH PUSH]
