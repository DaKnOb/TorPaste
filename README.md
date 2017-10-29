# TorPaste
A Pastebin for Tor

![TravisCI](https://api.travis-ci.org/DaKnOb/TorPaste.svg?branch=master)
![Current Version](https://img.shields.io/github/tag/daknob/torpaste.svg)
![Open Issues](https://img.shields.io/github/issues-raw/daknob/torpaste.svg)
![Closed Issues](https://img.shields.io/github/issues-closed-raw/daknob/torpaste.svg)
![License](https://img.shields.io/github/license/daknob/torpaste.svg)
![Awesome People](https://img.shields.io/github/contributors/daknob/torpaste.svg)
![Pull Requests](https://img.shields.io/github/issues-pr-raw/daknob/torpaste.svg)
![Closed Pull Requests](https://img.shields.io/github/issues-pr-closed-raw/daknob/torpaste.svg)
![Docker Pulls](https://img.shields.io/docker/pulls/daknob/torpaste.svg)

## What is this?

TorPaste is a simple Pastebin service written in Python using the Flask framework.
It is targeted to users inside Tor and can be easily setup as a Hidden Service.
As of version v0.4 TorPaste supports multiple backends for storage of data, however
currently only the local filesystem backend is implemented. TorPaste has been designed
in order to need no cookies or JavaScript and to run without problems in the Tor Browser
with the Security and Privacy Settings set to Maximum.

Unfortunately, the lack of client-side code means all the pastes are stored in
**plaintext** format, readable by anyone, including the server. For this reason,
all pastes are indexed and available publicly by default to anyone to see as well.
Do not use this service for sensitive data.

## How to run this?

You can run this locally in your system:

```bash
sudo pip install -r requirements.txt
python torpaste.py
```

or using `virtualenv`:

```bash
virtualenv .
bin/pip install -r requirements.txt
./torpaste.py
```

You can also run this using Docker:

```bash
docker build -t daknob/torpaste .
docker run -d -p 80:80 daknob/torpaste
```

or from Docker Hub:

```bash
docker run -d -p 80:80 daknob/torpaste
```

If you want to run TorPaste in production
( [don't worry, you're not alone](https://paste.daknob.net) ), consider using
a specific tag such as `daknob/torpaste:v0.3`. The `latest` tag is synchronized
automatically with the `master` branch of this repo and therefore is the bleeding
edge version. In both cases, don't forget to update your version of TorPaste for
bug fixes, security patches, and new features. This can be done by running:

```bash
docker pull daknob/torpaste
```

or of course, for a specific version:

```bash

docker pull daknob/torpaste:v0.3
```

and then stop the previous container and start a new one. It is important to use
the same settings when launching a new container, so any `-p` / `-e` / `-v` arguments
need to be specified again.

If you're using Docker and you need the pastes to persist, you can mount the paste
directory to the local filesystem. This will store all pastes in the host and not
inside the container. This can be done as such:

```bash
docker run -d -p 80:80 -v /path/to/host/:/torpaste/pastes daknob/torpaste
```

## Backends
TorPaste is extensible and supports multiple backends for storage of its data. As
of now, the only one implemented is the `filesystem` backend, which stores all data
as files in the local filesystem. If you're interested in writting a backend, please
see [Issue #15](https://github.com/DaKnOb/TorPaste/issues/15) for some ideas. For
more information in the development of new backends, there's an `example.py` file
inside the `backends` folder which you can copy and start editing right away. The
file includes a lot of useful information and design documentation for your new
backend, but if you still want to look at an example, the `backends/filesystem.py`
is there as well to have a look.

### filesystem
This is the first backend available for TorPaste and stores everything in the local
filesystem. TorPaste versions prior to v0.4 had this backend hardcoded and therefore
this is an improved implementation so we can maintain backwards compatibility without
running any migration scripts. It is also the simplest backend and it is used by
default.

### azure_storage
This is a backend based on the [Azure Storage Service](https://azure.microsoft.com/en-us/services/storage/blobs/).
The backend is activated by setting `TP_BACKEND=azure_storage`. Each paste is
stored as a separate blob which means that this backend supports paste sizes [up to 5TB](https://docs.microsoft.com/en-us/azure/storage/common/storage-scalability-targets).
Metadata associated with a paste is stored directly on the blob via [custom metadata fields](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-properties-metadata).

### postgres
This is a backend based on the Postgres database. The backend assumes that you
have a running Postgres database set up that the application can connect to via
a connection string. The backend is activated by setting `TP_BACKEND=postgres`.

## Configuration
TorPaste can be configured by using `ENV`ironment Variables. The list of available
variables as well as their actions is below so you can use them to parameterize your
installation of the software. Please note that all these variables have a default
value which may not work well for you, but makes them all optional.

### Available ENV Variables

* `TP_WEBSITE_TITLE` : Use this variable to set the TorPaste Title inside the HTML
`<title></title>` tags. *Default:* `Tor Paste`
* `TP_BACKEND` : Use this variable to select a backend for TorPaste to use. The
available backends for each version are included in the `COMPATIBLE_BACKENDS` variable
inside `torpaste.py`. *Default:* `filesystem`
* `TP_PASTE_MAX_SIZE` : Use this variable to set the maximum paste size, in bytes. The
possible values are formatted as `<amount> <unit>`, for example `10 M`, or `128 B`,
or `16 k`. Any value that starts with `0` changes this limit to unlimited. *Default:*
`0`
* `TP_PASTE_LIST_ACTIVE` : Use this variable to enable or disable the paste listing
available in the `Pastes` menu. *Default:* `True`
* `TP_CSP_REPORT_URI` : Use this variable to set a `report-uri` for the Content Security
Policy of TorPaste. If this variable is not set, no `report-uri` is added, which is the
default behavior.
* `TP_ENABLED_PASTE_VISIBILITIES` : Use this variable to select the available paste
visibilities, separated by a comma. Example: "public,unlisted". The available backends
for each version are included in the `AVAILABLE_VISIBILITIES` variable inside 
`torpaste.py`. *Default:* `public`.

### Backend ENV Variables
Each backend may need one or more additional `ENV` variables to work. For example,
a MySQL backend may need the `HOST`, `PORT`, `USERNAME`, and `PASSWORD` to connect
to the database. To prevent conflicts, all these variables will be available as
`TP_BACKEND_BACKENDNAME_VARIABLE` where `BACKENDNAME` is the name of the backend,
such as `MYSQL` and the `VARIABLE` will be the name of the variable, such as `HOST`.

#### azure_storage

This backend assumes that you have an Azure subscription and a storage account
in that subscription. You can learn how to set up a new subscription [here](https://azure.microsoft.com/en-us/free/)
and how to set up a storage account [here](https://docs.microsoft.com/en-us/azure/storage/common/storage-create-storage-account).

* `TP_BACKEND_AZURE_STORAGE_ACCOUNT_NAME` : Use this variable to set the name of
  the Azure storage account to use.
* `TP_BACKEND_AZURE_STORAGE_ACCOUNT_KEY` : Use this variable to set the key of
  the Azure storage account to use.
* `TP_BACKEND_AZURE_STORAGE_CONTAINER` : Use this variable to set the name of
  the container in which to store pastes and metadata. If the container does not
  exist, it will be created. *Default:* `torpaste`.
* `TP_BACKEND_AZURE_STORAGE_TIMEOUT_SECONDS` : Use this variable to set the
  timeout in seconds for all requests to Azure. *Default:* `10`.

#### postgres

* `TP_BACKEND_POSTGRES_DATABASE_CONNECTION` : Use this variable to set the
  connection string with which to connect to the Postgres database.