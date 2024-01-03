class GoogleAuthorizer:
    def __init__(self, scopes) -> None:
        self.SCOPES = scopes
        self.creds = None
        self.service = None
        self.DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"
