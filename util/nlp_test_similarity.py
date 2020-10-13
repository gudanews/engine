from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from itertools import product
import numpy


# Corpus with example sentences
# from sentence_transformers import SentenceTransformer
# import scipy.spatial


def similarity(a, b):
    embedder = SentenceTransformer('bert-base-nli-mean-tokens')

    corpus = [a]
    corpus_embeddings = embedder.encode(corpus)

    # Query sentences:
    queries = [b]
    query_embeddings = embedder.encode(queries)

    # Find the closest 5 sentences of the corpus for each query sentence based on cosine similarity
    closest_n = 5
    for query, query_embedding in zip(queries, query_embeddings):
        distances = scipy.spatial.distance.cdist([query_embedding], corpus_embeddings, "cosine")[0]

        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1])
        for idx, distance in results[0:closest_n]:
            return (1 - distance)


def find_similarity(a, b):
    str1 = a
    str2 = b

    stop_words = set(stopwords.words("english"))

    filtered_sentence1 = []
    filtered_sentence2 = []
    lemm_sentence1 = []
    lemm_sentence2 = []
    sims = []
    temp1 = []
    temp2 = []
    simi = []
    final = []
    same_sent1 = []
    same_sent2 = []

    lemmatizer = WordNetLemmatizer()

    for words1 in word_tokenize(str1):
        if words1 not in stop_words:
            if words1.isalnum():
                filtered_sentence1.append(words1)

    for i in filtered_sentence1:
        lemm_sentence1.append(lemmatizer.lemmatize(i))

    for words2 in word_tokenize(str2):
        if words2 not in stop_words:
            if words2.isalnum():
                filtered_sentence2.append(words2)

    for i in filtered_sentence2:
        lemm_sentence2.append(lemmatizer.lemmatize(i))

    for word1 in lemm_sentence1:
        simi = []
        for word2 in lemm_sentence2:
            sims = []
            # print(word1)
            # print(word2)
            syns1 = wordnet.synsets(word1)
            # print(syns1)
            # print(wordFromList1[0])
            syns2 = wordnet.synsets(word2)
            # print(wordFromList2[0])
            for sense1, sense2 in product(syns1, syns2):
                d = wordnet.wup_similarity(sense1, sense2)
                if d != None:
                    sims.append(d)

            # print(sims)
            # print(max(sims))
            if sims != []:
                max_sim = max(sims)
                # print(max_sim)
                simi.append(max_sim)

        if simi != []:
            max_final = max(simi)
            final.append(max_final)

    similarity_index = numpy.mean(final)
    similarity_index = round(similarity_index, 4)
    return similarity_index
import time
from gensim.matutils import softcossim
from gensim import corpora
import gensim.downloader as api
from gensim.models import KeyedVectors
import numpy as np
from gensim.test.utils import common_texts, get_tmpfile
from gensim.models import Word2Vec

start = time.time()
model = Word2Vec.load("word2vec.model")
word_vectors = model.wv
def avg_feature_vector(sentence, model, num_features, index2word_set):
    words = sentence.split()
    feature_vec = np.zeros((num_features, ), dtype='float32')
    n_words = 0
    for word in words:
        if word in index2word_set:
            n_words += 1
            feature_vec = np.add(feature_vec, model[word])
    if (n_words > 0):
        feature_vec = np.divide(feature_vec, n_words)
    return feature_vec

def gensim_similarity(a,b):
    similarity = model.similarity(a,b)
    return similarity
print(gensim_similarity('world','hello'))