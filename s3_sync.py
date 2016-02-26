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
conn = S3Connection()

bucket = conn.get_bucket(bucket_name)
k = Key(bucket)
k.key = 'db.json'

def get_data():
    logger.info('Fetching data from S3')
    with open(json_file, 'rb') as f:
        k.get_contents_to_file(f)


def put_data():
    logger.info('Storing data to S3')
    k.set_contents_from_file(json_file)


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
