from twilio.rest import TwilioRestClient
import imaplib
import email
from ConfigParser import SafeConfigParser
from pprint import pprint
import time
from HTMLParser import HTMLParser
import rethinkdb as r

parser = SafeConfigParser()
parser.read('/Users/wjimenez/Desktop/igchat.ini')

receiving_email = parser.get('main', 'receiving_email')
twilio_account = parser.get('twilio', 'account')
twilio_token = parser.get('twilio', 'token')
twilio_phone_number =  parser.get('twilio', 'phone_number')
imap_host = parser.get('imap', 'host')
imap_user = parser.get('imap', 'user')
imap_pass = parser.get('imap', 'pass')
imap_port = parser.get('imap', 'port')

def db_connect():
    r.connect( "localhost", 28015, db='ignitechat').repl()

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
        SendSMS(payload)


if __name__ == "__main__":
    run = True
    while run is True:
        getEmail()
        time.sleep(300)