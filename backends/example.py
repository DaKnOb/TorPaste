#!../bin/python

"""
This is an example backend which can serve as a template for you to add
more backends to TorPaste. Simply edit the content of the functions and
follow the contracts and guidelines in the comments. Please  note  that
this file is being imported by the Flask application, which is run with
Gunicorn with 8 workers.

Error Handling:
In order to handle any errors and to keep TorPaste sane, we  are  using
generic exceptions and we leave the control flow up to the backend dev-
eloper. That means that when writting this file, you must make some, if
not all the decisions on what the TorPaste  user  will  experience. So,
if you face an error that can be overcomed by  any  means,  you  should
raise the ErrorException and pass some text that will be visible to the
user. If this exception is raised, it means that the desired action has
failed and the user should be returned back to the original screen.  If
the WarningException is raised, it means that the  action is partly co-
mplete, the user should move to the intended view / screen, but also be
warned about something you want. This can be used for example in a case
where part of the action is complete but it did not finish as intended.
The InfoException can be raised when everything went fine, however  you
want to show the user an informational message. Please  note  that  the
backends must have no application logic: you can  assume  that  since a
certain method was called, say for example to create a new  paste,  the
web application already checked (or doesn't care) if a paste with  this
ID already exists. In addition to that, no data sanitization is needed.
Please make sure that all error messages shown to the user are friendly
and there's no leakage of private information (don't throw an exception
whose message is the MySQL error for example).

Backwards Compatibility
In order for TorPaste to work without any problem, all backends must be
backwards compatible with their previous versions. This  of  course  is
not easy to achieve. You may decide that you need a  schema  change  in
your database that breaks existing changes. In order to  overcome  this
problem, you can use the below provided  initialize_backend()  that  can
migrate the entire database to the new version before the  app  starts.
However,  this  is  impractical with large databases and can also cause
problems with parallel executions of this app (either in a  cluster  or
from multiple workers). This problem can be solved by having your code,
say for example update to the new format, every time a paste  is  read.
That means that all pastes will start to update to the new format  over
time, as they are being viewed by people. For this reason, as  well  as
the possibility of users upgrading from very very old versions to newer
ones, your code must be able to support any and all  past  versions  of
your backend. If your backend is merged upstream, and therefore  relea-
sed, even if it's for one single minor version, you must keep  support-
ing that indefinitely. So in order to avoid complicated backends in the
future,  please  think  very carefully before designing your persistent
storage, be it database tables, folders and files, or anything else.
"""

import exceptions as e


def initialize_backend():
    """
    This method is called when the Flask application starts.
    Here you can do any initialization that may be required,
    such as connecting to a remote database or making sure a file exists.
    """
    raise e.ErrorException("Hello world")
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

    raise e.WarningException("Hi there")
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

    return False


def get_paste_contents(paste_id):
    """
    This method must return all the paste contents in UTF-8 encoding for
    a given Paste ID. The Paste ID is typically in ASCII, and it is
    guaranteed that this Paste ID exists.
    :param paste_id: ASCII string which represents the ID of the paste
    :return: the content of the paste in UTF-8 encoding
    """

    return "Hello"


def get_paste_metadata(paste_id):
    """
    This method must return a Python Dictionary with all the currently
    stored metadata for the paste with the given Paste ID. All keys of
    the dictionary are typically in ASCII, while all values are in
    UTF-8. It is guaranteed that the Paste ID exists.
    :param paste_id: ASCII string which represents the ID of the paste
    :return: a dictionary with the metadata of a given paste
    """

    return {"Key": "Value"}


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

    if get_paste_metadata(paste_id)[key]:
        return get_paste_metadata(paste_id)[key]
    else:
        return None


def get_all_paste_ids():
    """
    This method must return a Python list containing each and every
    Paste ID, in ASCII. The order does not matter so it can be the same
    or it can be different every time this function is called. In the
    case of no pastes, the method must return a Python list with a
    single item, whose content must be equal to 'none'.
    :return: a list containing all paste IDs
    """

    return ['none']
