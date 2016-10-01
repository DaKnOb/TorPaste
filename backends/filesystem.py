#!../bin/python

from . import exceptions as e
import os

# initializeBackend()
## This method is called when the Flask application starts. Here you can do
## any initialization that may be required, such as connecting to a remote
## database or making sure a file exists.

def initializeBackend():
	try:
		os.mkdirs("pastes")
	except:
		pass
	return

# newPaste(pasteid, pastecontent)
## This method is called when the Flask application wants to create a new
## paste. The arguments given are the Paste ID, which is a paste identifier
## that is not neccesarily unique, as well as the paste content. Please note
## that the paste must be retrievable given the above Paste ID as well as
## the fact that pasteid is (typically) an ASCII string while pastecontent
## can (and will) contain UTF-8 characters.

def newPaste(pasteid, pastecontent):
	a = pasteid[0:2]
	b = pasteid[2:4]

	try:
		os.makedirs("pastes/" + a + "/" + b)
	except:
		pass

	ppath = "pastes/" + a + "/" + b + "/" + pasteid

	try:
		with open(ppath, "w+") as fd:
			fd.write(pastecontent)
	except:
		raise e.ErrorException("An issue occured with the local filesystem. Please try again later. If the problem perists, try notifying a system administrator.")

	return

# updatePasteMetadata(pasteid, metadata)
## This method is called by the Flask application to update a paste's
## metadata. For this to happen, the application passes the Paste ID,
## which is typically an ASCII string, as well as a Python dictionary
## that contains the new metadata. This method must overwrite any and
## all metadata with the passed dictionary. For example, if a paste has
## the keys a and b and this method is called with only keys b and c,
## the final metadata must be b and c only, and not a.

def updatePasteMetadata(pasteid, metadata):
	a = pasteid[0:2]
	b = pasteid[2:4]

	try:
		os.makedirs("pastes/" + a + "/" + b)
	except:
		pass

	ppath = "pastes/" + a + "/" + b + "/" + pasteid

	try:
		for j in os.listdir("pastes/" + a + "/" + b):
			if ("." in j) and (pasteid in j):
				os.remove("pastes/" + a + "/" + b + "/" + j)
	except:
		raise e.ErrorException("An issue occured with the local filesystem. Please try again later. If the problem persists, try notifying a system administrator.")

	try:
		for k, v in metadata.items():
			with open(ppath + "." + k, "w+") as fd:
				fd.write(v)
	except:
		raise e.ErrorException("An issue occured with the local filesystem. Please try again later. If the problem persists, try notifying a system administrator.")

	return

# doesPasteExist(pasteid)
## This method is called when the Flask application wants to check if a
## paste with a given Paste ID exists. The Paste ID is (typically) an
## ASCII string and your method must return True if a paste with this ID
## exists, or False if it doesn't.

def doesPasteExist(pasteid):
	a = pasteid[0:2]
	b = pasteid[2:4]

	return os.path.isfile("pastes/" + a + "/" + b + "/" + pasteid)

# getPasteContents(pasteid)
## This method must return all the paste contents in UTF-8 encoding for
## a given Paste ID. The Paste ID is typically in ASCII, and it is
## guaranteed that this Paste ID exists.

def getPasteContents(pasteid):
	a = pasteid[0:2]
	b = pasteid[2:4]

	try:
		with open("pastes/" + a + "/" + b + "/" + pasteid) as fd:
			return fd.read()
	except:
		raise e.ErrorException("An issue occured with the local filesystem. Please try again later. If the problem persists, try notifying a system administrator.")

# getPasteMetadata(pasteid)
## This method must return a Python Dictionary with all the currently
## stored metadata for the paste with the given Paste ID. All keys of
## the dictionary are typically in ASCII, while all values are in
## UTF-8. It is guaranteed that the Paste ID exists.

def getPasteMetadata(pasteid):
	a = pasteid[0:2]
	b = pasteid[2:4]

	ret = {}

	try:
		for f in os.listdir("pastes/" + a + "/" + b + "/"):
			if (pasteid in f) and ("." in f):
				t = f.split(".")[1]
				with open("pastes/" + a + "/" + b + "/" + f, "r") as fd:
					ret[t] = fd.read()
	except:
		raise e.ErrorException("An issue occured with the local filesystem. Please try again later. If the problem persists, try notifying a system administrator.")

	if ( len(ret) == 0 ):
		raise e.WarningException("Failed to load Paste Metadata. Some features like the paste date may not work. If the problem persists, try notifying a system administrator.")

	return ret

# getPasteMetadataValue(pasteid, key):
## This method must return the value of the metadata key provided for
## the paste whose Paste ID is provided. If the key is not set, the
## method should return None. You can assume that a paste with this
## Paste ID exists, and you can also assume that both parameters
## passed are typically ASCII.
def getPasteMetadataValue(pasteid, key):
	if ( getPasteMetadata(pasteid)[key] ):
		return getPasteMetadata(pasteid)[key]
	else:
		return None

# getAllPasteIDs()
## This method must return a Python list containing each and every
## Paste ID, in ASCII. The order does not matter so it can be the same
## or it can be different every time this function is called. In the
## case of no pastes, the method must return a Python list with a
## single item, whose content must be equal to 'none'.

def getAllPasteIDs():
	ret = []

	try:
		for i in os.listdir("pastes"):
			if ( "." in i ):
				continue
			for j in os.listdir("pastes/" + i):
				if ( "." in j ):
					continue
				for k in os.listdir("pastes/" + i + "/" + j):
					if ( "." in k ):
						continue
					ret.append(k)
		if ( len ( ret ) == 0 ):
			return ['none']

		return ret

	except:
		raise e.ErrorException("An issue occured with the local filesystem. Please try again later. If the problem persists, try notifying a system administrator.")
