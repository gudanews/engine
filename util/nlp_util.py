from datetime import datetime
import unittest
from util.config_util import Configure


# Program to measure the similarity between
# two sentences using cosine similarity.
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def check_similarity_nltk(phrase1, phrase2):
    # tokenization
    X_list = word_tokenize(phrase1)
    Y_list = word_tokenize(phrase2)

    # sw contains the list of stopwords
    sw = stopwords.words('english')
    l1 = []
    l2 = []

    # remove stop words from the string
    X_set = {w for w in X_list if not w in sw}
    Y_set = {w for w in Y_list if not w in sw}

    # form a set containing keywords of both strings
    rvector = X_set.union(Y_set)
    for w in rvector:
        if w in X_set:
            l1.append(1)  # create a vector
        else:
            l1.append(0)
        if w in Y_set:
            l2.append(1)
        else:
            l2.append(0)
    c = 0

    # cosine formula
    for i in range(len(rvector)):
        c += l1[i] * l2[i]
    cosine = c / float((sum(l1) * sum(l2)) ** 0.5)

    return cosine



from nltk.corpus import wordnet as wn

def words_similarity(word1, word2):
    ss1 = wn.synsets(word1, 'n')[0]  # Get the most common synset
    ss2 = wn.synsets(word2, 'n')[0]  # Get the most common synset
    return ss1.wup_similarity(ss2)

from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn


def penn_to_wn(tag):
    """ Convert between a Penn Treebank tag to a simplified Wordnet tag """
    if tag.startswith('N'):
        return 'n'

    if tag.startswith('V'):
        return 'v'

    if tag.startswith('J'):
        return 'a'

    if tag.startswith('R'):
        return 'r'

    return None


def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None

    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None


def sentence_similarity(sentence1, sentence2):
    """ compute the sentence similarity using Wordnet """
    # Tokenize and tag
    sentence1 = pos_tag(word_tokenize(sentence1))
    sentence2 = pos_tag(word_tokenize(sentence2))

    # Get the synsets for the tagged words
    synsets1 = [tagged_to_synset(*tagged_word) for tagged_word in sentence1]
    synsets2 = [tagged_to_synset(*tagged_word) for tagged_word in sentence2]

    # Filter out the Nones
    synsets1 = [ss for ss in synsets1 if ss]
    synsets2 = [ss for ss in synsets2 if ss]

    score, count = 0.0, 0

    # For each word in the first sentence
    for synset in synsets1:
        # Get the similarity value of the most similar word in the other sentence
        best_score = max([synset.path_similarity(ss) or 0 for ss in synsets2])

        # Check that the similarity could have been computed
        if best_score is not None:
            score += best_score
            count += 1

    # Average the values
    score /= count
    return score








import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from unidecode import unidecode
import string


def pre_process(corpus):
    # convert input corpus to lower case.
    corpus = corpus.lower()
    # collecting a list of stop words from nltk and punctuation form
    # string class and create single array.
    stopset = stopwords.words('english') + list(string.punctuation)
    # remove stop words and punctuations from string.
    # word_tokenize is used to tokenize the input corpus in word tokens.
    corpus = " ".join([i for i in word_tokenize(corpus) if i not in stopset])
    # remove non-ascii characters
    corpus = unidecode(corpus)
    return corpus

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
lemmatizer = WordNetLemmatizer()

def lemmatization(corpus):
    words = word_tokenize(corpus)
    return " ".join([lemmatizer.lemmatize(w) for w in words])

from sklearn.feature_extraction.text import TfidfVectorizer

def get_tfidf_feature_vectors(sentence1, sentence2):
    corpus = list()
    corpus.append(pre_process(sentence1))
    corpus.append(pre_process(sentence2))
    # creating vocabulary using uni-gram and bi-gram
    tfidf_vectorizer = TfidfVectorizer(ngram_range=(1,2))
    tfidf_vectorizer.fit(corpus)
    feature_vectors = tfidf_vectorizer.transform(corpus)
    return feature_vectors



