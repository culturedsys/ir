"""
Methods of index compression
"""


def values_to_gaps(values):
    """
    Convert a list of integer values to a list of gaps
    """
    result = []
    offset = 0
    for (index, value) in enumerate(values):
        result.append(value - offset)
        offset = value

    return result


def gaps_to_values(gaps):
    """
    Convert a list of gaps to a list of values
    """
    result = []
    offset = 0

    for (index, gap) in enumerate(gaps):
        offset += gap
        result.append(offset)

    return result


def build_gapped_postings(index):
    """
    Convert an inverted index from terms to doc ids to one from terms to gaps
    """

    result = {}
    for (k, v) in index.items():
        result[k] = values_to_gaps(v)

    return result
