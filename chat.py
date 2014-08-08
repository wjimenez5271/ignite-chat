from twilio.rest import TwilioRestClient
import imaplib
import email
from ConfigParser import SafeConfigParser
from pprint import pprint
import time
from HTMLParser import HTMLParser
import rethinkdb as r
import datetime
import sys
from email.parser import HeaderParser


parser = SafeConfigParser()
if not len(sys.argv) == 1:
    parser.read(sys.argv[1])
else:
    parser.read('/Users/wjimenez/Desktop/igchat.ini')

receiving_email = parser.get('main', 'receiving_email')
sms_window_start = parser.get('main', 'sms_window_start')
sms_window_end = parser.get('main', 'sms_window_end')
twilio_account = parser.get('twilio', 'account')
twilio_token = parser.get('twilio', 'token')
twilio_phone_number =  parser.get('twilio', 'phone_number')
imap_host = parser.get('imap', 'host')
imap_user = parser.get('imap', 'user')
imap_pass = parser.get('imap', 'pass')
imap_port = parser.get('imap', 'port')


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    """
    Remove HTML tags
    """
    s = MLStripper()
    s.feed(html)
    return s.get_data()

#TODO post to facebook
#TODO post to instagram

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

def send_sms(message):
    """
    Call SMS API sending message payload
    :param message: message to send to SMS API
    :return: None
    """
    client = TwilioRestClient(twilio_account, twilio_token)
    db_connect()
    cursor = r.table("sms_subscribers").run()
    for document in cursor:
        print type(document)
        print document
        print document['number']
        client.messages.create(
            to=document['number'],
            from_=twilio_phone_number,
            body=message,)
    print("%s: Sending SMS" % time.ctime())


def archive_email(server, emailid):
    """
    Move email to archive mailbox
    :param server: IMAP server object
    :param emailid: IMAP ID of msg to archive
    :return: None
    """
    print("%s:Archiving Email %s" % (time.ctime(), emailid))
    print server.copy(emailid,'INBOX.PROCESSED')
    print server.store(emailid, '+FLAGS', '\\DELETED')
    print server.expunge()


def parse_email(data):
    print data
    d = []
    l = False
    for line in data.split("\n"):
        if "Content-Type: text/plain; charset=UTF-8" in line:
            print "found it"
            l = True
            d.append(line)
        elif "Content-Type: text/html; charset=UTF-8" in line:
            break
        elif l:
            d.append(line)
    del d[0]
    del d[-1]
    d4 =[]
    for i in d:
        d4.append(i[:-2])
    s = ""
    for i in d4:
        s+=str(i)+'\n'
    return s


def get_email():
    """
    Make IMAP Connection and check for new messages
    :return:
    """
    server = imaplib.IMAP4_SSL(imap_host, port=imap_port)
    server.login(imap_user, imap_pass)

    print("%s: Checking for mail on %s" % (time.ctime(), imap_host))
    mbox = server.select("INBOX")

    mbox, data = server.search(None, "(To %s)" % receiving_email)
    if data ==['']:
        print "nothing to process!"
    else:
        if data == None:
            print 'none'
        data = data[0].split(' ')
        msgid = data[0]
        mbox, data = server.fetch(msgid, '(RFC822)')
        mail = email.message_from_string(data[0][1])

        for part in mail.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get_content_subtype() != 'plain':
                continue
        payload = part.get_payload()
        payload = strip_tags(payload)
        header = HeaderParser().parsestr(data[0][1])
        subject = header['Subject']
        print "Received Message. Subject: '%s' . Contents: '%s'" % (subject, payload)
        archive_email(server, msgid)
        send_sms("[Ignitechat]: %s - %s" % (subject, payload))
        server.LOGOUT()


def sms_window():
    """
    Check if its within the allowed time range to send SMS messages. Return True if it is, otherwise False.
    :return: Boolean
    """
    if datetime.time(int(sms_window_start)) < datetime.datetime.now().time() < datetime.time(int(sms_window_end)):
        return True
    else:
        return False


if __name__ == "__main__":
    c0 = 0
    run = True
    while run is True:
        if sms_window():
            get_email()
        else:
            if c0 == 0:
                print "Currently not processing"
            c0 += 1
        time.sleep(300)