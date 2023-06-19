import os
import base64
import json
import re
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def generate_access_token(SCOPES,credential_file="credentials.json"):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credential_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def check_and_deduplicate_read_mails(message_ids):
    file_path = 'messageIds.txt'
    with open(file_path,'r') as f:
        data = f.read()
        added_message_ids = data.split(",")
        # f.seek(0)
        # f.write(",".join(list(set(message_ids+added_message_ids))))
        # f.truncate()
    return [msgId for msgId in message_ids if msgId not in added_message_ids]

def write_message_ids(message_ids):
    file_path = 'messageIds.txt'
    with open(file_path,'a') as f:
        f.write(",".join(message_ids))
        f.close()

def fetch_mails(pageToken=None):
    try:
        mail_contents = []
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

        creds = generate_access_token(SCOPES,"credentials.json")

        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        if pageToken is None:
            messages = service.users().messages().list(userId='me', maxResults=500).execute()
        else:
            messages = service.users().messages().list(userId='me', maxResults=500,pageToken=pageToken).execute()

        message_ids = []
        for message in messages.get('messages',[]):
            message_ids.append(message['id'])
        
        message_ids = check_and_deduplicate_read_mails(message_ids)

        for message_id in message_ids:
            # Get the contents of the email
            message = service.users().messages().get(userId='me', id=message_id).execute()
            # print(json.dumps(message,indent=4))
            
            # Decode the email body
            msg_content = message.get('payload',{}).get('body',{}).get('data')
            msg_parts = message.get('payload',{}).get('parts',{})
            for msg_part in msg_parts:
                if msg_part.get('mimeType') == "text/plain":
                    msg_content = msg_part.get('body',{}).get('data')
            
            if msg_content is not None:
                body = base64.urlsafe_b64decode(msg_content)

                # Convert the email body to a string
                text = body.decode('utf-8')
                title = re.sub(r'[^A-Za-z0-9 ]+', '', message.get('snippet',''))
                if message.get('internalDate'):
                    date = datetime.datetime.fromtimestamp(int(message.get('internalDate')) / 1e3).strftime("%c")
                mail_contents.append({"title":title,"mail_body":text,"date":date})
                
        
        pageToken = messages.get('nextPageToken')

        return mail_contents,message_ids

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    fetch_mails()
