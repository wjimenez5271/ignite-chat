from boto.s3.key import Key
from boto.s3.connection import S3Connection
import logging

logger = logging.getLogger(__name__)

bucket_name = 'ignite_chat_data'
conn = S3Connection()

bucket = conn.get_bucket(bucket_name)
k = Key(bucket)
k.key = 'db_json'


def get_data(json_file):
    logger.info('Fetching data from S3')
    with open(json_file, 'rb') as f:
        k.get_contents_to_file(f)


def put_data(json_file):
    logginger.info('Storing data to S3')
    k.set_contents_from_file(json_file)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--get_data', action='store_true')
    parser.add_argument('--store_data', action='store_true')
    parser.add_argument('--json_path', default='db.json')
    args = parser.parse_args()
    
    if args.get_data:
        get_data(arg.json_path)
    elif args.store_data:
        put_data(args.json_path)
