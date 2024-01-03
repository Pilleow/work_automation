class Script:
    def __init__(self, scopes, token_path, client_secrets_path):
        self.token_path = token_path
        self.client_secrets_path = client_secrets_path
        self.SCOPES = scopes
        self.ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                         'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
