from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools

from google.google_authorizer import GoogleAuthorizer


class GForms(GoogleAuthorizer):
    def get_form_data(self, form_id: str) -> dict:
        return self.service.forms().get(formId=form_id).execute()

    def authorize(self, token_path: str, client_secrets_path: str):
        store = file.Storage(token_path)
        creds = None
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(client_secrets_path, self.SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = discovery.build(
            "forms",
            "v1",
            http=creds.authorize(Http()),
            discoveryServiceUrl=self.DISCOVERY_DOC,
            static_discovery=False,
        )