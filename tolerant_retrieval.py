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


def edit_distance_table(source, dest, insert_cost=None, delete_cost=None, substitute_cost=None):
    """
    Produce a table containing edit distances between source and dest.

    :param source: a string.
    :param dest: another string.
    :param insert_cost: a function taking one character and returning the cost to insert that character. Defaults to a
                        constant 1.
    :param delete_cost: a function taking one character and returning the cost to delete that character. Defaults to a
                        constant 1.
    :param substitute_cost: a function taking two characters and returning the cost to substitute the first for the
                        second. Defaults to a constant 1.
    :return: a two-dimensional array with dimensions len(source)+1 * len(dest) + 1, giving the minimum edit distance
    """
    if insert_cost is None:
        insert_cost = lambda _: 1

    if delete_cost is None:
        delete_cost = lambda _: 1

    if substitute_cost is None:
        substitute_cost = lambda a, b: 1

    table = [[None for _ in range(0, len(source) + 1)] for _ in range(0, len(dest) + 1)]

    table[0][0] = 0

    for i in range(1, len(source) + 1):
        table[0][i] = table[0][i-1] + insert_cost(source[i-1])

    for j in range(1, len(dest) + 1):
        table[j][0] = table[j-1][0] + delete_cost(dest[j - 1])

    for j in range(1, len(dest) + 1):
        for i in range(1, len(source) + 1):
            source_char = source[i - 1]
            dest_char = dest[j - 1]

            insert = table[j - 1][i] + insert_cost(dest_char)
            delete = table[j][i - 1] + delete_cost(source_char)

            substitute = table[j - 1][i - 1]
            if source_char == dest_char:
                substitute += 0
            else:
                substitute += substitute_cost(source_char, dest_char)

            table[j][i] = min(insert, delete, substitute)

    return table


def edit_distance(source, dest, insert_cost=None, delete_cost=None, substitute_cost=None):
    table = edit_distance_table(source, dest, insert_cost, delete_cost, substitute_cost)
    return table[len(dest)][len(source)]


def alignment(source, dest, insert_cost=None, delete_cost=None, substitute_cost=None):
    """
    Calculate the alignment using an edit distance table. Changes are reported as pairs, where (a, b) represents a
    substitution changing a to b, (a, None) represents the deletion of a, and (None, b) represents the insertion of b.

    :return: A list of pairs representing the changes made.
    """
    table = edit_distance_table(source, dest, insert_cost, delete_cost, substitute_cost)
    result = []
    j = len(dest)
    i = len(source)

    while j > 0 or i > 0:
        if i == 0:  # Must be delete
            result.insert(0, (None, dest[j - 1]))
            j -= 1
            continue
        elif j == 0:  # Must be insert
            result.insert(0, (source[i - 1], None))
            i -= 1
            continue

        del_cost = table[j][i - 1]
        ins_cost = table[j - 1][i]
        sub_cost = table[j - 1][i - 1]
        min_cost = min(del_cost, ins_cost, sub_cost)

        if min_cost == sub_cost:
            step = (source[i-1], dest[j-1])
            i -= 1
            j -= 1
        elif min_cost == del_cost:
            step = (source[i-1], None)
            i -= 1
        else:
            step = (None, dest[j-1])
            j -= 1

        result.insert(0, step)

    return result
