import os
import base64
import json
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
    # if os.path.exists(file_path) is not True: TODO create file
    with open(file_path,'r+') as f:
        data = f.read()
        added_message_ids = data.split(",")
        f.seek(0)
        f.write(",".join(list(set(message_ids+added_message_ids))))
        f.truncate()
    return [msgId for msgId in message_ids if msgId not in added_message_ids]

def fetch_mails(pageToken=None):
    try:
        mail_contents = []
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

        creds = generate_access_token(SCOPES,"credentials.json")

        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        if pageToken is None:
            messages = service.users().messages().list(userId='me', maxResults=100).execute()
        else:
            messages = service.users().messages().list(userId='me', maxResults=100,pageToken=pageToken).execute()

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
                mail_contents.append(text)
        
        pageToken = messages.get('nextPageToken')

        return mail_contents,pageToken

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    fetch_mails()
