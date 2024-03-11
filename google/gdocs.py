import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

from google.google_authorizer import GoogleAuthorizer


class GDocs(GoogleAuthorizer):
    def insert_into_document(self, document_id, requests):
        self.service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()

    def authorize(self, token_path: str, client_secrets_path: str):
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_path, self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            with open(token_path, "w") as token:
                token.write(self.creds.to_json())

        try:
            self.service = build("docs", "v1", credentials=self.creds)
        except HttpError as err:
            print(err)
