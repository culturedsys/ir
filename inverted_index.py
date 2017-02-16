"""
Functions relating to constructing and querying inverted indexes.
"""
import collections
import terms
import bisect
import re
import itertools
import functools

def build_inverted_index(documents):
    """
    Create an inverted index

    :param documents: a map from document ids to document contents
    :return: a map from terms to an ordered list of document ids
    """
    index = collections.defaultdict(list)

    docids = sorted(documents.keys())

    for docid in docids:
        for term in terms.normalize(terms.split_whitespace(documents[docid])):
            if len(index[term]) == 0 or index[term][-1] != docid:
                index[term].append(docid)

    return index


def query_and(index, term1, term2):
    """
    Query and inverted index for documents containing both terms
    :param index: the inverted index to search
    :param term1: the first term to search for
    :param term2: the second term to search for
    :return: an iterator over the ids of all documents in the index containing both terms
    """
    term1list = index[term1]
    term2list = index[term2]

    return intersect_sorted(term1list, term2list)


def intersect_sorted(list1, list2):
    """
    Calculate the intersection of two sorted lists
    :param list1: a list, must already be sorted
    :param list2: another list, must already be sorted
    :return: an iterator over the intersection of the two lists
    """
    iter1 = iter(list1)
    iter2 = iter(list2)
    term1 = next(iter1)
    term2 = next(iter2)

    while term1 is not None and term2 is not None:
        if term1 == term2:
            yield term1
            term1 = next(iter1)
            term2 = next(iter2)
        elif term1 < term2:
            term1 = next(iter1)
        else:
            term2 = next(iter2)


def query_or(index, term1, term2):
    """
    Query an inverted index for documents containing either term
    :param index: the index to search
    :param term1: the first term to search for
    :param term2: the second term to search for
    :return: an iterator over the ids of all documents in the index containing either term
    """
    term1list = index[term1]
    term2list = index[term2]

    return union_sorted(term1list, term2list)


def union_sorted(list1, list2):
    """
    Calculate the union of two sorted lists
    :param list1: a list, must already be sorted
    :param list2: another list, must already be sorted
    :return: an iterator over the union of both lists, also sorted
    """

    iter1 = iter(list1)
    iter2 = iter(list2)

    term1 = next(iter1, None)
    term2 = next(iter2, None)

    while term1 is not None and term2 is not None:
        if term1 == term2:
            yield term1
            term1 = next(iter1, None)
            term2 = next(iter2, None)
        elif term1 < term2:
            yield term1
            term1 = next(iter1, None)
        else:
            yield term2
            term2 = next(iter2, None)

    if term1 is not None:
        yield term1
        yield from iter1
    elif term2 is not None:
        yield term2
        yield from iter2


def build_position_index(documents):
    """
    Given a map from document ids to document contents, return a map from terms to a list of positions within each
    document at which that term occurs.
    """
    index = collections.defaultdict(list)

    docids = sorted(documents.keys())

    for docid in docids:
        for (position, term) in enumerate(terms.normalize(terms.split_whitespace(documents[docid]))):
            if len(index[term]) == 0 or index[term][-1][0] != docid:
                index[term].append((docid, [position]))
            else:
                index[term][-1][1].append(position)

    return index


def positional_intersect(position_list1,
                         position_list2,
                         proximity):
    """
    Given two positional posting lists, find documents where there is an element in the first list within a specified
    distance from an element in the second list.

    :param position_list1: A positional list, that is, a list of pairs of document ids and ordered positions,
    ordered by document id
    :param position_list2: A second positional list.
    :param proximity: The proximity to consider
    :return: An iterator over document id, position list pairs, giving all the matching occurences of the first term
    """

    iter1 = iter(position_list1)
    iter2 = iter(position_list2)

    (docid1, term_positions1) = next(iter1)
    (docid2, term_positions2) = next(iter2)

    while True:
        if docid1 == docid2:
            locations = []
            potential_matches = []
            position_iter1 = iter(term_positions1)
            position_iter2 = iter(term_positions2)
            position1 = next(position_iter1, None)
            position2 = next(position_iter2, None)

            while position1 is not None:
                while position2 is not None:
                    if abs(position1 - position2) <= proximity:
                        potential_matches.append(position2)
                    elif position2 > position1:
                        break
                    position2 = next(position_iter2, None)

                #TODO: Why is this here?
                while len(potential_matches) > 0 and abs(potential_matches[0] - position1) > proximity:
                    potential_matches = potential_matches[1:]

                if len(potential_matches) > 0:
                    locations.append(position1)

                position1 = next(position_iter1, None)

            if len(locations) > 0:
                yield (docid1, locations)

            (docid1, term_positions1) = next(iter1)
            (docid2, term_positions2) = next(iter2)

        elif docid1 < docid2:
            (docid1, position1) = next(iter1)
        else:
            (docid2, position2) = next(iter2)


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

