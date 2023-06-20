import os
import base64
import json
import re
import datetime
import math
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import CHAR_LIMIT,JOB_LABEL_ID,FILTER_MAIL
from logger import logger

def generate_access_token(SCOPES,credential_file="credentials.json",token_file="token.json"):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credential_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def check_and_deduplicate_read_mails(message_ids):
    file_path = 'messageIds.txt'
    with open(file_path,'r') as f:
        data = f.read()
        added_message_ids = data.split(",")
        f.close()
        # f.seek(0)
        # f.write(",".join(list(set(message_ids+added_message_ids))))
        # f.truncate()
    return [msgId for msgId in message_ids if msgId not in added_message_ids]

def write_message_ids(message_ids):
    file_path = 'messageIds.txt'
    with open(file_path,'a') as f:
        f.write(",".join(message_ids))
        f.close()

def fetch_mails(pageToken=None, nResults=100):
    
    try:
        mail_contents = []
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

        creds = generate_access_token(SCOPES,"credentials.json")

        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)

        pages = math.ceil(nResults/100)
        while pages>0:
            if pageToken is None:
                messages = service.users().messages().list(userId='me', maxResults=nResults).execute()
            else:
                messages = service.users().messages().list(userId='me', maxResults=nResults,pageToken=pageToken).execute()

            message_ids = []
            for message in messages.get('messages',[]):
                message_ids.append(message['id'])
            
            message_ids = check_and_deduplicate_read_mails(message_ids)

            for message_id in message_ids:
                # Get the contents of the email
                message = service.users().messages().get(userId='me', id=message_id).execute()
                
                # Decode the email body
                msg_content = message.get('payload',{}).get('body',{}).get('data')
                msg_parts = message.get('payload',{}).get('parts',{})

                # Filtering mails
                for header in message.get('payload',{}).get('headers',[]):
                    if header['name']=="From" and re.findall('\S+@\S+', header['value']) in FILTER_MAIL:
                        continue

                for msg_part in msg_parts:
                    if msg_part.get('mimeType') == "text/plain":
                        msg_content = msg_part.get('body',{}).get('data')
                
                if msg_content is not None:
                    body = base64.urlsafe_b64decode(msg_content)

                    # Convert the email body to a string
                    text = body.decode('utf-8')
                    if len(text)>CHAR_LIMIT:
                        continue
                    title = re.sub(r'[^A-Za-z0-9 ]+', '', message.get('snippet',''))
                    if message.get('internalDate'):
                        date = datetime.datetime.fromtimestamp(int(message.get('internalDate')) / 1e3).strftime("%c")
                    
                    mail_contents.append({"title":title,"mail_body":text,"date":date})
                    
            
            pageToken = messages.get('nextPageToken')
            logger.info(pageToken)
            pages-=1

        return mail_contents,message_ids

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        logger.critical(f'An error occurred: {error}')


def update_labels(label_id,message_ids):
    try:
        if len(message_ids)>0:
            SCOPES = [
                "https://mail.google.com/",
                "https://www.googleapis.com/auth/gmail.modify"
            ]
            creds = generate_access_token(SCOPES,"credentials.json","label_update_token.json")
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)
            body = {
                "ids":message_ids,
                "addLabelIds":[label_id]
            }
            service.users().messages().batchModify(userId='me',body=body).execute()
    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    update_labels(JOB_LABEL_ID,["188d7a15fb5dada0","188d792ad04cae1e","188d78906bdbbeb9","188d78905bbdb847","188d77a3b09bce2e","188d77460a795d8a"])
