



# Corpus with example sentences
def similarity(a,b):
    from sentence_transformers import SentenceTransformer
    import scipy.spatial

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
            return(1-distance)

def similar(a, b):
    X = a.lower()
    Y = b.lower()

    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

    X_list = word_tokenize(X)
    Y_list = word_tokenize(Y)

    sw = stopwords.words('english')
    l1 = []
    l2 = []

    X_set = {w for w in X_list if not w in sw}
    Y_set = {w for w in Y_list if not w in sw}

    rvector = X_set.union(Y_set)
    for w in rvector:
        if w in X_set:
            l1.append(1)
        else:
            l1.append(0)
        if w in Y_set:
            l2.append(1)
        else:
            l2.append(0)
    c = 0

    for i in range(len(rvector)):
        c += l1[i] * l2[i]
    cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
    return cosine

if __name__ == '__main__':
    from util.nlp_test_similarity import find_similarity
    from database.news import NewsDB

    if __name__ == '__main__':
        column = ["title"]
        existing = NewsDB().get_latest_news(column=column, record_as_dict=True)
        #file = open('data.txt', encoding="utf8")
        # existing = file.read().splitlines()
        for i in existing:
            for j in existing:
                item_1 = i['title']
                item_2 = j['title']
                number =float(similarity(item_1, item_2))
                if (number>= 0.75 or similar(item_1, item_2) >= 0.7 or find_similarity(item_1,item_2)>=0.75) and item_1 != item_2 :
                    print(item_1)
                    print(item_2)
                    print('\n')
                    print('cosine : ' + str(similar(item_1, item_2)))
                    print('\n')
                    print('tensorflow : ' + str(number))
                    print('\n')
                    print('nltk : '+str(find_similarity(item_1,item_2)))