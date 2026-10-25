"""Preprocessing yang sama untuk dokumen dan query, tanpa unduhan eksternal."""
import html
import re
import unicodedata

# Daftar eksplisit dan dapat diperluas; negasi 'tidak' sengaja dipertahankan.
STOPWORDS = frozenset('''yang dan di ke dari untuk pada dengan adalah ini itu dalam
atau sebagai oleh akan telah sudah juga karena agar sehingga saat ketika antara
para sebuah suatu tersebut terhadap tentang kepada saya kamu kami kita mereka ia
dia nya pun lah kah bahwa yaitu yakni serta bisa dapat lebih paling sangat ada
itu ini the a an and or of to in on for with is are was were be been this that
as by from at it its'''.split())

def tokenize(text):
    text = unicodedata.normalize('NFKC', html.unescape(str(text))).lower()
    text = re.sub(r'<[^>]+>', ' ', text)
    return [t for t in re.findall(r'[^\W_]+', text, flags=re.UNICODE)
            if t not in STOPWORDS]

def preprocess(text):
    return ' '.join(tokenize(text))
