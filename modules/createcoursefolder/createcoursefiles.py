import json

from google.gdrive import GDrive
from google.gforms import GForms
from modules.script import Script


class CreateCourseFiles(Script):
    def __init__(self, scopes, token_path, client_secrets_path):
        super().__init__(scopes, token_path, client_secrets_path)
        self.gd = GDrive(self.SCOPES)
        self.gf = GForms(self.SCOPES)
        self.gd.authorize(self.token_path, self.client_secrets_path)
        self.gf.authorize(self.token_path, self.client_secrets_path)
    
    def run(self, parent_folder_id: str, number_of_modules: int) -> dir:
        assert (number_of_modules > 0)
        assert (len(parent_folder_id) > 0)

        print("Started.")

        file_ids = self.gd.create_course_files(parent_folder_id, number_of_modules)

        for i, fid in enumerate(file_ids["zad_dom"]):
            print("Processing (zad_dom): " + fid)
            with open("./modules/createcoursefolder/zad_dom_update.json", "r", encoding="utf-8") as f:
                update = json.load(f)
            update["requests"][1]["updateFormInfo"]["info"]["title"] += str(i + 1)
            self.gf.insert_into_form(fid, update)

        for i, fid in enumerate(file_ids["zad_pyt"]):
            print("Processing (zad_pyt): " + fid)
            with open("./modules/createcoursefolder/zad_pyt_update.json", "r", encoding="utf-8") as f:
                update = json.load(f)
            update["requests"][1]["updateFormInfo"]["info"]["title"] += str(i + 1)
            self.gf.insert_into_form(fid, update)

        for i, fid in enumerate(file_ids["egz"]):
            print("Processing (egz): " + fid)
            with open(f"./modules/createcoursefolder/egz_{1 + i}_update.json", "r", encoding="utf-8") as f:
                update = json.load(f)
            self.gf.insert_into_form(fid, update)

        print("Done.")
        return file_ids
