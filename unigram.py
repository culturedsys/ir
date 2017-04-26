"""
Search using unigram language models
"""

import collections
import operator


class FrequencyTable(collections.defaultdict):
    """
    A table mapping tokens to frequency counts.
    Also maintains the property `length`, the total length of the underlying document
    """

    def __init__(self, document):
        collections.defaultdict.__init__(self, int)
        length = 0

        for token in document:
            self[token] += 1
            length += 1

        self.length = length


def create_model(frequencies):
    """
    Create a unigram model from a document.

    :param frequencies: A FrequencyTable representing to document
    :return: A map from terms to maximum-likelihood estimations of that term on the basis of the document
    """

    model = collections.defaultdict(float)

    for (token, frequency) in frequencies.items():
        model[token] = frequencies[token] / float(frequencies.length)

    return model


def create_collection_model(tables):
    """
    Create collection model based on the frequency tables for all documents.

    :param tables: An iterable of FrequencyTables representing the documents in the collection
    :return:
    """
    frequencies = collections.defaultdict(int)
    length = 0.0

    for table in tables:
        length += table.length
        for (token, frequency) in table.items():
            frequencies[token] += frequency

    model = collections.defaultdict(float)
    for (token, frequency) in frequencies.items():
        model[token] = frequencies[token] / length

    return model


def create_models(documents):
    """
    Converts an iterable over documents to a collection model and a list of document models

    :param documents: An iterable over iterables of tokens
    :return: A pair consisting of a collection model and a list of document models
    """

    tables = [FrequencyTable(document) for document in documents]

    document_models = [create_model(table) for table in tables]

    collection_model = create_collection_model(tables)

    return collection_model, document_models


def rank_models(query, collection_model, models, mixing=0.5):
    """
    Rank models according to the probability that they will generate the query.

    :param query: An iterable of tokens
    :param collection_model: A model representing the entire collection
    :param models: A list of document models
    :param mixing: A float representing how much weight to give the document model vs. the collection model (usually
    called 'lambda'
    :return: the indexes of the models, in the order from most to least likely to generate the query
    """

    tokens = list(query)

    probabilities = []

    for model in models:
        probability = 1
        for token in tokens:
            probability *= mixing * model[token] + (1 - mixing) * collection_model[token]
        probabilities.append(probability)

    return [i[0] for i in sorted(enumerate(probabilities), key=operator.itemgetter(1), reverse=True)]



