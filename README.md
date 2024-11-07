
# Google Drive File Manager

This is a simple Google Drive File Manager application built with Python's `tkinter` GUI toolkit. It allows users to authenticate with Google, view their files on Google Drive, and manage them (upload, download, and delete files). This application was built for the Strac take home assessment.

## Features

- **Google OAuth Authentication**: Securely log in with a Google account.
- **File Listing**: View your Google Drive files with details (name, type, and last modified date).
- **File Upload**: Upload local files to Google Drive.
- **File Download**: Download selected files from Google Drive.
- **File Deletion**: Delete selected files from Google Drive.
- **Remember Login**: Optionally save login credentials to avoid repeated sign-ins.

## Prerequisites

- **Python** 3.8 or higher
- **Google Cloud Project** with OAuth 2.0 credentials for the Google Drive API

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Create a Virtual Environment** (recommended):
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Google API Credentials**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a project, enable the Google Drive API, and create OAuth 2.0 credentials.
   - Download the `client_secret.json` file and save it in the `secrets` directory within the project.

5. **Configure Constants**:
   - Set up `constants.py` with paths to your credentials:
     ```python
     SCOPES = ['https://www.googleapis.com/auth/drive']
     SECRETS_PATH = 'secrets/client_secret.json'
     TOKENS_PATH = 'tokens/token.json'
     ```

## Running the Application

To start the application, run:

```bash
python main.py
```

## Usage Guide

1. **Login**: Click "Login to Google" and follow the prompts to authorize access.
   - Check "Remember login" to save your credentials for future sessions.
   
2. **Upload a File**: Click "Upload File" to choose and upload a file from your system to Google Drive.

3. **Download a File**: Select a file from the list and click "Download File" to save it locally.

4. **Delete a File**: Select a file from the list and click "Delete File" to remove it from Google Drive.

5. **Logout**: Click "Logout" to sign out and remove saved credentials.

## Running Tests

This project includes both unit tests (with mock Google Drive interactions) and integration tests (which interact directly with Google Drive).

### Running All Tests

To run all tests:

```bash
python -m unittest discover -s tests
```

### Running Individual Test Files

To run a specific test file, specify the file name:

```bash
python -m unittest tests/test_strac_google_drive_app.py
python -m unittest tests/test_strac_google_drive_app_mock.py
```

### Test Overview

- **Unit Tests (`test_strac_google_drive_app_mock.py`)**: Use mocks to simulate API interactions, verifying application logic without actual API calls.
- **Integration Tests (`test_strac_google_drive_app.py`)**: Use real Google Drive API interactions to test uploading, downloading, and deleting files.

## Important Notes

- **Google Drive API Quotas**: Ensure you have sufficient API quota, especially when running integration tests.
- **OAuth Permissions**: The application requests full access to manage files on Google Drive. Only authorize if you are comfortable with this level of access.
- **Token Storage**: Credentials are stored in `tokens/token.json` when "Remember login" is checked. Ensure this file is secure and not shared.
