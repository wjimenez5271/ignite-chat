from flask import Flask, request, redirect
import argparse
import twilio.twiml
import db
import logging

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def receive_sms():

    from_number = request.values.get('From', None)
    message_body = request.values.get('Body', None)
    message_sid = request.values.get('MessageSid', None)

    if "unsubscribe" in message_body.lower():
        try:
            db.db_remove_phonenumber(int(from_number))
            message = "Your phone number has been removed"
            logging.info('Phone number {} removed from db'.format(from_number))
        except Exception as e:
            logging.error('Exception removing phone number {} from db: {}'.format(from_number, e))
    elif "subscribe" in message_body.lower():  # if not check to see if subscribe is in body
        try:
            if db.db_get_phonenumber(int(from_number)):  # check if number is already in db
                message = "This number is currently subscribed to ignite chat"
                logging.info('Phone number {} already in DB'.format(from_number))
        except Exception as e:
            logging.error('Exception looking up phone number {} in db: {}'.format(from_number, e))
        else:
            try:
                db.db_set_phonenumber(int(from_number), message_sid)  # if subscribe is in body add to db
                message = "You've been subscribed to Ignite Chat"
                logging.info('Phone number {} added to DB'.format(from_number))
            except Exception as e:
                logging.error('Exception inserting phone number {} into db: {}'.format(from_number, e))
    else:  # if not reply with help message
        pass
        message = "To subscribe, reply with 'subscribe'. To unsubscribe, reply 'unsubscribe'"

    resp = twilio.twiml.Response()
    resp.message(message)

    return str(resp)


def setup_logging(loglevel, logfile):
    #Setup Logger
    numeric_log_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_log_level, int):
         raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(filename=logfile, level=numeric_log_level,
                        format="%(asctime)s - [ignite-chat] - "
                          "%(levelname)s - %(message)s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel', help='logging level', type=str, default='INFO')
    parser.add_argument('--logfile', help='path to write logfile to', type=str, default='sms-server.log')
    args = parser.parse_args()

    setup_logging(args.loglevel, args.logfile)
    logging.info('Starting server')
    if args.loglevel.upper() == 'DEBUG':
        floglevel=True
    else:
        floglevel=False

    app.run(debug=floglevel, host='0.0.0.0')
