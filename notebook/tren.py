from pickle import load
import pandas as pd

print('[INFO] preparing data')
df = pd.read_parquet('../dist/hp.parquet')

with open('../dist/dictionary.pickle', 'rb') as f:
    dictionary = load(f)
with open('../dist/corpus.pickle', 'rb') as f:
    corpus = load(f)
with open('../dist/model.pickle', 'rb') as f:
    model = load(f)

print('[INFO] building corpus')
df['corpus'] = corpus

print('[INFO] building topics')
df['topics'] = model.get_document_topics(df['corpus'])

print('[INFO] saving df')
df.to_parquet('../dist/hpct.parquet')