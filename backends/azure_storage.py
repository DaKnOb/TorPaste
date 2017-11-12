from os import getenv

from azure.common import AzureException
from azure.storage.blob import BlockBlobService
from azure.storage.blob import Include

from backends.utils import getenv_int
from backends.utils import getenv_required
from backends.utils import wrap_exception

_ENV_ACCOUNT_NAME = 'TP_BACKEND_AZURE_STORAGE_ACCOUNT_NAME'
_ENV_ACCOUNT_KEY = 'TP_BACKEND_AZURE_STORAGE_ACCOUNT_KEY'
_ENV_CONTAINER = 'TP_BACKEND_AZURE_STORAGE_CONTAINER'
_ENV_TIMEOUT = 'TP_BACKEND_AZURE_STORAGE_TIMEOUT_SECONDS'

_DEFAULT_CONTAINER = 'torpaste'
_DEFAULT_TIMEOUT = 10

_blob_service = None  # type: BlockBlobService
_container = None  # type: str
_timeout = None  # type: int


_wrap_azure_exception = wrap_exception(
    AzureException,
    'Error while communicating with the Azure Storage Service')


@_wrap_azure_exception
def initialize_backend():
    global _blob_service
    global _container
    global _timeout

    _blob_service = BlockBlobService(
        account_name=getenv_required(_ENV_ACCOUNT_NAME),
        account_key=getenv_required(_ENV_ACCOUNT_KEY))
    _container = getenv(_ENV_CONTAINER, _DEFAULT_CONTAINER)
    _timeout = getenv_int(_ENV_TIMEOUT, _DEFAULT_TIMEOUT)

    _blob_service.create_container(
        _container, fail_on_exist=False, timeout=_timeout)


@_wrap_azure_exception
def new_paste(paste_id, paste_content):
    _blob_service.create_blob_from_text(
        _container, paste_id, paste_content, timeout=_timeout)


@_wrap_azure_exception
def update_paste_metadata(paste_id, metadata):
    _blob_service.set_blob_metadata(
        _container, paste_id, metadata, timeout=_timeout)


@_wrap_azure_exception
def does_paste_exist(paste_id):
    return _blob_service.exists(
        _container, paste_id, timeout=_timeout)


@_wrap_azure_exception
def get_paste_contents(paste_id):
    blob = _blob_service.get_blob_to_text(
        _container, paste_id, timeout=_timeout)

    return blob.content


@_wrap_azure_exception
def get_paste_metadata(paste_id):
    return _blob_service.get_blob_metadata(
        _container, paste_id, timeout=_timeout)


@_wrap_azure_exception
def get_paste_metadata_value(paste_id, key):
    metadata = _blob_service.get_blob_metadata(
        _container, paste_id, timeout=_timeout)

    return metadata.get(key)


def _filters_match(metadata, filters, fdefaults):
    for metadata_key, filter_value in filters.items():
        try:
            metadata_value = metadata[metadata_key]
        except KeyError:
            metadata_value = fdefaults.get(metadata_key)

        if metadata_value != filter_value:
            return False

    return True


def _get_all_paste_ids(filters, fdefaults):
    blobs = _blob_service.list_blobs(
        _container, include=Include.METADATA, timeout=_timeout)

    for blob in blobs:
        if _filters_match(blob.metadata, filters, fdefaults):
            yield blob.name


@_wrap_azure_exception
def get_all_paste_ids(filters={}, fdefaults={}):
    return list(_get_all_paste_ids(filters, fdefaults))
