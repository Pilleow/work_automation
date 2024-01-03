import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from google.google_authorizer import GoogleAuthorizer


class GDrive(GoogleAuthorizer):
    def create_course_files(self, parent_folder_id: str, number_of_modules: int) -> dict:
        fld_zad_dom_id = self.create_folder("Zadania Domowe", parent_folder_id)
        fld_zad_ans_id = self.create_folder("Odpowiedzi", fld_zad_dom_id)
        fld_zad_pyt_id = self.create_folder("Zadaj Pytanie", parent_folder_id)
        fld_egz_id = self.create_folder("Egzaminy", parent_folder_id)

        print("Created folders.")

        file_ids = {
            "zad_dom": [],
            "zad_ans": [],
            "zad_pyt": [],
            "egz": []
        }
        for i in range(1, number_of_modules + 1):
            fid = self.create_file(f"Zadanie Domowe - Moduł {i}", fld_zad_dom_id, "application/vnd.google-apps.form")
            file_ids["zad_dom"].append(fid)
            fid = self.create_file(f"Zadanie Domowe (odp) - Moduł {i}", fld_zad_ans_id, "application/vnd.google-apps.document")
            file_ids["zad_ans"].append(fid)
            fid = self.create_file(f"Zadaj Pytanie - Moduł {i}", fld_zad_pyt_id, "application/vnd.google-apps.form")
            file_ids["zad_pyt"].append(fid)
        for i in [1, 2]:
            fid = self.create_file(f"Egzamin - Termin {'I' * i}", fld_egz_id, "application/vnd.google-apps.form")
            file_ids["egz"].append(fid)

        print("Created empty files.")

        return file_ids

    def create_file(self, name: str, parent_folder_id: str, mimeType: str) -> str:
        file_metadata = {
            "name": name,
            "parents": [parent_folder_id],
            "mimeType": mimeType,
        }
        file = self.service.files().create(body=file_metadata, fields="id").execute()
        return file.get("id")

    def create_folder(self, name: str, parent_folder_id: str) -> str:
        return self.create_file(name, parent_folder_id, "application/vnd.google-apps.folder")

    def authorize(self, token_path: str, client_secrets_path: str):
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, "w") as token:
                token.write(self.creds.to_json())
        self.service = build("drive", "v3", credentials=self.creds)

