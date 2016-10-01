#!bin/python

from flask import *
from hashlib import sha256
from datetime import datetime
import os, time
import backends.filesystem as b
app = Flask(__name__)

WEBSITE_TITLE = "Tor Paste"
VERSION = "0.5"

@app.route('/')
def index():
    return render_template(
		"index.html",
		title = WEBSITE_TITLE,
		version = VERSION,
		page = "main"
	)

@app.route("/new", methods=["GET", "POST"])
def newpaste():
	if(request.method == "GET"):
		return render_template(
			"index.html",
			title = WEBSITE_TITLE,
			version = VERSION,
			page = "new"
		)
	else:
		if(request.form['content']):
			try:
				PasteID = str(sha256(request.form['content']).hexdigest())
			except:
				return render_template(
					"index.html",
					title = WEBSITE_TITLE,
					version = VERSION,
					page = "new",
					error = "The current version of TorPaste supports ASCII characters only. UTF-8 support is coming soon."
				)
			try:
				b.newPaste(PasteID, request.form['content'])
			except b.e.ErrorException as errmsg:
				return render_template(
					"index.html",
					title = WEBSITE_TITLE,
					version = VERSION,
					page = "new",
					error = errmsg
				)

			try:
				b.updatePasteMetadata(
					PasteID,
					{
						"date": str(int(time.time()))
					}
				)
			except b.e.ErrorException as errmsg:
				return render_template(
					"index.html",
					title = WEBSITE_TITLE,
					version = VERSION,
					page = "new",
					error = errmsg
				)

			return redirect("/view/" + PasteID)
		else:
			return Response(
				render_template(
					"index.html",
					title = WEBSITE_TITLE,
					version = VERSION,
					error = "Please enter some text to include in the paste.",
					page = "new"
				),
				400
			)

@app.route("/view/<pasteid>")
def viewpaste(pasteid):
	if(not pasteid.isalnum()):
		return Response(
			render_template(
				"index.html",
				title = WEBSITE_TITLE,
				version = VERSION,
				error = "Invalid Paste ID. Please check the link you used or use Pastes button above.",
				page = "new"
			),
			400
		)
	if(len(pasteid) < 6):
		return Response(
			render_template(
				"index.html",
				title = WEBSITE_TITLE,
				version = VERSION,
				error = "Paste ID too short. Usually Paste IDs are longer than 6 characters. Please make sure the link you clicked is correct or use the Pastes button above.",
				page = "new"
			),
			400
		)
	if ( not b.doesPasteExist(pasteid) ):
		return Response(
			render_template(
				"index.html",
				title = WEBSITE_TITLE,
				version = VERSION,
				error = "A paste with this ID could not be found. Sorry.",
				page = "new"
			),
			404
		)

	try:
		PasteContent = b.getPasteContents(pasteid)
	except b.e.ErrorException as errmsg:
		return render_template(
			"index.html",
			title = WEBSITE_TITLE,
			version = VERSION,
			error = errmsg,
			page = "new"
		)

	try:
		PasteDate = b.getPasteMetadataValue(pasteid, "date")
	except b.e.ErrorException as errmsg:
		return render_template(
			"index.html",
			title = WEBSITE_TITLE,
			version = VERSION,
			error = errmsg,
			page = "new"
		)
	except b.e.WarningException as errmsg:
		return render_template(
			"index.html",
			title = WEBSITE_TITLE,
			version = VERSION,
			warning = errmsg,
			page = "new"
		)

	PasteDate = datetime.fromtimestamp(int(PasteDate) + time.altzone + 3600).strftime("%H:%M:%S %d/%m/%Y")
	PasteSize = formatSize(len(PasteContent))
	return render_template(
		"view.html",
		content = PasteContent,
		date = PasteDate,
		size = PasteSize,
		pid = pasteid,
		title = WEBSITE_TITLE,
		version = VERSION,
		page = "view"
	)

@app.route("/raw/<pasteid>")
def rawpaste(pasteid):
	if(not pasteid.isalnum()):
		return "No such paste", 404
	if(len(pasteid) < 6):
		return "No such paste", 404
	if ( not b.doesPasteExist(pasteid) ):
		return "No such paste", 404
	try:
		PasteContent = b.getPasteContents(pasteid)
	except b.e.ErrorException as errmsg:
		return Response(
			errmsg,
			500
		)
	return Response(
		PasteContent,
		mimetype = "text/plain"
	)

@app.route("/list")
def list():
	try:
		PasteList = b.getAllPasteIDs()
	except b.e.ErrorException as errmsg:
		return render_template(
			"index.html",
			title = WEBSITE_TITLE,
			version = VERSION,
			page = "new",
			error = errmsg
		)

	if ( PasteList[0] == 'none' ):
		return render_template(
			"list.html",
			pastes = ['none'],
			title = WEBSITE_TITLE,
			version = VERSION,
			page = "list"
		)
	return render_template(
		"list.html",
		pastes = PasteList,
		title = WEBSITE_TITLE,
		version = VERSION,
		page = "list"
	)

@app.route("/about")
def aboutTorPaste():
	return render_template(
		"about.html",
		title = WEBSITE_TITLE,
		version = VERSION,
		page = "about"
	)

# Functions
def formatSize(size):
	scales = ["bytes", "kB", "MB", "GB", "TB", "EB"]
	count = 0
	while(1==1):
		if(size > 1024.0):
			size = size / 1024.0
			count = count + 1
		else:
			break
	return str(round(size,1)) + " " + scales[count]

# Required Initialization Code
try:
	b.initializeBackend()
except:
	print("Failed to initialize backend")
	exit(1)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
