import json
import os
import time
import datetime

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def load_data(path):
    """ Load data, however it might be stored (change this accordingly). """
    # TODO: load from DB? (or connect with crawler)
    with open(path, encoding="utf8") as f:
        return json.load(f)


def ngrams(s, n=3):
    """ Returns a list of ngrams. E.g. `ngrams('najbolj'. n=3)` returns `['naj', 'ajb', 'jbo', 'bol', 'olj']`."""
    return [s[i: i + n] for i in range(len(s) - n + 1)]


def extract_scores(data):
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

def store_scores(articles):
    # create db connection and create table if it doesnt exist yet
    import sqlite3
    conn = sqlite3.connect('../data/news.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS `news_article` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `title` VARCHAR(255) NOT NULL, `content` VARCHAR(255), `topic` VARCHAR(255) NOT NULL, `datetime` DATETIME NOT NULL, `link` VARCHAR(255) NOT NULL UNIQUE, `score` FLOAT)''')

    # insert articles into table
    for article in articles:
        conn.execute("INSERT INTO news_article (title, content, topic, datetime, link, score) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(link) DO UPDATE SET score=?",
                     (article['title'], article['content'], article['topic'], article['date'], article['link'], article['score'], article['score']))
    conn.commit()


if __name__ == "__main__":
    # How far back are we looking for exclusiveness of articles?
    OBSERVED_PERIOD_S = 3 * 24 * 60 * 60

    # Unprocessed (raw) data
    data_path = os.environ.get("NEWS_DATA_PATH", "../data/news.json")
    articles = load_data(data_path)
    articles = extract_scores(articles)

    store_scores(articles)

