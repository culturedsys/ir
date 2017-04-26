import collections


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

