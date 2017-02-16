"""
Functions related to tolerant retrieval - wildcards, near matches, etc.
"""

import bisect
import collections
import functools
import re

from inverted_index import union_sorted, intersect_sorted


def kgrams(term, k):
    """
    Yield all the k-grams in a given term.
    """
    term = '$' + term + '$'
    for i in range(0, len(term) - k + 1):
        yield term[i:i+k]


def build_kgram_index(term_index, k):
    """
    Given an inverted index with terms as keys, return an index with k-grams as keys and terms as values.
    :param term_index: an inverted index
    :param k: the number of characters to include in each kgram
    :return: a map from k-grams to terms
    """
    result = collections.defaultdict(list)

    for (term, value) in term_index.items():
        for kgram in kgrams(term, k):
            bisect.insort_left(result[kgram], term)

    return result


def wildcard_match(query, term):
    """
    Does a term match a wildcard query?
    """
    regex = '^' + query.replace('*', '.*') + '$'
    return re.match(regex, term) is not None


def query_wildcard(index, kgram_index, k, query):
    """
    Use a k-gram index to retrieve documents matching a wildcard query.

    :param index: an inverted index (terms to documents)
    :param kgram_index: an index from k-grams to terms
    :param k: the length of the k-grams in kgram_index
    :param query: a query, potentially containing wildcards
    :return: an iterator over document ids that match the query
    """
    kgs = (kg for kg in kgrams(query, k) if '*' not in kg)
    terms = functools.reduce(intersect_sorted, (kgram_index[kg] for kg in kgs))
    terms = (term for term in terms if wildcard_match(query, term))

    term_iter = iter(terms)
    term = next(term_iter, None)

    result = []

    term = next(term_iter, None)

    while term is not None:
        result = union_sorted(result, index[term])
        term = next(term_iter, None)

    return result

