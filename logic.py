#!bin/python

import time
from hashlib import sha256


def format_size(size):
    """
    This method formats an arbitrary amount of bytes to a printable
    string. For example 1024 will be converted to 1.0 kB.
    :param size: an amount of bytes
    :return: a string that's ready to be printed representing
             approximately the amount of bytes in a human readable
             way.
    """
    scales = ["bytes", "kB", "MB", "GB", "TB", "PB"]
    count = 0
    while (1 == 1):
        if (size > 1024.0):
            size /= 1024.0
            count += 1
        else:
            break
    return str(round(size, 1)) + " " + scales[count]


def create_new_paste(content, metadata, config):
    """
    This method is responsible for creating new pastes by directly
    talking to the currently used backend. It is also responsible
    for ensuring the current input is valid, such as for example that
    it is under the Maximum Allowed Paste Size.
    :param content: The content of the paste to create
    :param metadata: Metadata for the new paste
    :param config: The TorPaste configuration object
    :return: The result of the action (ERROR/OK), some data (error message/
             Paste ID) as well as the suggested HTTP Status Code to return.
    """

    try:
        visibility = metadata['visibility']
        if visibility not in config['ENABLED_PASTE_VISIBILITIES']:
            return "ERROR", "The requested paste visibility is not " +\
                "currently supported."
    except KeyError:
        visibility = config['ENABLED_PASTE_VISIBILITIES'][0]

    try:
        paste_id = str(sha256(content.encode('utf-8')).hexdigest())
    except Exception:
        return "ERROR", "An issue occurred while handling the paste. " +\
            "Please try again later. If the problem persists, try " +\
            "notifying a system administrator."

    if (len(content.encode('utf-8')) > config['MAX_PASTE_SIZE']):
        return "ERROR", "The paste sent is too large. This TorPaste " +\
            "instance has a maximum allowed paste size of " +\
            format_size(config['MAX_PASTE_SIZE']) + "."

    try:
        config['b'].new_paste(paste_id, content)
    except config['b'].e.ErrorException as errmsg:
        return "ERROR", errmsg

    try:
        config['b'].update_paste_metadata(
            paste_id,
            {
                "date": str(int(time.time())),
                "visibility": visibility
            }
        )
    except config['b'].e.ErrorException as errmsg:
        return "ERROR", errmsg

    return "OK", paste_id


def view_existing_paste(paste_id, config):
    """
    This method is responsible for checking if a paste with a given Paste ID
    exists, and if it does, return its contents and needed metadata in order
    for the View Paste view to work.
    :param paste_id: The Paste ID to look for.
    :param config: The TorPaste configuration object
    :return: The result of the action (ERROR/WARNING/OK), some data (error
             message / data tuple) as well as the suggested HTTP Status Code
             to return.
    """
    if (not paste_id.isalnum()):
        return "ERROR", "Invalid Paste ID. Please check the link " +\
            "you used or use the Pastes button above.", 400

    if (len(paste_id) != 64):
        return "ERROR", "Paste ID has invalid length. Paste IDs " +\
           "are 64 characters long. Please make sure the link you " +\
           "clicked is correct or use the Pastes button above.", 400

    if (not config['b'].does_paste_exist(paste_id)):
        return "ERROR", "A paste with this Paste ID could not be " +\
            "found. Sorry.", 404

    try:
        paste_content = config['b'].get_paste_contents(paste_id)
    except config['b'].e.ErrorException as errmsg:
        return "ERROR", errmsg, 500

    try:
        paste_date = config['b'].get_paste_metadata_value(paste_id, "date")
    except config['b'].e.ErrorException as errmsg:
        return "ERROR", errmsg, 500
    except config['b'].e.WarningException as errmsg:
        return "WARNING", errmsg, 500

    return "OK", (paste_content, paste_date), 200


def get_paste_listing(config, filters={}, fdefaults={}):
    """
    This method is responsible for returning a list of all currently saved
    pastes, or a list with only one element ("none") if there are no pastes.
    :param config: The TorPaste configuration object
    :param filters: a dictionary of filters to apply on the listing
    :return: A list with all Paste IDs of all stored pastes. If no stored
             pastes exist, a list with only one element, "none".
    """
    if (not config['PASTE_LIST_ACTIVE']):
        return "ERROR", "Paste listing has been disabled by the " +\
            "administrator.", 503

    b = config['b']

    try:
        paste_list = b.get_all_paste_ids(filters, fdefaults)
    except b.e.ErrorException as errmsg:
        return "ERROR", errmsg, 500

    if (paste_list[0] == "none"):
        return "OK", "none", 200

    return "OK", paste_list, 200
