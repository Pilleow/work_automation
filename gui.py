import tkinter as tk
import webbrowser
import tkinter.messagebox
from tkinter import ttk, IntVar

from modules.analyzesectioncompletion.analyzesectioncompletion import AnalyzeSectionCompletion
from modules.createcoursefolder.createcoursefiles import CreateCourseFiles
from modules.formstodocs.formstodocs import FormsToDocsScript


class App(tk.Tk):
    def __init__(self):
        main_color = "#3f8a95"
        super().__init__()
        self.title("NGV Automation")
        self.iconbitmap("@icon.xbm")
        style = ttk.Style()
        style.theme_create("ngv", parent="alt", settings={
            "TNotebook": {
                "configure": {"padding": [10, 10], "background": main_color}
            }})
        style.theme_use("ngv")
        tab_control = ttk.Notebook(self, )

        # set constants
        self.configure(background=main_color)
        scopes = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/drive",
                  "https://www.googleapis.com/auth/forms.body.readonly"]
        token_path = "./credentials/token.json"
        client_secrets_path = "./credentials/client_secrets.json"
        teachable_key_path = "./credentials/teachable_key.json"
        padx = 10
        pady = 10

        # initialize scripts
        class Scripts:
            ftd = FormsToDocsScript(scopes, token_path, client_secrets_path)
            ccf = CreateCourseFiles(scopes, token_path, client_secrets_path)
            asc = AnalyzeSectionCompletion(teachable_key_path)

        # building the FTD gui
        use_numeration = IntVar()
        ftd_frame = ttk.Frame(tab_control)
        form_id_label = ttk.Label(ftd_frame, text="Form ID")
        form_id_entry = ttk.Entry(ftd_frame, width=44)
        docs_id_label = ttk.Label(ftd_frame, text="Document ID")
        docs_id_entry = ttk.Entry(ftd_frame, width=44)
        numeration_start_entry = ttk.Entry(ftd_frame, width=2)
        numeration_start_label = ttk.Label(ftd_frame, text="Start Numeration At")
        use_numeration_check = tk.Checkbutton(ftd_frame, text='Use Numeration', variable=use_numeration, onvalue=1,
                                              offvalue=0)

        def ftd_run():
            num_start = numeration_start_entry.get().strip()
            if num_start.isdigit():
                num_start = int(num_start)
            else:
                num_start = 0

            forms_id = form_id_entry.get().strip().split("/")
            if len(forms_id) > 1:
                forms_id = forms_id[-2]
            else:
                forms_id = forms_id[0]
            docs_id = docs_id_entry.get().strip().split("/")
            if len(docs_id) > 1:
                docs_id = docs_id[-2]
            else:
                docs_id = docs_id[0]

            try:
                Scripts.ftd.run(forms_id, docs_id, bool(use_numeration.get()), num_start)
            except Exception as e:
                tk.messagebox.showinfo("Error", str(e), icon=tkinter.messagebox.ERROR)
                raise e

        ftd_button = tk.Button(ftd_frame, text="Convert", command=ftd_run, bg=main_color, fg="white")

        # building the CCF gui
        ccf_frame = ttk.Frame(tab_control)
        folder_id_entry = ttk.Entry(ccf_frame, width=44)
        folder_id_label = ttk.Label(ccf_frame, text="Parent Folder ID")
        num_of_modules_label = ttk.Label(ccf_frame, text="Module Count")
        num_of_modules_entry = ttk.Entry(ccf_frame, width=14, justify="center")
        num_of_modules_entry.insert(0, "1")

        def ccf_run():
            folder_id = folder_id_entry.get().strip().split("/")
            if len(folder_id) > 1:
                folder_id = folder_id[-1]
            else:
                folder_id = folder_id[0]
            try:
                file_ids = Scripts.ccf.run(folder_id, int(num_of_modules_entry.get().strip()))
                if tk.messagebox.showinfo("Warning",
                                          "The Google Forms API does not allow changing forms settings.\n\nMake sure you set the settings of each Google Form manually. Open each Form in a new tab?",
                                          icon=tkinter.messagebox.WARNING,
                                          type=tkinter.messagebox.YESNO) == tkinter.messagebox.YES:
                    for k in file_ids:
                        if k == "zad_ans":
                            continue
                        for fid in file_ids[k]:
                            webbrowser.open(f"https://docs.google.com/forms/d/{fid}/edit")
                        if k != "egz" and tk.messagebox.showinfo("Warning",
                                                                 "Open the next batch of Forms?",
                                                                 icon=tkinter.messagebox.WARNING,
                                                                 type=tkinter.messagebox.YESNO) == tkinter.messagebox.NO:
                            break

            except Exception as e:
                tk.messagebox.showinfo("Error", str(e), icon=tkinter.messagebox.ERROR)
                raise e

        ccf_button = tk.Button(ccf_frame, text="Generate", command=ccf_run, bg=main_color, fg="white")

        # buidling the ASC gui
        asc_frame = ttk.Frame(tab_control)
        course_id_entry = ttk.Entry(asc_frame, width=8)
        course_id_label = ttk.Label(asc_frame, text="Course ID")
        section_name_entry = ttk.Entry(asc_frame, width=20)
        section_name_label = ttk.Label(asc_frame, text="Section Name")

        def asc_run():
            course_id = course_id_entry.get().strip().split("/")
            if len(course_id) > 1:
                course_id = course_id[-2]
            else:
                course_id = course_id[0]
            if not course_id.isnumeric():
                tk.messagebox.showinfo("Error", "Course ID must be a numeric value.\nIt is usually found in the URL.", icon=tkinter.messagebox.ERROR)
                return
            section_name = section_name_entry.get().strip()
            try:
                Scripts.asc.run(int(course_id), section_name)
            except Exception as e:
                tk.messagebox.showinfo("Error", str(e), icon=tkinter.messagebox.ERROR)
                raise e

        asc_button = tk.Button(asc_frame, text="Run Test (in terminal)", command=asc_run, bg=main_color, fg="white")

        # drawing the FTD gui
        use_numeration_check.grid(row=2, column=0, padx=padx, pady=0)
        numeration_start_entry.grid(row=2, column=1, padx=padx, pady=0)
        numeration_start_label.grid(row=2, column=2, padx=padx, pady=0)
        form_id_label.grid(row=1, column=0, padx=padx, pady=0)
        docs_id_label.grid(row=1, column=1, padx=padx, pady=0)
        form_id_entry.grid(row=0, column=0, padx=padx, pady=0)
        docs_id_entry.grid(row=0, column=1, padx=padx, pady=0)
        ftd_button.grid(row=0, column=2, padx=padx, pady=0)
        ftd_frame.grid(row=0, column=0, padx=2 * padx, pady=2 * pady)

        # drawing the CCF gui
        folder_id_label.grid(row=1, column=0, padx=padx, pady=0)
        num_of_modules_label.grid(row=1, column=1, padx=padx, pady=0)
        folder_id_entry.grid(row=0, column=0, padx=padx, pady=0)
        num_of_modules_entry.grid(row=0, column=1, padx=padx, pady=0)
        ccf_button.grid(row=0, column=2, padx=padx, pady=0)
        ccf_frame.grid(row=0, column=1, padx=2 * padx, pady=2 * pady)

        # drawing the ASC gui
        course_id_label.grid(row=1, column=0, padx=padx, pady=0)
        section_name_label.grid(row=1, column=1, padx=padx, pady=0)
        course_id_entry.grid(row=0, column=0, padx=padx, pady=0)
        section_name_entry.grid(row=0, column=1, padx=padx, pady=0)
        asc_button.grid(row=0, column=2, padx=padx, pady=0)
        asc_frame.grid(row=0, column=1, padx=2 * padx, pady=2 * pady)

        # drawing the main gui
        tab_control.add(ccf_frame, text="CreateCourseFolders")
        tab_control.add(ftd_frame, text="FormsToDocs")
        tab_control.add(asc_frame, text="AnalyzeSectionCompletion")
        tab_control.pack(expand=1, fill="both", padx=2 * padx, pady=(0.5 * pady, 2 * pady))


if __name__ == "__main__":
    App().mainloop()
