import os
import flask
from gmail_service import get_most_recent_aws_sns_email
import json
from flask import jsonify


app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    payload = get_most_recent_aws_sns_email()
    return payload
    #file = open('output/html_index_7.html','r')
    #removed_html_tags = file.read().replace('<html>','').replace('</html>','')
    #print(removed_html_tags)
    #sreturn get_most_recent_aws_sns_email()


if __name__=="__main__":
    app.run(host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 4444)))
