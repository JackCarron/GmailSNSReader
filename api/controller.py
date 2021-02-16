import os
import flask
from gmail_service import get_most_recent_aws_sns_email
from gmail_service import get_messages_with_search
import json
from flask import jsonify
from flask import request
import re
import quopri
from flask_cors import CORS



app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

@app.route('/api/v1/emails/search', methods=['GET'])
def email_search_v1():
    from_address = request.args.get('fromAddress')
    num = int(request.args.get('numOfEmails')) if request.args.get('numOfEmails') != None  else None
    if from_address == None and num == None:
        return 'Please add a from address such as api/emails/search?fromAddress=<no-reply@sns.amazonaws.com>&numOfEmails=10'
    #payload = get_most_recent_aws_sns_email(num, from_address)
    payload = get_messages_with_search('from:<no-reply@sns.amazonaws.com>')
    return_list = []
    for i in range(len(payload) - 1):
        curr_message = payload[i]
        flag = True
        try:
            json.loads(json.loads(curr_message)['Message'])['content']
        except:
            flag = False
        if flag:
            curr_message_content = json.loads(json.loads(curr_message)['Message'])['content']
            quotable_printable = curr_message_content.split('Content-Transfer-Encoding: quoted-printable')
            text_plain = curr_message_content.split('Content-Type: text/plain')
            if len(quotable_printable) > 1:
                encoded_string = quotable_printable[len(quotable_printable)-1]
                return_list.append({'quotable_printable' : encoded_string})
            elif len(text_plain) > 1:
                return_list.append({'text_plain' : text_plain[1]})
    return jsonify(return_list)
    # else:
    #     return 'Skip this -->'


app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True
@app.route('/api/v2/emails/search', methods=['GET'])
def email_search_v2():
    from_address = request.args.get('fromAddress')
    num = int(request.args.get('numOfEmails')) if request.args.get('numOfEmails') != None  else 5
    print(num)
    page_token = request.args.get('pageToken')
    return jsonify(get_messages_with_search(from_address,num,page_token))
    #return get_messages_with_search('from:<no-reply@sns.amazonaws.com>')


if __name__=="__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 4444)))
