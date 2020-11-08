# Setup
Make sure to download the word vectors (see below) if you want to use scoring 
using embeddings. Otherwise, there's also a reference n-gram similarity implemented. 

## Environment
You can either set these env vars, or just change them in `main.py`.  

`NEWS_DATA_PATH`: path to json, containing crawled news.  
 
`EMBEDDINGS_PATH`: path to model.txt, containing 100D Slovene word2vec embeddings 
(inside http://vectors.nlpl.eu/repository/20/67.zip)

## Running
Run `main.py`, which is intended to score crawled articles and write aggregated scores to DB.