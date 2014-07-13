from twilio.rest import TwilioRestClient
import imaplib
import email
import ConfigParser
from pprint import pprint

parser = SafeConfigParser()
parser.read('/Users/wjimenez/Desktop/igchat.ini')

twilio_account = parser.get('twilio', 'account')
twilio_token = parser.get('twilio', 'token')
imap_host = parser.get('imap', 'host')
imap_user = parser.get('imap', 'user')
imap_pass = parser.get('imap', 'pass')
imap_port = parser.get('imap', 'port')


def SendSMS(message):
    try:
        client = TwilioRestClient(account, token)
        message = client.messages.create(to="", from_="",
                                         body=message) % message
    except:
        raise Exception('Error Sending SMS')

def archiveEmail(server, emailid):
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

    #mboxes = server.list()[1]
    r = server.select("INBOX")

    r, data = server.search(None, "(To ignitechat@willjimenez.com)")
    if data ==['']:
        exit(0)

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
    print payload
    archiveEmail(server, msgid)
    server.LOGOUT()

    #pprint((data))
    #pprint(type(data))
    #print data[0][1]

getEmail()


