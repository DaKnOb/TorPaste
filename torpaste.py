#!bin/python

from flask import *
from hashlib import sha256
from datetime import datetime
import os, time
app = Flask(__name__)

WEBSITE_TITLE = "Tor Paste"

@app.route('/')
def index():
    return render_template("index.html", title=WEBSITE_TITLE)

@app.route("/new", methods=["GET", "POST"])
def newpaste():
	if(request.method == "GET"):
		return render_template("index.html", title=WEBSITE_TITLE)
	else:
		if(request.form['content']):
			PasteID = str(sha256(request.form['content']).hexdigest())
			A = PasteID[0:2]
			B = PasteID[2:4]
			try:
				os.makedirs("pastes/" + A + "/" + B)
			except:
				pass
			PASTEPATH = "pastes/" + A + "/" + B + "/" + PasteID
			open(PASTEPATH, "w+").write(request.form['content'])
			open(PASTEPATH + ".date", "w+").write(str(int(time.time())))
			return redirect("/view/" + PasteID)
		else:
			return "<h1>Bad Request</h1>", 400

@app.route("/view/<pasteid>")
def viewpaste(pasteid):
	if(not pasteid.isalnum()):
		return "<h1>Bad Request</h1>", 400
	if(len(pasteid) < 6):
		return "<h1>Bad Request</h1>", 400
	A = pasteid[0:2]
	B = pasteid[2:4]
	PastePath = "pastes/" + A + "/" + B + "/" + pasteid
	if(not os.path.isfile(PastePath)):
		return "<h1>Paste not found</h1>", 404
	PasteContent = open(PastePath, "r").read()
	PasteDate = open(PastePath + ".date", "r").read()
	PasteDate = datetime.fromtimestamp(int(PasteDate) + time.altzone + 3600).strftime("%H:%M:%S %d/%m/%Y")
	PasteSize = formatSize(len(PasteContent))
	return render_template("view.html", content=PasteContent, date=PasteDate, size=PasteSize, pid=pasteid, title=WEBSITE_TITLE)

@app.route("/raw/<pasteid>")
def rawpaste(pasteid):
	if(not pasteid.isalnum()):
		return "No such paste", 404
	if(len(pasteid) < 6):
		return "No such paste", 404
	A = pasteid[0:2]
	B = pasteid[2:4]
	PastePath = "pastes/" + A + "/" + B + "/" + pasteid
	if(not os.path.isfile(PastePath)):
		return "No such paste", 404
	PasteContent = open(PastePath, "r").read()
	return Response(PasteContent, mimetype="text/plain")

@app.route("/list")
def list():
	PasteList = []
	if(len(os.listdir("pastes")) < 2):
		return render_template("list.html", pastes=['none'], title=WEBSITE_TITLE)
	for a in os.listdir("pastes"):
		if(a.find(".") != -1):
			continue
		for b in os.listdir("pastes/" + a):
			for paste in os.listdir("pastes/" + a + "/" + b):
				if(paste.find(".") == -1):
					PasteList.append(paste)
	return render_template("list.html", pastes=PasteList, title=WEBSITE_TITLE)

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

if __name__ == '__main__':
    app.run(host="0.0.0.0")
