import json
from ConfigParser import SafeConfigParser
from os import path


parser = SafeConfigParser()
parser.read(path.join(path.expanduser('~'), '.ignite_chat.ini'))

json_db_file = parser.get('main', 'json_db_path')

try:
    with open(json_db_file, 'rb') as f:
       db = json.load(f)
except (IOError, ValueError):
    db = {'sms_subscribers': {}}


def write_data():
    with open(json_db_file, 'wb') as f:
        json.dump(db, f)


def db_get_phonenumber(phone_number):
    if phone_number in db['sms_subscribers']:
        return db['sms_subscribers'][phone_number]
    else:
        return False

def db_set_phonenumber(phone_number, msid):
    db['sms_subscribers'][phone_number] = {'subscription_msid': msid }
    write_data()


def db_remove_phonenumber(phone_number):
    del db['sms_subscribers'][phone_number]
    write_data()


def db_list_all_subscribers():
    for k,v in db['sms_subscribers'].iteritems():
        return k,v


