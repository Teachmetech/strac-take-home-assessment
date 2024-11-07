import unittest
from tkinter import Tk
from main import StracGoogleDriveApp
from google.oauth2.credentials import Credentials
from unittest.mock import Mock, MagicMock, patch, mock_open


class TestStracGoogleDriveApp(unittest.TestCase):
    @patch("main.Credentials.from_authorized_user_file")
    def setUp(self, mock_credentials):
        self.mock_credentials = Mock(spec=Credentials)
        self.mock_credentials.token = "dummy-token"
        self.mock_credentials.refresh_token = "dummy-refresh-token"
        self.mock_credentials.token_uri = "https://oauth2.googleapis.com/token"
        self.mock_credentials.client_id = "dummy-client-id"
        self.mock_credentials.client_secret = "dummy-client-secret"
        self.mock_credentials.universe_domain = "googleapis.com"
        mock_credentials.return_value = self.mock_credentials

        self.root = Tk()
        self.root.withdraw()
        self.app = StracGoogleDriveApp(self.root)
        self.app.drive_service = MagicMock()

    def tearDown(self):
        self.root.destroy()

    @patch("main.messagebox.showinfo")
    @patch("main.filedialog.askopenfilename")
    @patch("main.MediaFileUpload")
    def test_upload_file(
        self, mock_mediafileupload, mock_askopenfilename, mock_showinfo
    ):
        mock_askopenfilename.return_value = "testfile.txt"
        mock_mediafileupload.return_value = MagicMock()
        self.app.drive_service.files().create().execute.return_value = {"id": "12345"}
        self.app.upload_file()
        mock_showinfo.assert_called_with("Success", "File uploaded with ID: 12345")

    @patch("main.messagebox.showinfo")
    @patch("main.filedialog.asksaveasfilename")
    @patch("main.MediaIoBaseDownload")
    @patch("io.FileIO", new_callable=mock_open)
    def test_download_file(
        self, mock_fileio, mock_mediaiodownload, mock_asksaveasfilename, mock_showinfo
    ):
        self.app.file_listbox.insert(
            0, "TestFile | Type: text/plain | Last Modified: 2024-01-01T12:00:00Z"
        )
        self.app.file_listbox.select_set(0)
        mock_asksaveasfilename.return_value = "/path/to/downloaded_file.txt"
        mock_downloader = MagicMock()
        mock_mediaiodownload.return_value = mock_downloader
        mock_downloader.next_chunk.side_effect = [(MagicMock(), True)]
        self.app.download_file()
        mock_showinfo.assert_called_with(
            "Success", "File downloaded as /path/to/downloaded_file.txt"
        )

    @patch("main.messagebox.showinfo")
    def test_delete_file(self, mock_showinfo):
        self.app.file_listbox.insert(
            0, "TestFile | Type: text/plain | Last Modified: 2024-01-01T12:00:00Z"
        )
        self.app.file_listbox.select_set(0)
        self.app.drive_service.files().delete().execute.return_value = None
        self.app.delete_file()
        mock_showinfo.assert_called_with("Success", "File deleted successfully.")

    @patch("main.messagebox.showerror")
    def test_populate_file_list_error(self, mock_showerror):
        self.app.drive_service.files().list().execute.side_effect = Exception(
            "API Error"
        )
        self.app.populate_file_list()
        mock_showerror.assert_called_with("Error", "An error occurred: API Error")

    @patch("main.os.path.exists", return_value=True)
    @patch("main.os.remove")
    def test_logout(self, mock_remove, mock_path_exists):
        self.app.logout()
        mock_remove.assert_called_once_with("tokens/token.json")


if __name__ == "__main__":
    unittest.main()
