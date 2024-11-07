import io
import os
import tkinter as tk
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from tkinter import filedialog, messagebox, Listbox
from google_auth_oauthlib.flow import InstalledAppFlow
from constants import SCOPES, SECRETS_PATH, TOKENS_PATH
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


class StracGoogleDriveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Strac Take Home Assessment - Google Drive File Manager")
        self.root.geometry("600x400")
        self.creds = None
        self.drive_service = None

        self.remember_var = tk.BooleanVar()
        self.file_id_map = {}  # Map to store file names with their corresponding IDs

        self.login_frame = tk.Frame(root)
        self.login_button = tk.Button(
            self.login_frame, text="Login to Google", command=self.authenticate
        )
        self.login_button.pack(side=tk.LEFT, padx=5)
        self.remember_checkbox = tk.Checkbutton(
            self.login_frame, text="Remember login", variable=self.remember_var
        )
        self.remember_checkbox.pack(side=tk.LEFT)
        self.login_frame.pack(pady=10)

        self.file_listbox = Listbox(root)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.file_listbox.pack_forget()  # Hide the listbox until user is logged in

        self.button_frame = tk.Frame(root)
        self.upload_button = tk.Button(
            self.button_frame,
            text="Upload File",
            command=self.upload_file,
            state=tk.DISABLED,
        )
        self.upload_button.grid(row=0, column=0, padx=5)

        self.download_button = tk.Button(
            self.button_frame,
            text="Download File",
            command=self.download_file,
            state=tk.DISABLED,
        )
        self.download_button.grid(row=0, column=1, padx=5)

        self.delete_button = tk.Button(
            self.button_frame,
            text="Delete File",
            command=self.delete_file,
            state=tk.DISABLED,
        )
        self.delete_button.grid(row=0, column=2, padx=5)

        self.logout_button = tk.Button(root, text="Logout", command=self.logout)
        self.logout_button.pack_forget()  # Hide the logout button initially

        self.check_existing_token()

    def check_existing_token(self):
        if os.path.exists(TOKENS_PATH):
            self.creds = Credentials.from_authorized_user_file(TOKENS_PATH, SCOPES)
            if self.creds and self.creds.valid:
                self.drive_service = build("drive", "v3", credentials=self.creds)
                self.on_successful_login()

    def authenticate(self):
        if not self.creds or not self.creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(SECRETS_PATH, SCOPES)
            self.creds = flow.run_local_server(port=0)

            if self.remember_var.get():
                with open(TOKENS_PATH, "w") as token:
                    token.write(self.creds.to_json())

        self.drive_service = build("drive", "v3", credentials=self.creds)
        self.on_successful_login()

    def on_successful_login(self):
        self.login_frame.pack_forget()
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.button_frame.pack(pady=5)
        self.logout_button.pack(pady=5)
        self.upload_button.config(state=tk.NORMAL)
        self.download_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)
        self.populate_file_list()

    def populate_file_list(self):
        self.file_listbox.delete(0, tk.END)
        self.file_id_map.clear()
        try:
            results = (
                self.drive_service.files()
                .list(pageSize=20, fields="files(id, name, mimeType, modifiedTime)")
                .execute()
            )
            items = results.get("files", [])
            if not items:
                self.file_listbox.insert(tk.END, "No files found.")
            else:
                for item in items:
                    name = item["name"]
                    file_type = item["mimeType"]
                    last_modified = item["modifiedTime"]
                    file_id = item["id"]

                    file_details = (
                        f"{name} | Type: {file_type} | Last Modified: {last_modified}"
                    )
                    self.file_listbox.insert(tk.END, file_details)
                    self.file_id_map[name] = file_id
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def upload_file(self, file_data=None, file_name=None):
        if not file_data:
            file_path = filedialog.askopenfilename()
            if not file_path:
                return
            file_name = os.path.basename(file_path)
            file_data = MediaFileUpload(file_path, resumable=True)
        else:
            file_data = MediaFileUpload(io.BytesIO(file_data), resumable=True)

        file_metadata = {"name": file_name}
        file = (
            self.drive_service.files()
            .create(body=file_metadata, media_body=file_data, fields="id")
            .execute()
        )
        messagebox.showinfo("Success", f"File uploaded with ID: {file.get('id')}")
        self.populate_file_list()

    def download_file(self, in_memory_file=None):
        selected_file = self.file_listbox.get(tk.ACTIVE)
        if selected_file:
            file_id = self.file_id_map.get(selected_file.split(" | ")[0].strip())
            file_name = selected_file.split(" | ")[0].strip()
            request = self.drive_service.files().get_media(fileId=file_id)

            if in_memory_file:
                downloader = MediaIoBaseDownload(in_memory_file, request)
            else:
                file_path = filedialog.asksaveasfilename(initialfile=file_name)
                if not file_path:
                    return
                fh = io.FileIO(file_path, "wb")
                downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")

            if not in_memory_file:
                messagebox.showinfo("Success", f"File downloaded as {file_path}")
            return in_memory_file if in_memory_file else file_path

    def delete_file(self):
        selected_file = self.file_listbox.get(tk.ACTIVE)
        if selected_file:
            file_id = self.file_id_map.get(selected_file.split(" | ")[0].strip())
            self.drive_service.files().delete(fileId=file_id).execute()
            messagebox.showinfo("Success", "File deleted successfully.")
            self.populate_file_list()

    def logout(self):
        if os.path.exists(TOKENS_PATH):
            os.remove(TOKENS_PATH)

        self.file_listbox.pack_forget()
        self.button_frame.pack_forget()
        self.logout_button.pack_forget()
        self.login_frame.pack(pady=10)

        self.upload_button.config(state=tk.DISABLED)
        self.download_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)

        self.creds = None
        self.drive_service = None


# Initialize app for standalone testing
if __name__ == "__main__":
    root = tk.Tk()
    app = StracGoogleDriveApp(root)
    root.mainloop()
