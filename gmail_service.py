from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import base64
import webbrowser

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
BASE_URL = 'file:///Library/Frameworks/Python.framework/Versions/3.8/bin/scripts/GmailReader/'
NUM_OF_MESSAGES = 25


def main():
    service = getCreds()
    results = service.users().messages().list(userId='me',labelIds="INBOX").execute()
    messages = results.get('messages', [])
    message_parser(messages, NUM_OF_MESSAGES, service)


def message_parser(messages, num_of_messages, service):
    for i in range(num_of_messages):
        curr_message_info = service.users().messages() \
            .get(userId='me',id=messages[i]['id']).execute()
        headers = curr_message_info['payload']['headers']
        for j in range(len(headers)):
            file_name = ''
            
            if headers[j]['name'] != None and headers[j]['name'] == 'Content-Type':
                if 'multipart/alternative' in headers[j]['value']:
                    multipart_text = multipart_alt_parser(curr_message_info['payload']['parts'][0])
                    file_name = 'output/multipart_text_index_' + str(i) + '.txt'
                    write_file_utility(file_name, multipart_text)
                    
                elif 'text/html' in headers[j]['value']:
                    decoded_html = decode_string(curr_message_info['payload']['body']['data'])
                    file_name = 'output/html_index_' + str(i) + '.html'
                    write_file_utility(file_name, decoded_html)
                    
                webbrowser.open(BASE_URL + file_name,new=2)
                continue
        print('-------------' + str(i) + '----------------')
        

def multipart_alt_parser(message):
        message_info = message
        message = message['body']['data']
        return decode_string(message)



def decode_string(message):
    decoded_message = base64.urlsafe_b64decode(message)
    return str(decoded_message).replace('\\r','').replace('\\t','').replace('\\n','')
    

def write_file_utility(file_name,file_content):
    file= open(file_name,'w')
    file.write(file_content)
    file.close()


def getCreds():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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