# print(datetime.now())
# from gensim.models import Word2Vec
# from gensim.models import KeyedVectors
# import numpy as np
#
# # give a path of model to load function
# #word_emb_model = KeyedVectors.load_word2vec_format('pruned.word2vec.txt', binary=False)
# word_emb_model = KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
# #word_emb_model = KeyedVectors.load_word2vec_format('freebase-vectors-skipgram1000-en.bin', binary=True)
# #word_emb_model = Word2Vec.load('word2vec.bin')
#
# print(datetime.now())
#
# from collections import Counter
# import itertools
#
#
# def map_word_frequency(document):
#     return Counter(itertools.chain(*document))
#
#
# def get_sif_feature_vectors(sentence1, sentence2, word_emb_model=word_emb_model):
# #def get_sif_feature_vectors(sentence1, sentence2, word_emb_model=None):
#     # sentence1 = [token for token in sentence1.split() if token in word_emb_model.wv.vocab]
#     # sentence2 = [token for token in sentence2.split() if token in word_emb_model.wv.vocab]
#     sentence1 = [token for token in sentence1.split() if token in word_emb_model.vocab]
#     sentence2 = [token for token in sentence2.split() if token in word_emb_model.vocab]
#     word_counts = map_word_frequency((sentence1 + sentence2))
#     embedding_size = 300  # size of vectore in word embeddings
#     a = 0.001
#     sentence_set = []
#     for sentence in [sentence1, sentence2]:
#         vs = np.zeros(embedding_size)
#         sentence_length = len(sentence)
#         for word in sentence:
#             a_value = a / (a + word_counts[word])  # smooth inverse frequency, SIF
#             # vs = np.add(vs, np.multiply(a_value, word_emb_model.wv[word]))  # vs += sif * word_vector
#             vs = np.add(vs, np.multiply(a_value, word_emb_model[word]))  # vs += sif * word_vector
#         vs = np.divide(vs, sentence_length)  # weighted average
#         sentence_set.append(vs)
#     return sentence_set





from sklearn.metrics.pairwise import cosine_similarity
def get_cosine_similarity(feature_vec_1, feature_vec_2):
    return cosine_similarity(feature_vec_1.reshape(1, -1), feature_vec_2.reshape(1, -1))[0][0]




def check_similarity_nlp(sen1, sen2):
    sen1 = lemmatization(pre_process(sen1))
    sen2 = lemmatization(pre_process(sen2))
    #abc = get_sif_feature_vectors(sen1, sen2)
    abc = get_tfidf_feature_vectors(sen1, sen2)
    return get_cosine_similarity(abc[0], abc[1])






from util.common import LoggedTestCase
from colorama import Fore, Back, Style, init

class TestConfigParser(LoggedTestCase):

    def setUp(self):
        self.cfg = Configure()

    def test_compare_similarity(self):
        init()
        certainly = 0
        likely = 0
        with open("./new_headings.txt", 'r') as f_new:
            for new in f_new:
                new = new.rstrip()
                with open("./existing_headings.txt", 'r') as f_existing:
                    for existing in f_existing:
                        existing = existing.rstrip()
                        sentence1= lemmatization(pre_process(new))
                        sentence2= lemmatization(pre_process(existing))
                        sim1 = check_similarity_nltk(sentence1, sentence2)
                        sim2 = sentence_similarity(sentence1, sentence2)
                        # if any(x > 0.6 for x in (sim1, sim2)):
                        #if 0.99 > sim2 > 0.7 and (sim1 + sim2 > 1.3):
                        if 1.99 > sim1 + sim2 > 1.0:
                            print("\n" + "*" * 60 + "\n")
                            color = ""
                            if abs(sim1 - sim2) > 0.5:
                                color = Back.RED + Fore.WHITE
                            elif abs(sim1 - sim2) > 0.2:
                                color = Back.BLACK
                                if sim1 > sim2:
                                    color += Fore.YELLOW
                                else:
                                    color += Fore.WHITE
                            print(color + "New: %s" % new)
                            print("Old: %s" % existing)
                            print("(%.3f\t:\t%.3f)" % (sim1, sim2))
                            print(Style.RESET_ALL)
                            certainly += 1
                            likely += 1

        print("CERTAINLY found [%s]" % certainly)
        print("LIKELY found [%s]" % likely)

if __name__ == '__main__':
    unittest.main()
