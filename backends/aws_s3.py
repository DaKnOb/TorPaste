from os import getenv

import boto3
from botocore.exceptions import ClientError

from backends.utils import getenv_required
from backends.utils import wrap_exception

_ENV_ACCESS_KEY_ID = 'TP_BACKEND_AWS_S3_ACCESS_KEY_ID'
_ENV_SECRET_ACCESS_KEY = 'TP_BACKEND_AWS_S3_SECRET_ACCESS_KEY'
_ENV_BUCKET = 'TP_BACKEND_AWS_S3_BUCKET'

_DEFAULT_BUCKET = 'torpaste'

_s3 = None
_bucket = None

_wrap_aws_exception = wrap_exception(
    ClientError,
    'Error while communicating with AWS S3')


@_wrap_aws_exception
def initialize_backend():
    global _s3
    global _bucket

    _s3 = boto3.resource(
        's3',
        aws_access_key_id=getenv_required(_ENV_ACCESS_KEY_ID),
        aws_secret_access_key=getenv_required(_ENV_SECRET_ACCESS_KEY))

    _bucket = getenv(_ENV_BUCKET, _DEFAULT_BUCKET)
    _s3.create_bucket(Bucket=_bucket)


@_wrap_aws_exception
def new_paste(paste_id, paste_content):
    _s3.Bucket(_bucket).put_object(
        Body=paste_content.encode('utf-8'),
        Key=paste_id)


@_wrap_aws_exception
def update_paste_metadata(paste_id, metadata):
    obj = _s3.Object(_bucket, paste_id)
    obj.metadata.clear()
    obj.metadata.update(metadata)
    obj.copy_from(CopySource={'Bucket': _bucket, 'Key': paste_id},
                  Metadata=obj.metadata,
                  MetadataDirective='REPLACE')


@_wrap_aws_exception
def does_paste_exist(paste_id):
    try:
        _s3.Object(_bucket, paste_id).load()
    except ClientError as ex:
        if ex.response['Error']['Code'] != '404':
            raise
        else:
            return False
    else:
        return True


@_wrap_aws_exception
def get_paste_contents(paste_id):
    body = _s3.Object(_bucket, paste_id).get()['Body'].read()
    return body.decode('utf-8')


@_wrap_aws_exception
def get_paste_metadata(paste_id):
    obj = _s3.Object(_bucket, paste_id)
    obj.load()
    return obj.metadata


@_wrap_aws_exception
def get_paste_metadata_value(paste_id, key):
    return get_paste_metadata(paste_id).get(key)


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
    for obj in _s3.Bucket(_bucket).objects.all():
        paste_id = obj.key
        metadata = get_paste_metadata(paste_id)
        if _filters_match(metadata, filters, fdefaults):
            yield paste_id


@_wrap_aws_exception
def get_all_paste_ids(filters={}, fdefaults={}):
    return list(_get_all_paste_ids(filters, fdefaults)) or ['none']
