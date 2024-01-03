import tkinter as tk
import webbrowser
import tkinter.messagebox
from tkinter import ttk

from modules.formstodocs.formstodocs import FormsToDocsScript
from modules.createcoursefolder.createcoursefiles import CreateCourseFiles

class App(tk.Tk):
    def __init__(self):
        main_color = "#3f8a95"
        super().__init__()
        self.title("NGV Automation")
        self.iconbitmap("icon.ico")
        style = ttk.Style()
        style.theme_create("ngv", parent="alt", settings={
            "TNotebook": {
                "configure": {"padding": [10, 10], "background": main_color}
            }})
        style.theme_use("ngv")
        tab_control = ttk.Notebook(self, )

        # set constants
        self.configure(background=main_color)
        scopes = ["https://www.googleapis.com/auth/userinfo.email","https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/forms.body.readonly"]
        token_path = "./credentials/token.json"
        client_secrets_path = "./credentials/client_secrets.json"
        padx = 10
        pady = 10

        # initialize scripts
        class Scripts:
            ftd = FormsToDocsScript(scopes, token_path, client_secrets_path)
            ccf = CreateCourseFiles(scopes, token_path, client_secrets_path)

        # building the FTD gui
        ftd_frame = ttk.Frame(tab_control)
        form_id_label = ttk.Label(ftd_frame, text="Form ID")
        form_id_entry = ttk.Entry(ftd_frame, width=44)
        docs_id_label = ttk.Label(ftd_frame, text="Document ID")
        docs_id_entry = ttk.Entry(ftd_frame, width=44)

        def ftd_run():
            try:
                Scripts.ftd.run(form_id_entry.get().strip(), docs_id_entry.get().strip())
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
            try:
                file_ids = Scripts.ccf.run(folder_id_entry.get().strip(), int(num_of_modules_entry.get().strip()))
                if tk.messagebox.showinfo("Warning", "The Google Forms API does not allow changing forms settings.\n\nMake sure you set the settings of each Google Form manually. Open each Form in a new tab?", icon=tkinter.messagebox.WARNING, type=tkinter.messagebox.YESNO) == tkinter.messagebox.YES:
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


        # drawing the FTD gui
        form_id_label.grid(row=1, column=0, padx=padx, pady=0)
        docs_id_label.grid(row=1, column=1, padx=padx, pady=0)
        form_id_entry.grid(row=0, column=0, padx=padx, pady=0)
        docs_id_entry.grid(row=0, column=1, padx=padx, pady=0)
        ftd_button.grid(row=0, column=2, padx=padx, pady=0)
        ftd_frame.grid(row=0, column=0, padx=2*padx, pady=2*pady)

        # drawing the CCF gui
        folder_id_label.grid(row=1, column=0, padx=padx, pady=0)
        num_of_modules_label.grid(row=1, column=1, padx=padx, pady=0)
        folder_id_entry.grid(row=0, column=0, padx=padx, pady=0)
        num_of_modules_entry.grid(row=0, column=1, padx=padx, pady=0)
        ccf_button.grid(row=0, column=2, padx=padx, pady=0)
        ccf_frame.grid(row=0, column=1, padx=2*padx, pady=2*pady)

        # drawing the main gui
        tab_control.add(ccf_frame, text="CreateCourseFolders")
        tab_control.add(ftd_frame, text="FormsToDocs")
        tab_control.pack(expand=1, fill="both", padx=2*padx, pady=(0.5*pady, 2*pady))


if __name__ == "__main__":
    App().mainloop()
