from boto.s3.key import Key
from boto.s3.connection import S3Connection

bucket_name = 'ignite_chat_data'
conn = S3Connection()

bucket = conn.get_bucket(bucket_name)
k = Key(bucket)
k.key = 'db_json'


def get_data(json_file):
    with open(json_file, 'rb') as f:
        k.get_contents_to_file(f)


def put_data(json_file):
    k.set_contents_from_file(json_file)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--get_data', action='store_true')
    args = parser.parse_args()
    if args.get_data:
        get_data('db.json')