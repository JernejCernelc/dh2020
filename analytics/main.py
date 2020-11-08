import json
import os
from process_articles import extract_scores_ngrams, extract_scores_word2vec, load_word2vec


def load_data(path):
    """ Load data, however it might be stored (change this accordingly). """
    with open(path, encoding="utf8") as f:
        return json.load(f)


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
    # Unprocessed (raw) crawled data
    data_path = os.environ.get("NEWS_DATA_PATH", "../data/news.json")
    w2v_embs = load_word2vec(os.environ.get("EMBEDDINGS_PATH", "/home/matej/Documents/data/w2v100_sl/model.txt"))

    articles = load_data(data_path)
    groups = {}
    for art in articles:
        curr_articles = groups.get(art["topic"], [])
        curr_articles.append(art)
        groups[art["topic"]] = curr_articles

    for curr_topic, arts in groups.items():
        print(f"TOPIC {curr_topic}")
        # articles = extract_scores_ngrams(arts)
        articles = extract_scores_word2vec(arts, w2v_embs)
        store_scores(articles)

