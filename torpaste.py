#!bin/python
# -*- coding: utf-8 -*-

import importlib
import time
from datetime import datetime
from os import getenv
import sys
import logic
from subprocess import check_output

from flask import Flask
from flask import Response
from flask import redirect
from flask import render_template
from flask import request

app = Flask(__name__)

# Calculate Software Version
VERSION = check_output(["git", "describe"]).decode("utf-8").replace("\n", "")

# Compatible Backends List
COMPATIBLE_BACKENDS = [
    "filesystem",
    "azure_storage",
    "postgres",
]

# Available list of paste visibilities
# public: can be viewed by all, is listed in /list
# unlisted: can be viewed by all, is not listed in /list ("hidden")
AVAILABLE_VISIBILITIES = ["public", "unlisted"]


@app.route('/')
def index():
    return render_template(
        "index.html",
        config=config,
        version=VERSION,
        page="main"
    )


@app.route("/new", methods=["GET", "POST"])
def new_paste():
    if request.method == "GET":
        return render_template(
            "index.html",
            config=config,
            version=VERSION,
            page="new"
        )
    else:
        if (request.form['content']):
            status, message = logic.create_new_paste(
                request.form['content'],
                request.form,
                config
            )
            if (status == "ERROR"):
                return Response(
                    render_template(
                        "index.html",
                        config=config,
                        version=VERSION,
                        page="new",
                        error=message
                    ),
                    400
                )

            if (status == "OK"):
                return redirect("/view/" + message)
        else:
            return Response(
                render_template(
                    "index.html",
                    config=config,
                    version=VERSION,
                    error="Please enter some text to include in the paste.",
                    page="new"
                ),
                400
            )


@app.route("/view/<pasteid>")
def view_paste(pasteid):
    status, data, code = logic.view_existing_paste(pasteid, config)

    if (status == "ERROR"):
        return Response(
            render_template(
                "index.html",
                config=config,
                version=VERSION,
                error=data,
                page="new"
            ),
            code
        )

    if (status == "OK"):
        paste_date = datetime.fromtimestamp(
            int(
                data[1]
            ) + time.altzone + 3600).strftime("%H:%M:%S %d/%m/%Y")

        paste_size = logic.format_size(len(data[0].encode('utf-8')))

    if (status == "WARNING"):
        paste_date = "Not available."

    return Response(
        render_template(
            "view.html",
            content=data[0],
            date=paste_date,
            size=paste_size,
            pid=pasteid,
            config=config,
            version=VERSION,
            page="view"
        ),
        200
    )


@app.route("/raw/<pasteid>")
def raw_paste(pasteid):
    status, data, code = logic.view_existing_paste(pasteid, config)

    if (status == "ERROR" and code >= 500):
        return Response(data, code, mimetype="text/plain")
    if (status == "ERROR"):
        return Response("No such paste", code, mimetype="text/plain")
    return Response(data[0], mimetype="text/plain")


@app.route("/list")
def list():
    listFilters = {"visibility": "public"}
    defaultFilters = {"visibility": "public"}
    status, data, code = logic.get_paste_listing(
        config,
        listFilters,
        defaultFilters
    )

    if (status == "ERROR"):
        return Response(
            render_template(
                "index.html",
                config=config,
                version=VERSION,
                page="new",
                error=data
            ),
            code
        )

    return Response(
        render_template(
            "list.html",
            pastes=data,
            config=config,
            version=VERSION,
            page="list"
        )
    )


@app.route("/about")
def about_tor_paste():
    return render_template(
        "about.html",
        config=config,
        version=VERSION,
        page="about"
    )


@app.after_request
def additional_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Xss-Protection"] = "1; mode=block"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Powered-By"] = "Tor Paste " + VERSION
    response.headers["Content-Security-Policy"] = "default-src 'none'; "
    response.headers["Content-Security-Policy"] += "img-src 'self'; "
    response.headers["Content-Security-Policy"] += "style-src 'self'; "
    if (config['CSP_REPORT_URI']):
        response.headers["Content-Security-Policy"] += "report-uri "
        response.headers["Content-Security-Policy"] += config['CSP_REPORT_URI']
    return response


