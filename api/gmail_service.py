from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import base64
import webbrowser
import sys
from flask import jsonify
import re
from urllib.parse import unquote
import codecs


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
BASE_URL = 'file:///Library/Frameworks/Python.framework/Versions/3.8/bin/scripts/GmailReader/'
NUM_OF_MESSAGES = 25


def main():
    service = getCreds()
    results = service.users().messages().list(userId='me',labelIds="INBOX").execute()
    messages = results.get('messages', [])
    message_parser(messages, NUM_OF_MESSAGES, service)


def get_inbox(service):
    results = service.users().messages().list(userId='me',labelIds="INBOX").execute()
    return results.get('messages', [])


def message_parser(messages, num_of_messages, service):
    try:
        list_of_emails = []
        print(len(messages))
        for i in range(num_of_messages):
            curr_message_info = service.users().messages() \
                .get(userId='me',id=messages[i]['id']).execute()
            headers = curr_message_info['payload']['headers']
            headers_dict = {}
            for j in range(len(headers)):
                headers_dict[headers[j]['name']]= headers[j]['value']

            if '<no-reply@sns.amazonaws.com>' in headers_dict['From']:
                decoded_bytes = decode_string(curr_message_info['payload']['body']['data'])
                utf8_str = str(decoded_bytes, 'UTF-8')
                #if  json.loads(utf8_str)['Type'] != None # and \
                #json.loads(utf8_str)['Type'] == 'Notification':
                list_of_emails.append(utf8_str)
                print('HERE!123456')
        return list_of_emails
    except:
        e = sys.exc_info()
        return str(e)



def multipart_alt_parser(message):
        message_info = message
        message = message['body']['data']
        return decode_string(message)



def decode_string(message):
    decoded_message = base64.urlsafe_b64decode(message + '==')
    return decoded_message#.read().decode('utf-8')

    #return str(decoded_message).replace('\\r','').replace('\\t','').replace('\\n','')


def write_file_utility(file_name,file_content):
    file = open(file_name,'w')
    file.write(file_content)
    file.close()


# For getting aws mails
def get_most_recent_aws_sns_email():
    try:
        service = getCreds()
        messages = get_inbox(service)
        return message_parser(messages, NUM_OF_MESSAGES, service)
    except:
        e = sys.exc_info()[0]
        return str(e)


def getCreds():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


if __name__ == '__main__':
    main()


        # decoded_html = decode_string(curr_message_info['payload']['body']['data'])
        #return decoded_html.replace('b\'','') + '}'
            #file_name = '../output/html_index_' + str(i) + '.html'

    # return headers_dict


        #if headers[j]['name'] == 'From' and '<no-reply@sns.amazonaws.com>' in headers[j]['value']:
            #json_body = decode_string(curr_message_info['payload']['body']['data'])
            #print(json_body['notificationType'])
            #return headers_dict
            #return json_body

        #     file_name = ''
        #     if headers[j]['name'] == 'Content-Type':
        #         print(headers[j]['value'])
        #         if 'multipart/alternative' in headers[j]['value']:
        #             multipart_text = multipart_alt_parser(curr_message_info['payload']['parts'][0])
        #             file_name = '../output/multipart_text_index_' + str(i) + '.txt'
        #             return multipart_text
        #             #write_file_utility(file_name, multipart_text)
        #
                # el
        #  write_file_utility(file_name, decoded_html)
        #
        #         elif 'text/plain' in headers[j]['value']:
        #             return curr_message_info
        #         else:
        #             return 'Error: Please try again.'
        #         continue
        #
        #print('-------------' + str(i) + '----------------')
