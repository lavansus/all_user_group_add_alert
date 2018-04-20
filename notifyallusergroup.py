from __future__ import print_function
import httplib2
import os
import base64
from email.mime.text import MIMEText
import mimetypes

from apiclient import discovery
from apiclient.discovery import build
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
SCOPES = 'https://www.googleapis.com/auth/admin.directory.group.readonly https://www.googleapis.com/auth/admin.directory.group https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.compose https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'All User Group Added Alert'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
	"""
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.dirname(os.path.realpath(__file__))
    
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'admin-directory_v1-python-gmail.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
    
def SendMessage(service, user_id, message):

    message = (service.users().messages().send(userId=user_id, body=message)
            .execute())
    """
    print('Message Id: %s' % message['id'])
    return message
    """

def CreateMessage(sender, to, subject, message_text):

    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    return {'raw': raw}

def main():

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('admin', 'directory_v1', http=http)
    servicegmail = build('gmail', 'v1', http=http)
	
    results = service.groups().list(userKey='C01hvmh3f').execute()
    groups = results.get('groups',[])
    if groups:
        grouplist = 'The following groups contain all users in the organization: '
        for group in groups:
            grouplist = grouplist + '{0}'.format(group['email']) + '\n'
    
        message = CreateMessage('anthony.wollenburg2@isd728.org', 'notify@isd728.org', 'All users within Independent School District 728', grouplist)
        SendMessage(servicegmail, 'me', message)

if __name__ == '__main__':
    main()