# Required Initialization Code

# necessary for local modules import (backends, exceptions)
sys.path.append('.')


def load_config():
    """
    This method reads all configuration variables from environment variables
    and put them in a dictionary, which is then returned. Environment
    variables are used for convenience when using Docker (simply add
    an -e "TP_SOME_CONFIG_VAR=value" to docker run to modify the default
    configuration)

    :return: the configuration dictionary
    """

    # Web App <title>
    WEBSITE_TITLE = getenv("TP_WEBSITE_TITLE") or "Tor Paste"

    # Backend Used
    BACKEND = getenv("TP_BACKEND") or "filesystem"

    if BACKEND in COMPATIBLE_BACKENDS:
        b = importlib.import_module('backends.'+BACKEND)
    else:
        print(
            "Configured backend (" + BACKEND + ") is not compatible with " +
            "current version."
        )
        exit(1)

    # Maximum Paste Size
    MAX_PASTE_SIZE = getenv("TP_PASTE_MAX_SIZE") or "1 P"

    if MAX_PASTE_SIZE[0] == "0":
        MAX_PASTE_SIZE = "1 P"

    MAX_PASTE_SIZE = MAX_PASTE_SIZE.split(" ")

    try:
        AMOUNT = int(MAX_PASTE_SIZE[0])
        UNIT = MAX_PASTE_SIZE[1]
    except:
        print("Invalid TP_PASTE_MAX_SIZE: " + " ".join(MAX_PASTE_SIZE))
        exit(1)

    orders = ["B", "k", "M", "G", "T", "P"]

    if UNIT not in orders:
        print("Invalid Unit Size: " + UNIT)

    try:
        MAX_PASTE_SIZE = AMOUNT * 1024**orders.index(UNIT)
    except:
        print("An unknown error occured while determining max paste size.")
        exit(1)

    # Disable the paste listing feature
    PASTE_LIST_ACTIVE = getenv("TP_PASTE_LIST_ACTIVE") or True
    if PASTE_LIST_ACTIVE in ["False", "false", 0, "0"]:
        PASTE_LIST_ACTIVE = False

    # Content Security Policy Handling
    CSP_REPORT_URI = getenv("TP_CSP_REPORT_URI") or False

    # control the enabled paste visibilities:
    # public = can be opened by anyone and listed in /list
    # unlisted = can be opened by anyone, but are not listed in /list
    visibilityEnv = "TP_ENABLED_PASTE_VISIBILITIES"
    ENABLED_PASTE_VISIBILITIES = getenv(visibilityEnv) or 'public'
    ENABLED_PASTE_VISIBILITIES = ENABLED_PASTE_VISIBILITIES.replace(' ', '')
    ENABLED_PASTE_VISIBILITIES = ENABLED_PASTE_VISIBILITIES.split(',')
    # remove any potential whitespace
    ENABLED_PASTE_VISIBILITIES = [visibility
                                  for visibility in ENABLED_PASTE_VISIBILITIES
                                  if visibility in AVAILABLE_VISIBILITIES]

    if len(ENABLED_PASTE_VISIBILITIES) == 0:
        print("No valid visibilities found for pastes.")
        exit(1)

    return {
        "MAX_PASTE_SIZE": MAX_PASTE_SIZE,
        "WEBSITE_TITLE": WEBSITE_TITLE,
        "PASTE_LIST_ACTIVE": PASTE_LIST_ACTIVE,
        "CSP_REPORT_URI": CSP_REPORT_URI,
        "ENABLED_PASTE_VISIBILITIES": ENABLED_PASTE_VISIBILITIES,
        "b": b
    }


config = load_config()
b = config['b']

# Initialize Backend
try:
    b.initialize_backend()
except:
    print("Failed to initialize backend")
    exit(1)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
