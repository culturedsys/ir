"""
Load a set of documents
"""

import pathlib


def load_documents(dir="documents", ext="txt"):
    """
    Load all documents with the specified extension in the specified directory, using the file name as the document id.
    :param dir: the directory to load from, "documents" by default
    :param ext: the extension to look for, "txt" by default
    :return: a pair of maps, the first from document id to document id to filename, the second from document id to
    contents
    """

    filenames = {}
    contents = {}

    p = pathlib.Path(dir)

    for (i, path) in enumerate(p.glob('*.' + ext)):
        name = path.parts[-1]

        with path.open() as f:
            content = ''.join(f)

        filenames[i] = name
        contents[i] = content

    return filenames, contents
