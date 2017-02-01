"""
Load a set of documents
"""

import pathlib


def load_documents(dir="documents", ext="txt"):
    """
    Load all documents with the specified extension in the specified directory, using the file name as the document id.
    :param dir: the directory to load from, "documents" by default
    :param ext: the extension to look for, "txt" by default
    :return: a map from document id to document contents
    """

    result = {}

    p = pathlib.Path(dir)

    for path in p.glob('*.' + ext):
        name = path.parts[-1]

        with path.open() as f:
            content = ''.join(f)

        result[name] = content

    return result
