# Google Sheets Integration for Orders

## Setup Instructions

1. **Install Google API Libraries** (if not already installed):
   ```
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

2. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

3. **Enable Google Sheets API**:
   - In the Cloud Console, go to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it

4. **Create a Service Account**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Give it a name, e.g., "ddrp-orders"
   - Create and download the JSON key file

5. **Share the Google Sheet**:
   - Create a new Google Sheet
   - Note the Spreadsheet ID from the URL (the long string between /d/ and /edit)
   - Share the sheet with the service account email (found in the JSON file)

6. **Configure Environment**:
   - Place the downloaded JSON file as `backend/venv/service_account.json`
   - Update `backend/venv/.env`:
     ```
     GOOGLE_SHEETS_SPREADSHEET_ID=your_actual_spreadsheet_id
     GOOGLE_APPLICATION_CREDENTIALS=backend/venv/service_account.json
     ```

7. **Sheet Structure**:
   - Create a sheet named "Orders"
   - Headers in row 1: Serial No, Order ID, Customer Name, Product Name, Quantity, Date of Order

The integration will append new orders to the sheet automatically when placed.