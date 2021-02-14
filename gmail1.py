from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import base64

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
NUM_OF_MESSAGES = 20


def main():

    service = getCreds()
    print('service: ' + str(service))

    # Call the Gmail API
    results = service.users().messages().list(userId='me',labelIds="INBOX").execute()
    messages = results.get('messages', [])
    message_parser(messages, NUM_OF_MESSAGES, service)


def message_parser(messages, num_of_messages, service):
    for i in range(num_of_messages):
        is_text_flag = False
        # curr_message_info is main object
        curr_message_info = service.users().messages() \
        .get(userId='me',id=messages[i]['id']).execute()
        headers = curr_message_info['payload']['headers']
        for j in range(len(headers)):
            print('index #: ' + str(j))
            if headers[j]['name'] != None and headers[j]['name'] == 'Content-Type':
                print(json.dumps(headers[j],indent=2))
                if 'multipart/alternative' in headers[j]['value']:
                    is_text_flag = True
        if is_text_flag:
            multipart_alt_parser(curr_message_info)
        print('-------------------------------')
        print('-------------' + str(i) + '----------------')
        print('-------------------------------')
        

def multipart_alt_parser(message):
        message_info = message['payload']['parts'][0]
        message = message_info['body']['data']
        decoded_message = base64.urlsafe_b64decode(message)
        decoded_message_list = str(decoded_message).split('\\r\\n')
        for m in decoded_message_list:
            print(m)



def getCreds():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
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
