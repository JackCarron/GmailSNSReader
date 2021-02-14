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
    # payload = payload[:-2] + '"}'
    #
    #regex = re.compile(r'--(?s)(.*)support')
    # aws_payload = regex.sub(r'',json.loads(fixed)['content'])
    # print(type(aws_payload))
    # aws_payload = jsonify(aws_payload.split(';\\\\'))
    #print(type(payload[0]))
    curr_message = payload[1]
    quotable_printable = json.loads(json.loads(curr_message)['Message'])['content']. \
      split('Content-Transfer-Encoding: quoted-printable')
    text_plain = json.loads(json.loads(curr_message)['Message'])['content']. \
      split('Content-Type: text/plain')
    if len(quotable_printable) > 1:
        print(payload)
        decoded_string = quopri.decodestring(payload)
        print(decoded_string.decode('utf-8'))
        return decoded_string
    elif len(text_plain) > 1:
        return text_plain[1]
    return jsonify(quotable_printable)
    #file = open('output/html_index_7.html','r')
    #removed_html_tags = file.read().replace('<html>','').replace('</html>','')
    #print(removed_html_tags)
    #sreturn get_most_recent_aws_sns_email()


#@app.route('/email?')

if __name__=="__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 4444)))
