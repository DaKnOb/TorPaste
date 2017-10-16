#!../bin/python

import backends.exceptions as e
import redis
from os import getenv


def initialize_backend():
    """
    This method is called when the Flask application starts.
    Here you can do any initialization that may be required,
    such as connecting to a remote database or making sure a file exists.
    """
    global rb

    RedisHost = getenv("TP_BACKEND_REDIS_HOST") or "127.0.0.1"
    RedisPort = int(getenv("TP_BACKEND_REDIS_PORT") or "6379")
    RedisPass = getenv("TP_BACKEND_REDIS_PASSWORD") or None
    RedisDBI = int(getenv("TP_BACKEND_REDIS_DB_INDEX") or "1")

    rb = redis.StrictRedis(
        host=RedisHost,
        port=RedisPort,
        password=RedisPass,
        db=RedisDBI
    )

    if rb.ping() is not True:
        raise e.ErrorException(
            "Could not connect to the backend database. Please try again" +
            "later. If the error persists, please contact a system" +
            "administrator."
        )

    rb.save()

    return


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

    rb.set(paste_id, paste_content)

    rb.save()

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

    for md in rb.keys(paste_id + ".*"):
        rb.delete(md)
    for md in metadata:
        rb.set(paste_id + "." + md, metadata[md])

    rb.save()

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

    return rb.exists(paste_id)


def get_paste_contents(paste_id):
    """
    This method must return all the paste contents in UTF-8 encoding for
    a given Paste ID. The Paste ID is typically in ASCII, and it is
    guaranteed that this Paste ID exists.
    :param paste_id: ASCII string which represents the ID of the paste
    :return: the content of the paste in UTF-8 encoding
    """

    return rb.get(paste_id).decode("utf-8")


def get_paste_metadata(paste_id):
    """
    This method must return a Python Dictionary with all the currently
    stored metadata for the paste with the given Paste ID. All keys of
    the dictionary are typically in ASCII, while all values are in
    UTF-8. It is guaranteed that the Paste ID exists.
    :param paste_id: ASCII string which represents the ID of the paste
    :return: a dictionary with the metadata of a given paste
    """

    ret = {}

    f = rb.keys(paste_id + ".*")
    for md in f:
        ret[md.split(".")[1]] = rb.get(md).decode("utf-8")

    return str(ret)


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

    if rb.exists(paste_id + "." + key) is not True:
        return None
    else:
        return rb.get(paste_id + "." + key).decode("utf-8")


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

    ak = rb.keys()
    ap = []
    for k in ak:
        if b"." not in k:
            ap.append(k.decode("utf-8"))
    filt = []
    for p in ap:
        keep = True

        for k, v in filters.items():
            gpmv = get_paste_metadata_value(p, k)
            if gpmv is None:
                gpmv = fdefaults[k]
            if gpmv != v:
                keep = False
                break

        if keep:
            filt.append(p)

    if len(filt) == 0:
        filt = ['none']

    return filt
