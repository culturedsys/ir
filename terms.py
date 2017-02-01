"""
Functions related to producing term lists - tokenization, stemming, etc.
"""


import re


def split_whitespace(document):
    """
    Trivial tokenizer which just splits on whitespace.
    :param document: a string representing a document
    :return: an iterable of tokens
    """
    return document.split()


# Common English stop words, from Christopher D. Manning, Prabhakar Raghavan, and Hinrich Schutze (2008), Introduction
# to Information Retrieval, p. 26
ENGLISH_STOP_WORDS = ['a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it',
                      'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'with']


def drop_stop_words(terms, stop_words=ENGLISH_STOP_WORDS):
    """
    Remove stop words from an iterable of terms
    :param terms: and iterable of terms
    :param stop_words: a list of stop words; the default is a list of common Enhlish stop words
    :return: an iterable of terms with stop words removed
    """
    return (term for term in terms if term not in stop_words)


def strip_punctuation(term):
    """
    Removes punctuation from a string, leaving only letters and numbers
    """
    return re.sub('\\W', '', term)


def normalize(terms, replacements={}, default=lambda s: strip_punctuation(s.lower())):
    """
    Normalize by first checking against a dictionary, and, if no term is found, applying a function. This can be used
    to, for example, keep known proper names in upper case, while lowercasing everything else.
    :param terms: an iterable of terms
    :param replacements: a dictionary of specific term-to-term replacements; empty by default
    :param default: a function to apply to terms that do not have a specific replacement. By default lowercases and strips punctuation
    :return: an iterable of normalized terms.
    """
    for term in terms:
        if replacements.get(term, False):
            yield replacements[term]
        else:
            yield default(term)
