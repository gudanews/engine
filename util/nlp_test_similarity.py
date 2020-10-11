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

from gensim import corpora, models, similarities
import jieba
texts = ['I love reading Japanese novels. My favorite Japanese writer is Tanizaki Junichiro.', 'Natsume Soseki is a well-known Japanese novelist and his Kokoro is a masterpiece.', 'American modern poetry is good. ']
keyword = 'Japan has some great novelists. Who is your favorite Japanese writer?'
texts = [jieba.lcut(text) for text in texts]
dictionary = corpora.Dictionary(texts)
feature_cnt = len(dictionary.token2id)
corpus = [dictionary.doc2bow(text) for text in texts]
tfidf = models.TfidfModel(corpus)
kw_vector = dictionary.doc2bow(jieba.lcut(keyword))
index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features = feature_cnt)
sim = index[tfidf[kw_vector]]
for i in range(len(sim)):
    print('keyword is similar to text%d: %.2f' % (i + 1, sim[i]))
