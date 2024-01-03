from google.gdrive import GDrive
from modules.script import Script


class CreateCourseFiles(Script):
    def __init__(self, scopes, token_path, client_secrets_path):
        super().__init__(scopes, token_path, client_secrets_path)
        self.gd = GDrive(self.SCOPES)
        self.gd.authorize(self.token_path, self.client_secrets_path)
    
    def run(self, parent_folder_id: str, number_of_modules: int):
        assert (number_of_modules > 0)
        assert (len(parent_folder_id) > 0)

        self.gd.create_course_files(parent_folder_id, number_of_modules)
