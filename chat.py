from twilio.rest import TwilioRestClient
import imaplib
import email
from ConfigParser import SafeConfigParser
import time
import db_json as db
from HTMLParser import HTMLParser
import datetime
import sys
from os import path

parser = SafeConfigParser()
parser.read(path.join(path.expanduser('~'), '.ignite_chat.ini'))

receiving_email = parser.get('main', 'receiving_email')
sms_window_start = parser.get('main', 'sms_window_start')
sms_window_end = parser.get('main', 'sms_window_end')
sms_header = parser.get('main', 'sms_header')
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
    s = MLStripper()
    s.feed(html)
    return s.get_data()

#TODO post to facebook
#TODO post to instagram


def SendSMS(message):
    # truncate message length to 1599 characters to comply with Twilio limits
    message = message[:1598]
    client = TwilioRestClient(twilio_account, twilio_token)
    for subscriber in db.db_list_all_subscribers():
        client.messages.create(
            to=subscriber['number'],
            from_=twilio_phone_number,
            body=message
        )
    print("%s: Sending SMS" % time.ctime())


def archiveEmail(server, emailid):
    print("%s:Archiving Email %s" % (time.ctime(), emailid))
    print server.copy(emailid,'INBOX.PROCESSED')
    print server.store(emailid, '+FLAGS', '\\DELETED')
    print server.expunge()


def parseEmail(data):
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


def getEmail():
    server = imaplib.IMAP4_SSL(imap_host, port=imap_port)
    server.login(imap_user, imap_pass)

    print("%s: Checking for mail on %s" % (time.ctime(), imap_host))
    #mboxes = server.list()[1]
    r = server.select("INBOX")

    r, data = server.search(None, "(To %s)" % receiving_email)
    if data ==['']:
        print "nothing to process!"
    else:
        if data == None:
            print 'none'
        data = data[0].split(' ')
        msgid = data[0]
        r, data = server.fetch(msgid, '(RFC822)')
        mail = email.message_from_string(data[0][1])

        for part in mail.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get_content_subtype() != 'plain':
                continue
        payload = part.get_payload()

        payload = strip_tags(payload)
        print "Received Message. Contents: "+payload
        archiveEmail(server, msgid)
        server.LOGOUT()
        # Add sms header to message payload
        payload = sms_header + ' ' + payload
        SendSMS(payload)


def SMS_window():
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
        if SMS_window():
            getEmail()
        else:
            if c0 == 0:
                print "Currently not processing"
            c0 += 1
        time.sleep(300)