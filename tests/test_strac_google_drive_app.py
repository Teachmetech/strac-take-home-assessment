import unittest
import os
import time
import io
from unittest.mock import patch
from tkinter import Tk
from main import StracGoogleDriveApp


class TestStracGoogleDriveAppIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Tk()
        cls.root.withdraw()  # Hide the GUI during tests
        cls.app = StracGoogleDriveApp(cls.root)
        cls.app.authenticate()

    @classmethod
    def tearDownClass(cls):
        cls.cleanup_drive_files()
        cls.root.destroy()

    @classmethod
    def cleanup_drive_files(cls):
        # Use drive_service directly to delete files instead of relying on the listbox UI
        cls.app.populate_file_list()
        for name, file_id in cls.app.file_id_map.items():
            if "testfile_integration_" in name:
                try:
                    cls.app.drive_service.files().delete(fileId=file_id).execute()
                except Exception as e:
                    print(f"Failed to delete test file {name} from Google Drive: {e}")

    @patch("main.messagebox.showinfo")
    def test_upload_file(self, mock_showinfo):
        test_file_name = f"testfile_integration_{int(time.time())}.txt"
        with open(test_file_name, "w") as f:
            f.write("This is a test file for Google Drive integration testing.")

        with patch("main.filedialog.askopenfilename", return_value=test_file_name):
            self.app.upload_file()

        uploaded = False
        for _ in range(5):
            self.app.populate_file_list()
            if test_file_name in self.app.file_id_map:
                uploaded = True
                break
            time.sleep(2)

        if uploaded:
            self.app.drive_service.files().delete(
                fileId=self.app.file_id_map[test_file_name]
            ).execute()

        os.remove(test_file_name)
        self.assertTrue(uploaded, "File was not uploaded successfully.")

    @patch("main.messagebox.showinfo")
    def test_download_file_in_memory(self, mock_showinfo):
        test_file_name = f"testfile_integration_{int(time.time())}.txt"
        with open(test_file_name, "w") as f:
            f.write("This is a test file for Google Drive integration testing.")

        with patch("main.filedialog.askopenfilename", return_value=test_file_name):
            self.app.upload_file()

        uploaded = False
        for _ in range(5):
            self.app.populate_file_list()
            if test_file_name in self.app.file_id_map:
                uploaded = True
                break
            time.sleep(2)

        if uploaded:
            in_memory_file = io.BytesIO()
            self.app.download_file(in_memory_file=in_memory_file)

            in_memory_file.seek(0)
            downloaded_content = in_memory_file.read()
            expected_content = (
                b"This is a test file for Google Drive integration testing."
            )

            self.app.drive_service.files().delete(
                fileId=self.app.file_id_map[test_file_name]
            ).execute()
            os.remove(test_file_name)
            self.assertEqual(
                downloaded_content,
                expected_content,
                "File content mismatch on download.",
            )
        else:
            os.remove(test_file_name)
            self.fail("File was not uploaded for download test.")

    @patch("main.messagebox.showinfo")
    def test_delete_file(self, mock_showinfo):
        test_file_name = f"testfile_integration_{int(time.time())}.txt"
        with open(test_file_name, "w") as f:
            f.write("This is a test file for Google Drive integration testing.")

        with patch("main.filedialog.askopenfilename", return_value=test_file_name):
            self.app.upload_file()

        uploaded = False
        for _ in range(5):
            self.app.populate_file_list()
            if test_file_name in self.app.file_id_map:
                uploaded = True
                break
            time.sleep(2)

        if uploaded:
            self.app.drive_service.files().delete(
                fileId=self.app.file_id_map[test_file_name]
            ).execute()

            self.app.populate_file_list()
            deleted = test_file_name not in self.app.file_id_map
            os.remove(test_file_name)
            self.assertTrue(deleted, "File was not deleted successfully.")
        else:
            os.remove(test_file_name)
            self.fail("File was not uploaded for delete test.")


if __name__ == "__main__":
    unittest.main()
