#!../bin/python
# -*- coding: utf-8 -*-

import backends.exceptions as e
import os
import codecs


def initialize_backend():
    """
    This method is called when the Flask application starts.
    Here you can do any initialization that may be required,
    such as connecting to a remote database or making sure a file exists.
    """

    os.makedirs("pastes", exist_ok=True)


def new_paste(paste_id, paste_content):
    """
    This method is called when the Flask application wants to create a new
    paste. The arguments given are the Paste ID, which is a paste identifier
    that is not necessarily unique, as well as the paste content. Please note
    that the paste must be retrievable given the above Paste ID as well as
    he fact that paste_id is (typically) an ASCII string while paste_content
    can (and will) contain UTF-8 characters.
    :param paste_id: a not necessarily unique id of the paste
    :param paste_content: content of the paste (utf-8 encoded)
    :return:
    """

    a = paste_id[0:2]
    b = paste_id[2:4]

    os.makedirs("pastes/" + a + "/" + b, exist_ok=True)

    ppath = "pastes/" + a + "/" + b + "/" + paste_id

    try:
        with codecs.open(
            ppath,
            encoding="utf-8",
            mode="w+"
        ) as fd:
            fd.write(paste_content)
    except Exception:
        raise e.ErrorException(
            "An issue occurred with the local filesystem. Please try again " +
            "later. If the problem persists, try notifying a system " +
            "administrator."
        )

    return


def update_paste_metadata(paste_id, metadata):
    """
    This method is called by the Flask application to update a paste's
    metadata. For this to happen, the application passes the Paste ID,
    which is typically an ASCII string, as well as a Python dictionary
    that contains the new metadata. This method must overwrite any and
    all metadata with the passed dictionary. For example, if a paste has
    the keys a and b and this method is called with only keys b and c,
    the final metadata must be b and c only, and not a.
    :param paste_id: ASCII coded id of the paste
    :param metadata: dictionary containing the metadata
    :return:
    """

    a = paste_id[0:2]
    b = paste_id[2:4]

    os.makedirs("pastes/" + a + "/" + b, exist_ok=True)

    ppath = "pastes/" + a + "/" + b + "/" + paste_id

    try:
        for j in os.listdir("pastes/" + a + "/" + b):
            if ("." in j) and (paste_id in j):
                os.remove("pastes/" + a + "/" + b + "/" + j)
    except Exception:
        raise e.ErrorException(
            "An issue occurred with the local filesystem. Please try again " +
            "later. If the problem persists, try notifying a system " +
            "administrator."
        )

    try:
        for k, v in metadata.items():
            with codecs.open(
                ppath + "." + k,
                encoding="utf-8",
                mode="w+"
            ) as fd:
                fd.write(v)
    except Exception:
        raise e.ErrorException(
            "An issue occurred with the local filesystem. Please try again " +
            "later. If the problem persists, try notifying a system " +
            "administrator."
        )

    return


def does_paste_exist(paste_id):
    """
    This method is called when the Flask application wants to check if a
    paste with a given Paste ID exists. The Paste ID is (typically) an
    ASCII string and your method must return True if a paste with this ID
    exists, or False if it doesn't.
    :param paste_id: ASCII string which represents the ID of the paste
    :return: True if paste with given ID exists, false otherwise
    """

    a = paste_id[0:2]
    b = paste_id[2:4]

    return os.path.isfile("pastes/" + a + "/" + b + "/" + paste_id)


def get_paste_contents(paste_id):
    """
    This method must return all the paste contents in UTF-8 encoding for
    a given Paste ID. The Paste ID is typically in ASCII, and it is
    guaranteed that this Paste ID exists.
    :param paste_id: ASCII string which represents the ID of the paste
    :return: the content of the paste in UTF-8 encoding
    """

    a = paste_id[0:2]
    b = paste_id[2:4]

    try:
        with codecs.open(
            "pastes/" + a + "/" + b + "/" + paste_id,
            encoding="utf-8",
            mode="r"
        ) as fd:
            return fd.read()
    except Exception:
        raise e.ErrorException(
            "An issue occurred with the local filesystem. Please try again " +
            "later. If the problem persists, try notifying a system " +
            "administrator."
        )


def get_paste_metadata(paste_id):
    """
    This method must return a Python Dictionary with all the currently
    stored metadata for the paste with the given Paste ID. All keys of
    the dictionary are typically in ASCII, while all values are in
    UTF-8. It is guaranteed that the Paste ID exists.
    :param paste_id: ASCII string which represents the ID of the paste
    :return: a dictionary with the metadata of a given paste
    """

    a = paste_id[0:2]
    b = paste_id[2:4]

    ret = {}

    try:
        for f in os.listdir("pastes/" + a + "/" + b + "/"):
            if (paste_id in f) and ("." in f):
                t = f.split(".")[1]
                with codecs.open(
                    "pastes/" + a + "/" + b + "/" + f,
                    encoding="utf-8",
                    mode="r"
                ) as fd:
                    ret[t] = fd.read()
    except Exception:
        raise e.ErrorException(
            "An issue occurred with the local filesystem. Please try again " +
            "later. If the problem persists, try notifying a system " +
            "administrator."
        )

    if len(ret) == 0:
        raise e.WarningException(
            "Failed to load Paste Metadata. Some features like the paste " +
            "date may not work. If the problem persists, try notifying a " +
            "system administrator."
        )

    return ret


def get_paste_metadata_value(paste_id, key):
    """
    This method must return the value of the metadata key provided for
    the paste whose Paste ID is provided. If the key is not set, the
    method should return None. You can assume that a paste with this
    Paste ID exists, and you can also assume that both parameters
    passed are typically ASCII.
    :param paste_id: ASCII string which represents the ID of the paste
    :param key: key of the metadata
    :return: value of the metadata key provided for the given ID, None if
             the key wasn't set
    """

    try:
        return get_paste_metadata(paste_id)[key]
    except Exception:
        return None


def get_all_paste_ids(filters={}, fdefaults={}):
    """
    This method must return a Python list containing the ASCII ID of all
    pastes which match the (optional) filters provided. The order does not
    matter so it can be the same or it can be different every time this
    function is called. In the case of no pastes, the method must return a
    Python list with a single item, whose content must be equal to 'none'.
    :param filters: a dictionary of filters
    :param fdefaults: a dictionary with the default value for each filter
                      if it's not present
    :return: a list containing all paste IDs
    """

    allPastes = []

    try:
        for i in os.listdir("pastes"):
            if "." in i:
                continue
            for j in os.listdir("pastes/" + i):
                if "." in j:
                    continue
                for k in os.listdir("pastes/" + i + "/" + j):
                    if "." in k:
                        continue
                    allPastes.append(k)
    except Exception:
        raise e.ErrorException(
            "An issue occurred with the local filesystem. Please try again " +
            "later. If the problem persists, try notifying a system " +
            "administrator."
        )

    filtered = []
    for p in allPastes:
        keep = True

        try:
            for k, v in filters.items():
                gpmv = get_paste_metadata_value(p, k)
                if gpmv is None:
                    gpmv = fdefaults[k]
                if gpmv != v:
                    keep = False
                    break
        except (e.ErrorException, e.WarningException):
            keep = False

        if keep:
            filtered.append(p)

    if len(filtered) == 0:
        filtered = ['none']

    return filtered
