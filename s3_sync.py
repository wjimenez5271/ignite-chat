from boto.s3.key import Key
from boto.s3.connection import S3Connection
import logging
from ConfigParser import SafeConfigParser
from os import path

logger = logging.getLogger(__name__)


parser = SafeConfigParser()
parser.read(path.join(path.expanduser('~'), '.ignite_chat.ini'))

bucket_name = parser.get('main', 's3_bucket')
json_file = parser.get('main', 'json_db_path')
s3_key = parser.get('main', 's3_key')
aws_access_key = parser.get('main', 'aws_access_key')
aws_secret_access_key = parser.get('main', 'aws_secret_access_key')

conn = S3Connection(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_access_key)

bucket = conn.get_bucket(bucket_name)
k = Key(bucket)
k.key = s3_key


def get_data():
    logger.info('Fetching data from S3')
    with open(json_file, 'wb') as f:
        k.get_contents_to_file(f)


def put_data():
    logger.info('Storing data to S3')
    with open(json_file, 'rb') as f:
        k.set_contents_from_file(f)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--get_data', action='store_true')
    parser.add_argument('--store_data', action='store_true')

    args = parser.parse_args()
    
    if args.get_data:
        get_data()
    elif args.store_data:
        put_data()
