from __future__ import print_function
import base64
import os.path

from email.message import MIMEPart
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

"""Shows basic usage of the Gmail API.
Lists the user's Gmail labels.
"""
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
        flow = InstalledAppFlow.from_client_secrets_file('/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


def get_label_id(number):
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()

        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        for label in labels:
            if label['name'][0] == str(number):
                return label['id']

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def send_mail(address, subject, body, tag_number):
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = MIMEPart()
        message.set_content(body, 'html')
        message['To'] = address
        message['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send(userId="me", body=create_message).execute())

        label_body = {
            'addLabelIds': [get_label_id(tag_number)]
        }

        service.users().messages().modify(userId='me', id=send_message["id"], body=label_body).execute()
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None