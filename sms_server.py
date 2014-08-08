from flask import Flask, request, redirect
import twilio.twiml
import chat
 
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def receive_sms():

    from_number = request.values.get('From', None)
    message_body = request.values.get('Body', None)
    message_sid = request.values.get('MessageSid', None)

    if "subscribe" in message_body.lower():  # if not check to see if subscribe is in body
        if not chat.db_get_phonenumber(from_number): # check if number is already in db
            message = "This number is currently subscribed to ignite chat"
        else:
            chat.db_set_phonenumber(from_number, message_sid)  # if subscribe is in body add to db
    else:  # if not reply with help message
        pass
        message = "To subscribe, reply with 'subscribe'"

    resp = twilio.twiml.Response()
    resp.message(message)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)