import datetime
import time

import numpy as np
from utils import DATE_FORMAT, OBSERVED_PERIOD_S, UNK_TOKEN


def extract_scores_word2vec(data, embeddings):
    # Earliest to latest
    data_chronologically = sorted(data, key=lambda curr_article: time.mktime(datetime.datetime.strptime(curr_article['date'], DATE_FORMAT).timetuple()))
    article_scores = []

    for i, curr_instance in enumerate(data_chronologically):
        # First instance of current topic - nothing to compare it's exclusiveness with
        if i == 0:
            article_scores.append(1.0)
            continue

        curr_title = curr_instance["title"]
        curr_time = time.mktime(datetime.datetime.strptime(curr_instance['date'], DATE_FORMAT).timetuple())

        curr_repr = embed(curr_title, embeddings=embeddings)

        # Gather up representation for already observed articles
        previous_reprs = []
        for idx_prev in range(i):
            other_instance = data_chronologically[idx_prev]
            other_title = other_instance["title"]
            other_time = time.mktime(datetime.datetime.strptime(other_instance['date'], DATE_FORMAT).timetuple())

            if other_time < curr_time - OBSERVED_PERIOD_S:
                continue
            previous_reprs.append(embed(other_title, embeddings=embeddings))

        previous_reprs = np.mean(previous_reprs, axis=0)
        # Exclusiveness = dissimilarity to previous news for the same topic
        similarity = cosine(previous_reprs, curr_repr)
        exclusiveness = 1 - similarity

        article_scores.append(exclusiveness)

    assert len(article_scores) == len(data)
    for curr_article, curr_score in zip(data_chronologically, article_scores):
        curr_article["score"] = curr_score
        print(f"[{curr_article['score']:.3f}] {curr_article['title']}")

    return data


def load_word2vec(path):
    tok2emb = {}
    with open(path) as f:
        nrows, emb_dim = list(map(lambda s: int(s), f.readline().strip().split(" ")))
        i, lines = 0, []
        # This is intentionally ugly: the embeddings are encoded in some broken way -> skip those embeddings
        while True:
            try:
                curr_line = f.readline().strip()
                if len(curr_line) == 0 or i == nrows:
                    break
                lines.append(curr_line)
                i += 1
            except UnicodeDecodeError:
                continue

    for line in lines:
        parts = line.strip().split(" ")
        word, embedding = parts[0], parts[1:]
        try:
            assert len(embedding) == emb_dim
        except AssertionError:
            continue
        tok2emb[word] = np.array(list(map(lambda n: float(n), embedding)))

    if UNK_TOKEN not in tok2emb:
        tok2emb[UNK_TOKEN] = np.random.random(emb_dim)
        tok2emb[UNK_TOKEN] /= np.sqrt(np.sum(np.square(tok2emb[UNK_TOKEN])))

    return tok2emb


def cosine(x, y):
    """Cosine similarity between x and y"""
    return np.dot(x, y) / (np.sqrt(np.sum(np.square(x))) * np.sqrt(np.sum(np.square(y))))


def embed(sequence, embeddings):
    """ Embed the sequence by averaging non-contextual token embeddings"""
    unks = 0
    embedded_seq = []
    for token in sequence.strip().lower().split():
        curr_emb = embeddings.get(token, None)
        if curr_emb is None:
            curr_emb = embeddings[UNK_TOKEN]
            unks += 1

        embedded_seq.append(curr_emb)

    return np.mean(embedded_seq, axis=0)


def ngrams(s, n=3):
    """ Returns a list of ngrams. E.g. `ngrams('najbolj'. n=3)` returns `['naj', 'ajb', 'jbo', 'bol', 'olj']`."""
    return [s[i: i + n] for i in range(len(s) - n + 1)]


def extract_scores_ngrams(data):
    # Earliest to latest
    data_chronologically = sorted(data, key=lambda curr_article: time.mktime(datetime.datetime.strptime(curr_article['date'], DATE_FORMAT).timetuple()))
    article_scores = []

    for i, curr_instance in enumerate(data_chronologically):
        # First instance of current topic - nothing to compare it's exclusiveness with
        if i == 0:
            article_scores.append(1.0)
            continue

        curr_title = curr_instance["title"]
        curr_time = time.mktime(datetime.datetime.strptime(curr_instance['date'], DATE_FORMAT).timetuple())
        curr_ngrams = ngrams(curr_title.lower(), n=3)
        curr_uniq_ngrams = set(curr_ngrams)

        # Gather up already observed n-grams before the current article and check how many are also in new article
        all_previous_uniq_ngrams = set()
        for idx_prev in range(i):
            other_instance = data_chronologically[idx_prev]
            other_title = other_instance["title"]
            other_time = time.mktime(datetime.datetime.strptime(other_instance['date'], DATE_FORMAT).timetuple())

            if other_time < curr_time - OBSERVED_PERIOD_S:
                continue
            other_uniq_ngrams = set(ngrams(other_title.lower(), n=3))
            all_previous_uniq_ngrams.update(other_uniq_ngrams)

        # Exclusiveness = dissimilarity to previous news for the same topic
        similarity = len(all_previous_uniq_ngrams & curr_uniq_ngrams) / len(all_previous_uniq_ngrams | curr_uniq_ngrams)
        exclusiveness = 1 - similarity
        article_scores.append(exclusiveness)

    assert len(article_scores) == len(data)
    for curr_article, curr_score in zip(data_chronologically, article_scores):
        curr_article["score"] = curr_score
        print(f"[{curr_article['score']:.3f}] {curr_article['title']}")

    return data


if __name__ == "__main__":
    vecs = load_word2vec("/home/matej/Documents/data/w2v100_sl/model.txt")
    print("FIN")
