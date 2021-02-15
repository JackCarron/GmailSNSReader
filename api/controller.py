import os
import flask
from gmail_service import get_most_recent_aws_sns_email
import json
from flask import jsonify
import re
import quopri


app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    payload = get_most_recent_aws_sns_email()
    print('length of aws emails -> ' + str(len(payload)))
    print('HERE!!!')
    return_list = []
    for i in range(len(payload) - 1):
        curr_message = payload[i]
        flag = True
        try:
            json.loads(json.loads(curr_message)['Message'])['content']
        except:
            flag = False
        if flag:
            print(i)
            curr_message_content = json.loads(json.loads(curr_message)['Message'])['content']
            quotable_printable = curr_message_content.split('Content-Transfer-Encoding: quoted-printable')
            text_plain = curr_message_content.split('Content-Type: text/plain')
            if len(quotable_printable) > 1:
                # decoded_string = quopri.decodestring(quotable_printable[len(quotable_printable)-1])
                # return_list.append({'quotable_printable' : str(decoded_string)})
                encoded_string = quotable_printable[len(quotable_printable)-1]
                return_list.append({'quotable_printable' : encoded_string})
            elif len(text_plain) > 1:
                return_list.append({'text_plain' : text_plain[1]})

    for a in return_list:
        print(a)
        print('--------------')
        print('--------------')
        print('--------------')
        print('--------------')

    return jsonify(return_list)
    # else:
    #     return 'Skip this -->'


#@app.route('/email?')

if __name__=="__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 4444)))
