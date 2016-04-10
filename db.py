import rethinkdb as r


def db_connect():
    r.connect("localhost", 28015, db='ignitechat').repl()


def db_get_phonenumber(phone_number):
    db_connect()
    results = list(r.table("sms_subscribers").get_all(phone_number, index="number").run())
    if results == []:
        return False
    else:
        print results[0]
        return True


def db_set_phonenumber(phone_number, msid):
    db_connect()
    r.table('sms_subscribers').insert([{'number':phone_number, 'subscription_msid': msid }]).run()


def db_remove_phonenumber(phone_number):
    db_connect()
    r.table("sms_subscribers").filter(r.row["number"] == phone_number).delete().run()


def db_list_all_records(table):
    db_connect()
    cursor = r.table(table).run()
    for document in cursor:
        print document
