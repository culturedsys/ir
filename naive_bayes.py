"""
A naive Bayes classifier with Laplace smoothing
"""

import itertools
import operator
import frequencies
import collections
import math


class Classifier(object):
    """
    A classifier, for calculating the probability that a document is in a given class
    """

    def __init__(self, label, prior, vocabulary, table):
        """
        Create a classifer based on the supplied frequency tables

        :param label: an identifier for the class this classifier is dealing with
        :param prior: the prior probability that a document is in this class
        :param vocabulary: the vocabulary in the whole training collection
        :param table: a frequency table for documents in this class in the training collection
        """

        self.label = label
        self.prior = math.log(prior)

        self.probabilities = collections.defaultdict(float)

        for term in vocabulary:
            self.probabilities[term] = math.log(table[term] + 1) - math.log(table.length + len(vocabulary))

    def score(self, document):
        """
        Return a score representing how probable the document is to be in the class. This is an un-normalized
        probability, but is comparable with other scores generated for the same document.

        :param document: an iterable of tokens
        """

        score = self.prior
        for token in document:
            score += self.probabilities[token]

        return score


def create_classifiers(labelled_documents):
    """
    Create a sequence of classifiers trained on the labelled documents.

    :param labelled_documents: A sequence of (label, document) pairs, where each document is a sequence of tokens
    """

    grouped = itertools.groupby(sorted(labelled_documents, key=operator.itemgetter(0)), key=operator.itemgetter(0))

    tables = collections.defaultdict(frequencies.FrequencyTable)
    vocabulary = frequencies.FrequencyTable()
    document_count = 0
    label_counts = collections.defaultdict(int)

    for label, documents in grouped:
        for document in documents:
            document_count += 1
            label_counts[label] += 1
            tables[label] += frequencies.FrequencyTable(document[1])
            vocabulary += tables[label]

    classifiers = []

    for label, table in tables.items():
        classifiers.append(Classifier(label, label_counts[label] / document_count, vocabulary.keys(), table))

    return classifiers


def classify(document, classifiers):
    """
    Classify a document into one class based on the supplied classifiers

    :param document: an iterable of tokens
    :param classifiers: an iterable of Classifier objects
    :return: the label of the class predicted for the document
    """

    return sorted(classifiers, key=lambda c: c.score(document), reverse=True)[0].label
