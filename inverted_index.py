"""
Functions relating to constructing and inverted indexes.
"""
import collections
import terms


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
