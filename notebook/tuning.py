import os
import pickle

import pandas as pd
from gensim.corpora.dictionary import Dictionary
from gensim.models.coherencemodel import CoherenceModel
from gensim.models.ldamulticore import LdaMulticore
from hyperopt import fmin, hp, tpe

df = pd.read_parquet('../dist/hp.parquet')

dataset = df['preprocessed']
dictionary = Dictionary(dataset)
dictionary.filter_extremes()
corpus = [dictionary.doc2bow(text) for text in dataset]

with open('../dist/dictionary.pickle', 'wb') as f:
    pickle.dump(dictionary, f)
with open('../dist/corpus.pickle', 'wb') as f:
    pickle.dump(corpus, f)


def get_lda(args):
    return LdaMulticore(
        corpus=corpus,
        id2word=dictionary,
        num_topics=args['k'],
        alpha=args['a'],
        eta=args['e'],
        per_word_topics=True,
        workers=3,
        random_state=99)


def get_coherence(args):
    model = get_lda(args)
    cm = CoherenceModel(model, texts=dataset)
    c = cm.get_coherence()
    args['ci'] = 1 - c
    print(args)
    return c


def tuning(args):
    c = get_coherence(args)

    current_result = pd.DataFrame(
        [[args['k'], args['a'], args['e'], c]],
        columns=['k', 'a', 'e', 'c'])
    output_path = '../dist/tuning.csv'
    current_result.to_csv(
        output_path,
        mode='a',
        header=not os.path.exists(output_path),
        index=False)

    return 1 - c


space = {
    'k': hp.uniformint('k', 2, 20),
    'a': hp.uniform('a', 0, 0.7),
    'e': hp.uniform('e', 0.3, 1),
}

best_args = fmin(
    tuning,
    space,
    algo=tpe.suggest,
    max_evals=100
)

print(best_args)
