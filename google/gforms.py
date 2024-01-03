import os.path
from oauth2client import client, file, tools
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from google.google_authorizer import GoogleAuthorizer


class GForms(GoogleAuthorizer):
    def get_form_data(self, form_id: str) -> dict:
        return self.service.forms().get(formId=form_id).execute()

    def insert_into_form(self, form_id, requests):
        self.service.forms().batchUpdate(formId=form_id, body=requests).execute()

    def authorize(self, token_path: str, client_secrets_path: str):
        store = file.Storage(token_path)
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        if not self.creds or not self.creds.valid:
            flow = client.flow_from_clientsecrets(client_secrets_path, self.SCOPES)
            self.creds = tools.run_flow(flow, store)
        self.service = build("forms", "v1", credentials=self.creds)